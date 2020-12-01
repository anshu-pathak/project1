from flask import Flask,request,url_for, flash,Response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
from resources.product import PostListResource,PostResource,CSVData
from resources.user import UserView,UserViewList,ConfirmationView,LoginApi,CSVTable
from models.product import db
from flask_mail import Mail,Message
from celery import Celery

app = Flask(__name__,template_folder='templates')
app.config.from_object("config")
app.secret_key = app.config['SECRET_KEY']
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product.db'
app.config['SECRET_KEY'] = 'f495b66803a6512d'
# set up celery client
client = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
client.conf.update(app.config)

api = Api(app)
db.init_app(app)

# Product api views
api.add_resource(PostListResource, '/products')
api.add_resource(PostResource, '/products/<int:post_id>')
api.add_resource(CSVData, '/csv/data')

# Signup and login api views
api.add_resource(UserViewList, '/api/users')
api.add_resource(UserView, '/api/users/<user_id>')
api.add_resource(ConfirmationView, '/confirmation/<token>')
api.add_resource(LoginApi, '/api/login')
api.add_resource(CSVTable, '/api/upload')


if __name__ == '__main__':
    app.debug = True
    app.run(debug=True)
