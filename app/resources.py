from flask import request
from flask_restful import Resource
from .auth import require_bearer_token
from .extensions import db
from .models import Blacklist
from .schemas import BlacklistCreateSchema

create_schema = BlacklistCreateSchema()

class HealthResource(Resource):
    def get(self):
        return {"status": "ok"}, 200


class BlacklistResource(Resource):
    method_decorators = [require_bearer_token]

    def post(self):
        json_data = request.get_json()

        if not json_data:
            return {"message": "Request body is required"}, 400

        errors = create_schema.validate(json_data)
        if errors:
            return {"message": "Validation error", "errors": errors}, 400

        email = json_data["email"].lower().strip()
        app_uuid = str(json_data["app_uuid"])
        blocked_reason = json_data.get("blocked_reason")

        existing = Blacklist.query.filter_by(email=email).first()
        if existing:
            return {
                "message": "Email already exists in blacklist",
                "email": email
            }, 409

        item = Blacklist(
            email=email,
            app_uuid=app_uuid,
            blocked_reason=blocked_reason,
            client_ip=request.remote_addr or "unknown"
        )

        db.session.add(item)
        db.session.commit()

        return {
            "message": "Email added to blacklist successfully",
            "email": item.email
        }, 201


class BlacklistCheckResource(Resource):
    method_decorators = [require_bearer_token]

    def get(self, email):
        email = email.lower().strip()
        item = Blacklist.query.filter_by(email=email).first()

        if item:
            return {
                "is_blacklisted": True,
                "email": item.email,
                "blocked_reason": item.blocked_reason
            }, 200

        return {
            "is_blacklisted": False,
            "email": email,
            "blocked_reason": None
        }, 200