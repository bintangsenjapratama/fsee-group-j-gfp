from flask import Flask
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


from connectors.mysql_connectors import connection
from controllers.users import users_routes
from models.user import User


load_dotenv()

app = Flask(__name__)

Session = sessionmaker(connection)

app.register_blueprint(users_routes)


@app.route("/")
def index():
    return "Welcome to Flask!"
