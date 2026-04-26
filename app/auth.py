from functools import wraps
from flask import request, jsonify, current_app

def require_bearer_token(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        expected = f"Bearer {current_app.config['STATIC_BEARER_TOKEN']}"

        if auth_header != expected:
            return jsonify({"message": "Unauthorized"}), 401

        return fn(*args, **kwargs)
    return wrapper