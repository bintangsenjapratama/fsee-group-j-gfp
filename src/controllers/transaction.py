from flask import Blueprint, request
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models.transaction import Transaction
from datetime import datetime
from connectors.mysql_connectors import connection
from models.product import Product
from models.blocklist import BLOCKLIST
from flask_jwt_extended import jwt_required, get_jwt_identity


transaction_routes = Blueprint("transaction_routes", __name__)
Session = sessionmaker(connection)
s = Session()


@transaction_routes.route("/getallTransaction", methods=["GET"])
def get_all_product():
    try:
        with Session() as s:
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
            return {"products": transactions}, 200
    except Exception as e:
        print(e)
        s.rollback()
        return {"message": "Unexpected Error"}, 500


@transaction_routes.route("/register/transactions", methods=["POST"])
def register_transaction():
    s.begin()
    try:
        from_user_id = int(request.form["from_user_id"])
        to_user_id = int(request.form["to_user_id"])
        product_id = int(request.form["product_id"])
        stock = int(request.form["stock"])
        product_quantity = int(request.form["product_quantity"])
        price = float(request.form["price"])
        total_price = float(request.form["total_price"])
        status = request.form["status"]

        if stock < product_quantity:
            return {"message": "Insufficient Stock"}, 400

        updated_stock = stock - product_quantity

        expected_total_price = price * product_quantity
        if total_price != expected_total_price:
            return {"message": "Total price mismatch"}, 400

        new_transaction = Transaction(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            product_id=product_id,
            stock=updated_stock,
            product_quantity=product_quantity,
            price=price,
            total_price=total_price,
            status=status,
        )

        s.add(new_transaction)

        s.commit()

    except Exception as e:
        s.rollback()

        print(f"Error occurred: {e}")
        return {"message": "Failed to Register New Transaction"}, 500

    return {"message": "Successfully Created New Transaction"}, 200

