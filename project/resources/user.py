from flask import Flask, request,Response
from flask_restful import Api, Resource, fields, marshal, marshal_with
from flask_api import FlaskAPI, status
from resources.token import generate_confirmation_token, confirm_token

from models.product import User,UserSchema,db
from resources.email import send_email
from flask import redirect, render_template, url_for
from passlib.hash import pbkdf2_sha256
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import csv
import sqlite3
import xlrd
from celery import Celery
app = Flask(__name__)
# set up celery client
app.config.from_object("config")
app.secret_key = app.config['SECRET_KEY']

# set up celery client
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

post_schema = UserSchema()
posts_schema = UserSchema(many=True)
PASSWORD_CHANGED = "Password changed successfully."
resource_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'username': fields.String,
}

class UserView(Resource):
    """UserView API."""

    def get(self, user_id):
        """Get a user."""
        user = User.query.get(user_id)
        if user:
            return marshal(user, resource_fields),status.HTTP_200_OK
        return 'User not found', 404

    def put(self,user_id):
        """Update a user."""
        data = request.form
        username = data['username']
        email = data['email']
        user = User.query.get(user_id)
        user_email = User.query.filter_by(email=email).first()
        if user_email:
            return 'Email already registered',409
        if user:
            user = user
            user.username = username
            db.session.commit()
            return marshal(user, resource_fields), 201
        return 'User not found', 404


class UserViewList(Resource):
    """UserViewList API."""

    def get(self):
        posts = User.query.all()
        return posts_schema.dump(posts)

    def post(self):
        """Register user."""
        data = request.form
        print("data",data)
        username = data['username']
        email = data['email']
        # password = data['password']
        # hashed_password = generate_password_hash(password, method='sha256')
        email1 = User.query.filter_by(email=email).first()
        user = User.query.filter_by(username=username).first()
        if email1:
            return {"error":'Email already registered'},409
        if user:
            return {"error": "Username already registered"},409
        new_user = User(
            username = username,
            email = email,
            password = "",
            active = False
            )
        db.session.add(new_user)
        db.session.commit()
        token = generate_confirmation_token(new_user.email)
        html = render_template('confirmation.html', confirm_url='http://127.0.0.1:5000/confirmation/'+token)
        subject = "Please confirm your email"
        send_email.delay(new_user.email, subject, html)
        return {'message':'Thanks for registering!  Please check your email to confirm your email address.'},status.HTTP_201_CREATED


# class ConfirmationView(Resource):
#     """ConfirmationView API."""
#     def get(self, token):
#         """Check confirmation token."""
#         email = confirm_token(token)
#         user = User.query.filter_by(email=email).first()
#         if user:
#             if user.active:
#                 return 'Account is already confirmed.', 200
#             user.active=True
#             db.session.commit()
#             return 'Account confirmation was successful.', 200
#         return 'Invalid confirmation token.', 406


import random

class ConfirmationView(Resource):
    """ConfirmationView API."""
    def get(self, token):
        """Check confirmation token."""
        characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_'
        temporarypassword = ''
        for i in range(0, 15):
            temporarypassword += random.choice(characters)
        print(temporarypassword)
        password = temporarypassword
        print("password",password)
        hashed_password = generate_password_hash(password, method='sha256')
        email = confirm_token(token)
        user = User.query.filter_by(email=email).first()
        if user:
            if user.active:
                return 'Account is already confirmed.', 200
            user.password=hashed_password
            user.active=True
            db.session.commit()
            html = render_template('confirmation.html', confirm_url=password)
            print("html",html)
            subject = "Please confirm your email"
            send_email.delay(user.email, subject, html)
            return {'message':'Send password to user.'},status.HTTP_201_CREATED
            # return 'Account confirmation was successful.', 200
        return 'Invalid confirmation token.', 406

class LoginApi(Resource):
    """Login view API."""
    def post(self):
        data = request.form
        email = data['email']
        password = data['password']
        user = User.query.filter_by(email=email).first()
        if not user:
            return {'error': 'Email or password invalid'}, 401
        authorized = user.check_password(password)
        if not authorized:
            return {'error': 'Email or password invalid'}, 401
        return {'message':'Login successfully.'},status.HTTP_200_OK



class ChangePassword(Resource):

    def post(cls):
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        user_data = request.form
        password = user_data['password']
        new_password = user_data['new_password']
        user = current_user.find_by_username(username=current_user.username)
        print("user==",user)
        if user is None or not user.check_password(password=password):
            return {"message": INCORRECT_PASSWORD}, 422

        user.set_password(password=new_password)
        user.save_to_db()
        expires = datetime.timedelta(days=120)

        return {"message": PASSWORD_CHANGED}, 200

# Create your Celery task
@celery.task
def save_operation(create_sql,insert_sql,values):
    conn = sqlite3.connect('xlsx_database.db')
    c = conn.cursor()
    c.execute(create_sql)
    c.executemany(insert_sql, values)
    conn.commit()
    return 'created new record'


class CSVTable(Resource):
    """Create xlsx view API."""
    def post(self):
        data = request.form
        file_name = request.files['file_name']
        strFileName = file_name.filename
        txt= strFileName[:-5]
        new_cdf = pd.read_excel(file_name)
        column_name = list(new_cdf.columns)
        print("==",column_name)
        table_name = txt
        create_sql = 'CREATE TABLE IF NOT EXISTS  ' + table_name + '(id_product_item INTEGER PRIMARY KEY,' \
            + ','.join(column_name) + ')'
        # conn = sqlite3.connect('xlsx_database.db')
        # c = conn.cursor()
        # c.execute(create_sql)
        insert_sql = 'INSERT INTO ' + table_name + ' (' + ','.join(column_name) \
            + ') VALUES (' + ','.join(['?'] * len(column_name)) + ')'
        df = pd.DataFrame(new_cdf, columns=column_name)
        values = df.values.tolist()
        print("values",values)
        # c.executemany(insert_sql, values)
        # conn.commit()
        print("==",insert_sql)
        save_operation.delay(create_sql,insert_sql,values)
        # save_operation.apply_async(args=[create_sql,insert_sql,values], countdown=60)

        return {"message": "Created successfully.","data":column_name}
