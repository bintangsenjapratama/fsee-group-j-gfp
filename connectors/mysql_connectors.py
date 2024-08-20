from sqlalchemy import create_engine
import os

# username = os.getenv("MYSQLUSER")
# password = os.getenv("MYSQLPASSWORD")
# host = os.getenv("MYSQLHOST")
# database = os.getenv("MYSQLDATABASE")
# port = os.getenv("MYSQLPORT")

# print("Connecting to MySQL Database")
# engine = create_engine(
#     f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}"
# )
# print(engine)


username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
database = os.getenv("DB_DATABASE")

print("Connecting to MySQL Database")
engine = create_engine(
    f"mysql+mysqlconnector://{username}:{password}@{host}/{database}"
)
print(engine)

connection = engine.connect()
print("Success Connecting to MySQL User Database")
print(connection)
