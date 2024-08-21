from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from models.transaction import Transaction
from connectors.mysql_connectors import connection
from models.product import Product
from flask_jwt_extended import jwt_required, get_jwt
from controllers.users import s
from flasgger import swag_from


transaction_routes = Blueprint("transaction_routes", __name__)


@transaction_routes.route("/register/transactions", methods=["POST"])
@swag_from("docs/transaction/register_transaction.yml")
def register_transaction():
    try:
        from_user_id = int(request.form["from_user_id"])
        to_user_id = int(request.form["to_user_id"])
        product_id = int(request.form["product_id"])
        product_quantity = int(request.form["product_quantity"])
        total_price = float(request.form["total_price"])
        status = request.form["status"]

        product = (
            s.execute(select(Product).where(Product.id == product_id)).scalars().first()
        )
        if not product:
            s.rollback()
            return {"message": "Product not found"}, 404

        if product.stock < product_quantity:
            s.rollback()
            return {"message": "Insufficient Stock"}, 400

        expected_total_price = product.price * product_quantity
        if total_price != expected_total_price:
            s.rollback()
            return {"message": "Total price mismatch"}, 400

        transaction = Transaction(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            product_id=product_id,
            product_quantity=product_quantity,
            total_price=total_price,
            status=status,
        )
        s.add(transaction)

        # new_stock = product.stock - product_quantity
        product.stock = product.stock - product_quantity
        # s.execute(
        #     update(Product).where(Product.id == product_id).values(stock=product.stock)
        # )

        s.commit()

    except Exception as e:
        s.rollback()
        print(f"Error occurred: {e}")
        return {"message": "Failed to Register New Transaction"}, 500

    return {"message": "Successfully Created New Transaction"}, 200


@transaction_routes.route("/getallTransaction", methods=["GET"])
@swag_from("docs/transaction/get_all_transaction.yml")
def get_all_transaction():
    try:
        transaction_querry = select(Transaction)
        search_keyword = request.args.get("query")
        if search_keyword:
            transaction_querry = transaction_querry.where(
                Transaction.status.like(f"%{search_keyword}%")
            )

        result = s.execute(transaction_querry)
        transactions = []

        for row in result.scalars():
            transactions.append(
                    {
                        "id": row.id,
                        "user_id": row.from_user_id,
                        "product_id": row.product_id,
                        "product_quantity": row.product_quantity,
                        "total_price": row.total_price,
                        "status": row.status,
                    }
                )
        return {"transactions": transactions}, 200
    except Exception as e:
        print(e)
        s.rollback()
        return {"message": "Unexpected Error"}, 500

@transaction_routes.route("/getCart", methods=["GET"])
@jwt_required()
def get_cart():
    user = get_jwt()
    try:
        # get user's cart items
        cart_items = s.query(Transaction).filter_by(to_user_id=user.get("id"), status="cart").all()
        
        # collect product ids
        product_ids = [item.product_id for item in cart_items]

        # Query all products in one go using the list of product IDs
        products = s.query(Product).filter(Product.id.in_(product_ids)).all()
        product_map = {product.id: product for product in products}

        # Calculate order summary
        subtotal = sum(item.product_quantity * float(product_map[item.product_id].price) for item in cart_items if item.product_id in product_map)
        total_discount = sum(float(product_map[item.product_id].discount) * float(product_map[item.product_id].price) for item in cart_items if item.product_id in product_map)
        delivery_cost = subtotal * 0.1
        total = subtotal - total_discount + delivery_cost
        
        items_data = [{
            'id': item.id,
            'seller_id': item.from_user_id,
            'buyer_id': item.to_user_id,
            'product_id': item.product_id,
            'quantity': item.product_quantity,
            'product_name': product_map[item.product_id].product_name if item.product_id in product_map else None,
            'price': float(product_map[item.product_id].price) if item.product_id in product_map else None,
            'image_url': product_map[item.product_id].image_url if item.product_id in product_map else None,
            'stock': product_map[item.product_id].stock if item.product_id in product_map else None,
            'discount': float(product_map[item.product_id].discount) if item.product_id in product_map else None,
            'description': product_map[item.product_id].description if item.product_id in product_map else None,
            'total_price': item.total_price
        } for item in cart_items]

        return jsonify({
            'items': items_data,
            'summary': {
                'subtotal': round(subtotal, 2),
                'total_discount': round(total_discount, 2),
                'delivery_cost': round(delivery_cost, 2),
                'total': round(total, 2),
            }
        }), 200
    
    except Exception as e:
        print(e)
        s.rollback()
        return {"message": "Unexpected Error, {e}"}, 500

@transaction_routes.route("/updateCartItemQuantity", methods=["PATCH"])
@jwt_required()
def update_cart_item_quantity():
    user = get_jwt()
    try:
        data = request.get_json()
        cart_item_id = data.get("itemId")
        new_quantity = data.get("quantity")

        # Find the cart item by id
        cart_item = s.query(Transaction).filter_by(id=cart_item_id, to_user_id=user.get("id"), status="cart").first()
        if not cart_item:
            return jsonify({"message": "Cart item not found"}), 404
        
        # Find product
        product = s.query(Product).filter_by(id=cart_item.product_id).first()
        if not product:
            return jsonify({"message": "Product not found"}), 404
        
        # Update stock
        product.stock = product.stock - (new_quantity - cart_item.product_quantity)

        if product.stock >= 0:
            # Update the quantity
            cart_item.product_quantity = new_quantity
            
            # Calculate new total price
            discount_amount = (product.discount or 0) * product.price * new_quantity / 100
            cart_item.total_price = (product.price * new_quantity) - discount_amount

            s.commit()

            return jsonify({"message": "Quantity updated successfully"}), 200
        else:
            return jsonify({"message": "Insufficient Stock"}), 400
    except Exception as e:
        print(e)
        s.rollback()
        return jsonify({"message": "Unexpected Error"}), 500

@transaction_routes.route("/deleteCartItem", methods=["DELETE"])
@jwt_required()
def delete_cart_item():
    user = get_jwt()
    try:
        # Get the cart item by id
        data = request.get_json()
        cart_item_id = data.get("id")

        # Find the cart item by its id
        cart_item = s.query(Transaction).filter_by(id=cart_item_id, to_user_id=user.get("id"), status="cart").first()
        if not cart_item:
            return jsonify({"message": "Cart item not found"}), 404
        
        # Find product
        product = s.query(Product).filter_by(id=cart_item.product_id).first()
        if not product:
            return jsonify({"message": "Product not found"}), 404
        
        # Return product stock
        product.stock = product.stock + cart_item.product_quantity

        # Remove cart item from transaction table
        s.delete(cart_item)
        s.commit()

        return jsonify({"message": "Cart item deleted successfully"}), 200
    except Exception as e:
        print(e)
        s.rollback()
        return jsonify({"message": "Unexpected Error"}), 500
