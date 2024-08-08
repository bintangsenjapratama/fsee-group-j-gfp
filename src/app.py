from flask import Flask
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import sys
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from flask_cors import CORS

from connectors.mysql_connectors import connection
from controllers.users import users_routes
from controllers.products import products_routes
from controllers.transaction import transaction_routes
from models.user import User

from models.blocklist import BLOCKLIST
from models.user import User

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
jwt = JWTManager(app)

Session = sessionmaker(connection)
swagger = Swagger(app)

app.register_blueprint(users_routes)
app.register_blueprint(products_routes)
app.register_blueprint(transaction_routes)


cors = CORS(
    app,
    resources={r"/*": {"origins": ["http://localhost:3000"]}},
)


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return {"description": "The token has been revoked.", "error": "token_revoked"}, 401


@jwt.additional_claims_loader
def make_additional_claims(role):
    if role == "seller":
        return {"is_seller": True}
    return {"is_seller": False}


@app.route("/")
def index():
    return "Welcome to Flask!"
