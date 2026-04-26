from marshmallow import fields, validate
from .extensions import ma

class BlacklistCreateSchema(ma.Schema):
    email = fields.Email(required=True)
    app_uuid = fields.UUID(required=True)
    blocked_reason = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=255)
    )

class BlacklistResponseSchema(ma.Schema):
    email = fields.Email()
    app_uuid = fields.String()
    blocked_reason = fields.String(allow_none=True)
    client_ip = fields.String()
    created_at = fields.DateTime()