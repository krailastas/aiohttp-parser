from marshmallow import Schema, fields, validate


class TaskSchema(Schema):
    company_name = fields.Str(
        validate=validate.Length(max=64, min=2), required=True
    )
    location = fields.Str(
        validate=validate.Length(max=64, min=2), required=True, allow_none=True
    )
