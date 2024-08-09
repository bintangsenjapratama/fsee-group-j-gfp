from flask import Blueprint, request
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models.product import Product
from datetime import datetime
from connectors.mysql_connectors import connection
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flasgger import swag_from

products_routes = Blueprint("products_routes", __name__)
Session = sessionmaker(connection)
s = Session()


@products_routes.route("/getallproduct", methods=["GET"])
@swag_from("docs/products/get_all_product.yml")
def get_all_product():
    try:
        product_query = select(Product)
        search_keyword = request.args.get("query")
        if search_keyword:
            product_query = product_query.where(
                Product.product_name.like(f"%{search_keyword}%")
            )

        result = s.execute(product_query)
        products = []

        for row in result.scalars():
            products.append(
                {
                    "id": row.id,
                    "user_id": row.user_id,
                    "product_name": row.product_name,
                    "price": row.price,
                    "description": row.description,
                    "stock": row.stock,
                    "category": row.category,
                    "type": row.type,
                    "discount": row.discount,
                }
                )
        return {"products": products}, 200
    except Exception as e:
        print(e)
        s.rollback()
        return {"message": "Unexpected Error"}, 500


@products_routes.route("/registerProduct", methods=["POST"])
@jwt_required()
@swag_from("docs/products/register_product.yml")
def register_product():
    claims = get_jwt()
    if claims.get("role") == "seller":
        try:
            product_name = request.form["product_name"]
            price = float(request.form["price"])
            description = request.form["description"]
            stock = int(request.form["stock"])
            category = request.form["category"]
            product_type = request.form["type"]
            discount = (
                float(request.form["discount"]) if "discount" in request.form else 0.0
            )
            user_id = int(claims.get("id"))

            if discount > 0:
                discounted_price = price * (1 - discount / 100)
            else:
                discounted_price = price

                new_product = Product(
                    product_name=product_name,
                    price=discounted_price,
                    description=description,
                    stock=stock,
                    category=category,
                    type=product_type,
                    discount=discount,
                    user_id=user_id,
                )
            s.add(new_product)
            s.commit()
            return {"message": "Success to Create New Product"}, 200
        except Exception as e:
            print(e)
            s.rollback()
            return {"message": "Fail to Register New Product"}, 500
    else:
        return {"message": "Only Seller can register add product"}, 403


@products_routes.route("/products/me", methods=["GET"])
@jwt_required()
@swag_from("docs/products/get_accounts_by_user_id.yml")
def get_accounts_by_user_id():
    current_user_id = get_jwt_identity()
    try:
        products = s.query(Product).filter(Product.user_id == current_user_id).all()

        if not products:
            return {"message": "No product found for this user"}, 404

        products_list = []
        for product in products:
            products_details = {
                "id": product.id,
                "user_id": product.user_id,
                "product_name": product.product_name,
                "price": product.price,
                "description": product.description,
                "stock": product.stock,
                "category": product.category,
                "type": product.type,
                "discount": product.discount,
            }
            products_list.append(products_details)
        return {"accounts": products_list}, 200

    except Exception as e:
        print(e)
        s.rollback()
        return {"message": "Unexpected Error"}, 500


@products_routes.route("/product/<id>", methods=["PUT"])
@swag_from("docs/products/product_update.yml")
def product_update(id):
    s.begin()
    try:
        product = s.query(Product).filter(Product.id == id).first()

        if not product:
            return {"message": "Product not found"}, 404

        product_name = request.form.get("product_name", product.product_name)
        price = float(request.form.get("price", product.price))
        description = request.form.get("description", product.description)
        stock = int(request.form.get("stock", product.stock))
        category = request.form.get("category", product.category)
        type = request.form.get("type", product.type)
        discount = (
            float(request.form.get("discount", product.discount))
            if "discount" in request.form
            else product.discount
        )
        user_id = int(request.form.get("user_id", product.user_id))

        if discount > 0:
            price = price * (1 - discount / 100)

        product.product_name = product_name
        product.price = price
        product.description = description
        product.stock = stock
        product.category = category
        product.type = type
        product.discount = discount
        product.user_id = user_id
        product.update_at = datetime.now()

        s.commit()
    except Exception as e:
        print(e)
        s.rollback()
        return {"message": "Failed to update"}, 500
    return {"message": "Successfully updated product data"}, 200
