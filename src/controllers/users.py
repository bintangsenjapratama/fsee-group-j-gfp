from flask import Blueprint, request
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from connectors.mysql_connectors import connection
from models.user import User


users_routes = Blueprint("users_routes", __name__)
Session = sessionmaker(connection)
s = Session()


@users_routes.route("/users/register", methods=["POST"])
def register_usersData():
    s.begin()
    try:
        NewUser = User(
            username=request.form["username"],
            email=request.form["email"],
            role=request.form["role"],
        )
        NewUser.set_password(request.form["password"])
        s.add(NewUser)
        s.commit()
    except Exception as e:
        print(e)
        s.rollback()
        return {"message": "Fail to Register New User"}, 500
    return {"message": "Success to Create New User"}, 200
