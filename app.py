from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from flask_cors import CORS

from connectors.mysql_connectors import connection
from controllers.users import users_routes
from controllers.products import products_routes
from controllers.transaction import transaction_routes


from models.blocklist import BLOCKLIST

import cloudinary
import cloudinary.uploader
import cloudinary.api



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
    resources={r"/*": {"origins": ["http://localhost:3000", "https://front-end-git-main-lightkazutos-projects.vercel.app/"]}},
)

cloudinary.config(
  cloud_name = 'defjz8q5v',
  api_key = '791993253684266',
  api_secret = 'faM4kmRGhnK5pvEYImpnWZqhbbU'
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


# Routes
@app.route("/")
def index():
    return "Welcome to Flask!"

@app.route('/upload', methods=['POST'])
def upload_image():
    file_to_upload = request.files.get('file')

    if not file_to_upload:
        return jsonify({"error": "No file provided"}), 400

    try:
        upload_result = cloudinary.uploader.upload(file_to_upload)
        return jsonify(upload_result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500