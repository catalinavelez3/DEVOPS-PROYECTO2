from datetime import datetime
from .extensions import db

class Blacklist(db.Model):
    __tablename__ = "blacklists"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    app_uuid = db.Column(db.String(36), nullable=False)
    blocked_reason = db.Column(db.String(255), nullable=True)
    client_ip = db.Column(db.String(45), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Blacklist {self.email}>"