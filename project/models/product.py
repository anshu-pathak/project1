
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class Product(db.Model):
    """ Protduc model """
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20),unique=True)
    description = db.Column(db.String(100),nullable=False)
    brand = db.Column(db.String(20),nullable=False)
    price = db.Column(db.Float,nullable=True)

    def __str__(self):
        return self.name


class ProductSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Product
        sqla_session = db.session
    id = fields.Number(dump_only=True)
    name = fields.String(required=True,unique=True)
    description = fields.String(required=True)
    brand = fields.String(required=True)
    # price = fields.Number(required=True)

# class ProductSchema(ModelSchema):
#     class Meta(ModelSchema.Meta):
#         fields = ("id", "name", "description","brand","price")

class User(UserMixin, db.Model):
    """ User model """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def __repr__(self):
        return '<User %r>' %(self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class UserSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        fields = ("id", "username", "email","password","active")
