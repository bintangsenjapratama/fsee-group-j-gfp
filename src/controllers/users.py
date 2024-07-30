from flask import Blueprint, request
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from flask_jwt_extended import create_access_token

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


@users_routes.route("/users/login", methods=["POST"])
def login_userData():
    try:
        email = request.form["email"]
        user = s.query(User).filter(User.email == email).first()

        if user == None:
            return {"message": "User not found"}, 403

        if not user.check_password(request.form["password"]):
            return {"message": "Invalid password"}, 403

        acces_token = create_access_token(
            identity=user.id, additional_claims={"email": user.email, "id": user.id}
        )
        s.flush()
        return {"access_tokern": acces_token, "message": "Success to Login user"}, 200
    except Exception as e:
        print(e)
        s.rollback()
        return {"message": "Failed to Login User"}, 500
