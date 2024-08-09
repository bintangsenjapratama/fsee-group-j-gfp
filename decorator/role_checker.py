from functools import wraps
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from flask import jsonify


def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            roles = claims.get("seller", [])
            if required_role not in roles:
                return (
                    jsonify(msg="Access forbidden: You don't have the required role"),
                    403,
                    print(claims),
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator
