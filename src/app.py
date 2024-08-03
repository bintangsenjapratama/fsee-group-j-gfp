from flask import Flask
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager


from connectors.mysql_connectors import connection
from controllers.users import users_routes
from controllers.products import products_routes
from controllers.transaction import transaction_routes

from models.blocklist import BLOCKLIST
from models.user import User


load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
jwt = JWTManager(app)

Session = sessionmaker(connection)

app.register_blueprint(users_routes)
app.register_blueprint(products_routes)
app.register_blueprint(transaction_routes)


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return {"description": "The token has been revoked.", "error": "token_revoked"}, 401


@app.route("/")
def index():
    return "Welcome to Flask!"
