from flask import Blueprint, request
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from sqlalchemy import select

from connectors.mysql_connectors import connection
from models.blocklist import BLOCKLIST
from models.user import User

from flasgger import swag_from


users_routes = Blueprint("users_routes", __name__)
Session = sessionmaker(connection)
s = Session()


@users_routes.route("/getalluser", methods=["GET"])
@swag_from("docs/users/get_alluser.yml")
def get_allUser():
    try:
        with Session() as s:
            user_query = select(User)

            search_keyword = request.args.get("query")
            if search_keyword is not None:
                user_query = user_query.where(User.username.like(f"%{search_keyword}%"))

            result = s.execute(user_query)
            users = []

            for row in result.scalars():
                users.append(
                    {
                        "id": row.id,
                        "email": row.email,
                        "username": row.username,
                        "role": row.role,
                    }
                )
            return (
                {"users": users},
                200,
            )
    except Exception as e:
        print(e)
        return {"message": "Unexpected Error"}, 500


@users_routes.route("/register", methods=["POST"])
@swag_from("docs/users/register.yml")
def register_usersData():
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


@users_routes.route("/login", methods=["POST"])
@swag_from("docs/users/login.yml")
def login_userData():
    try:
        email = request.form["email"]
        user = s.query(User).filter(User.email == email).first()

        if user == None:
            return {"message": "User not found"}, 403

        if not user.check_password(request.form["password"]):
            return {"message": "Invalid password"}, 403

        acces_token = create_access_token(
            identity=user.id,
            additional_claims={"email": user.email, "id": user.id, "role": user.role},
        )
        s.flush()
        return {
            "email": user.email,
            "id": user.id,
            "role": user.role,
            "access_token": acces_token,
            "message": "Success to Login user",
        }, 200
    except Exception as e:
        print(e)
        s.rollback()
        return {"message": "Failed to Login User"}, 500


@users_routes.route("/logout", methods=["POST"])
@jwt_required()
@swag_from("docs/users/logout.yml")
def logout():
    try:
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "User successfully logged out"}, 200
    except Exception as e:
        print(e)
        return {"message": "Failed to logout"}, 500


@users_routes.route("/users/me", methods=["PUT"])
@jwt_required()
@swag_from("docs/users/update_current_user.yml")
def update_current_user():
    current_user_id = get_jwt_identity()
    print(current_user_id)
    try:
        user = s.query(User).filter(User.id == current_user_id).first()
        if not user:
            return {"message": "User not found"}, 404

        if "password" in request.form:
            user.set_password(request.form["password"])
        user.update_at = datetime.now()

        s.add(user)
        s.commit()
        return {"message": "User updated successfully"}, 200

    except Exception as e:
        print(e)
        s.rollback()
        return {"message": "Failed to update user"}, 500


@users_routes.route("/whoami", methods=["GET"])
@jwt_required()
@swag_from("docs/users/get_current_user.yml")
def get_current_user():
    claims = get_jwt()
    return {"claims": claims}
