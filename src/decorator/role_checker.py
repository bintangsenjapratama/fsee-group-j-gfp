from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity


def role_required(role):
    def decorator(func):
        @wraps(func)
        @jwt_required()  # tambahkan ini
        def wrapper(*args, **kwargs):
            jwt_identity = get_jwt_identity()
            if isinstance(jwt_identity, dict):
                if jwt_identity.get("role") == "admin" and role == "admin":
                    return func(*args, **kwargs)
                elif jwt_identity.get("role") == "user" and role == "user":
                    return func(*args, **kwargs)
            else:
                return {"message": "Unauthorized"}, 403

        return wrapper

    return decorator
