import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from .extensions import db, ma, api, jwt
from .models import Blacklist
from .schemas import BlacklistCreateSchema
from .auth import require_bearer_token

load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["STATIC_BEARER_TOKEN"] = os.getenv("STATIC_BEARER_TOKEN", "token-super-secreto")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")

    # Si vienen configuraciones de prueba, sobrescriben las normales
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    ma.init_app(app)
    api.init_app(app)
    jwt.init_app(app)

    create_schema = BlacklistCreateSchema()

    @app.get("/healthz")
    def health():
        return {"status": "ok"}, 200

    @app.post("/blacklists")
    @require_bearer_token
    def create_blacklist():
        json_data = request.get_json()

        if not json_data:
            return jsonify({"message": "Request body is required"}), 400

        errors = create_schema.validate(json_data)
        if errors:
            return jsonify({"message": "Validation error", "errors": errors}), 400

        email = json_data["email"].lower().strip()
        app_uuid = str(json_data["app_uuid"])
        blocked_reason = json_data.get("blocked_reason")

        existing = Blacklist.query.filter_by(email=email).first()
        if existing:
            return jsonify({
                "message": "Email already exists in blacklist",
                "email": email
            }), 409

        item = Blacklist(
            email=email,
            app_uuid=app_uuid,
            blocked_reason=blocked_reason,
            client_ip=request.remote_addr or "unknown"
        )

        db.session.add(item)
        db.session.commit()

        return jsonify({
            "message": "Email added to blacklist successfully",
            "email": item.email
        }), 201


    @app.get("/blacklists/<string:email>")
    @require_bearer_token
    def check_blacklist(email):
        email = email.lower().strip()
        item = Blacklist.query.filter_by(email=email).first()

        if item:
            return jsonify({
                "is_blacklisted": True,
                "email": item.email,
                "blocked_reason": item.blocked_reason
            }), 200

        return jsonify({
            "is_blacklisted": False,
            "email": email,
            "blocked_reason": None
        }), 200

    with app.app_context():
        db.create_all()

    return app