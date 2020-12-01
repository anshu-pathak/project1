from flask import Flask, request,Response
from flask_restful import Api, Resource
from models.product import Product,ProductSchema,db
from flask_api import FlaskAPI, status
import pandas as pd
import csv

post_schema = ProductSchema()
posts_schema = ProductSchema(many=True)


class PostListResource(Resource):

    def get(self):
        posts = Product.query.all()
        return posts_schema.dump(posts)

    def post(self):
        new_cdf =  pd.read_csv('product.csv')
        column_name = list(new_cdf.columns)
        df = pd.DataFrame(columns = column_name)
        data = request.form
        name = data['name']
        description = data['description']
        brand = data['brand']
        price = data['price']
        product_name = Product.query.filter_by(name=name).first()
        if not product_name:
            if not price:
                price  = 0
            new_product = Product(
                name = name,
                brand = brand,
                description = description,
                price = price
                )
            db.session.add(new_product)
            db.session.commit()
            result = post_schema.dump(new_product),status.HTTP_201_CREATED
        else:
            response = {
                'status': False,
                'message': "Name already exists."
            }
            return (response,status.HTTP_400_BAD_REQUEST)

        if not brand:
            brand = "null"
        if not description:
            description = "null"
        df = df.append({
            'name' : name ,
            'description' : description,
            'brand' : brand,
            'price' : price
            },ignore_index=True)
        new_cdf.drop_duplicates(inplace=True)
        df.to_csv("product.csv",mode='a',header=False,encoding='utf-8',index=False)
        return {"message": "Created successfully.", "data": result}


class PostResource(Resource):

    def get(self, post_id):
        post = Product.query.get_or_404(post_id)
        return post_schema.dump(post)

    def patch(self, post_id):
        new_cdf =  pd.read_csv('product.csv')
        column_name = list(new_cdf.columns)
        df = pd.DataFrame(columns = column_name)
        data1 = csv.DictReader(new_cdf)
        data = request.form
        name = data['name']
        description = data['description']
        brand = data['brand']
        price = data['price']
        product_name = Product.query.filter_by(name=name).first()
        if not product_name:
            if not price:
                price  = 0
            product = Product.query.get_or_404(post_id)
            product.name = name
            product.brand = brand
            product.description = description
            product.price = price
            db.session.commit()
            result = post_schema.dump(product),status.HTTP_200_OK
            return {"message": "Product updated successfully." ,"data":result}
        else:
            response = {
                'status': False,
                'message': "Name already exists."
            }
            return (response,status.HTTP_400_BAD_REQUEST)

    def delete(self, post_id):
        post = Product.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        return f"Product with id {post_id} is deleted.",status.HTTP_200_OK


class CSVData(Resource):

    def post(self):
        new_cdf =  pd.read_csv('product.csv')
        column_name = list(new_cdf.columns)
        df = pd.DataFrame(columns = column_name)
        data_list = []
        for index, row in new_cdf.iterrows():
            data_dict ={
                'id' : row['id'],
                'name' : row['name'] ,
                'description' : row['description'],
                'brand' : row['brand'],
                'price' : row['price']
                }
            data_list.append(data_dict)
        for data in data_list:
            name = data['name']
            description = data['description']
            brand = data['brand']
            price = data['price']
            new_product = Product(
                name = name,
                brand = brand,
                description = description,
                price = price
                )
            db.session.add(new_product)
            db.session.commit()
        result = post_schema.dump(new_product),status.HTTP_201_CREATED
        return {"message": "Created successfully." ,"data":result}


