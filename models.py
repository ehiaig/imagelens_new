from datetime import datetime
from config import db, ma
from marshmallow import fields, ValidationError
import pickle

class Vector(db.Model):
    __tablename__ = "vector"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    vector_id = db.Column(db.Integer, index=True, unique=True)
    encoding = db.Column(db.JSON)
    image_byte = db.Column(db.LargeBinary)
    image_url = db.Column(db.String(1000))
    misc = db.Column(db.JSON)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class ByteField(fields.Field):
    
    def _deserialize(self, value, *args, **kwargs):
        if value is None:
            return None
        if isinstance(value, bytes):
            return value

    def _serialize(self, value, *args, **kwargs):
        return str(value)

class VectorSchema(ma.Schema):

    class Meta:
        model = Vector
        sqla_session = db.session

    id = fields.Int(dump_only=True)
    vector_id = fields.Str(dump_only=True)
    encoding = fields.Str(dump_only=True)
    image_byte = ByteField(dump_only=True)
    image_url = fields.Str(dump_only=True)
    misc = fields.Str(dump_only=True)
    date_created = fields.DateTime(dump_only=True)
    date_updated = fields.DateTime(dump_only=True)


# Custom validator
def must_not_be_blank(data):
    if not data:
        raise ValidationError("Data not provided.")


