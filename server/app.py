#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import validates

from config import app, db, api
from models import User, Recipe

class Signup(Resource):

    def post(self):
        # breakpoint()
        
        data_form = request.get_json()
        username = data_form.get('username')
        image_url = data_form.get('image_url')
        bio = data_form.get('bio')

        user = User.query.filter(User.username == username).first()

        errors = []
        if username == "":
            errors.append('Username must be populated')

        if user and username == user.username:
            errors.append('That username is already taken.')

        if errors:
            return {'errors': errors}, 422
        
        if 'username' in data_form:
            new_user = User(
                username = data_form.get('username'),
                image_url = data_form.get('image_url'),
                bio = data_form.get('bio')
            )

            new_user.password_hash = data_form['password']

            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id

            return new_user.to_dict(), 201

        else:
            return {'errors' : '422: Unprocessable Entry'}, 422

class CheckSession(Resource):
    def get(self):
        if session['user_id']:
            user = User.query.filter(User.id == session.get('user_id')).first()
            return user.to_dict(), 200
        else:
            return {'errors' : '401 : Unauthorized'}, 401

class Login(Resource):
    def post(self):
        form_data = request.get_json()
        username = form_data.get('username')
        password = form_data.get('password')

        user = User.query.filter(User.username == username).first()
        breakpoint()

        if username == "":
            return {"errors" : "401: username needed to login"}, 401

        if password == "":
            return {'errors' : "401: invalid password"}, 401

        if user:
            if user.authenticate(password):
                session['user_id'] = user.id
                return user.to_dict(), 200
        
        return {'errors' : '401: Unauthorized'}, 401


class Logout(Resource):
    def delete(self):
        # session['user_id'] = session.get('user_id')
        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
    
        return {'errors' : '401: Unauthorized'}, 401
        
        
class RecipeIndex(Resource):
    def get(self):
        recipes = Recipe.query.all()
        if session['user_id']:
            return [recipe.to_dict() for recipe in recipes]
        else:
            return {
                'errors' : '401: Unauthorized'
            }, 401

    def post(self):
        data_form = request.get_json()
        if session.get('user_id'):       
            try:
                new_recipe = Recipe(
                    title = data_form.get('title'),
                    instructions = data_form.get('instructions'),
                    minutes_to_complete = data_form.get('minutes_to_complete'),
                )

                new_recipe.user_id = session['user_id']

                db.session.add(new_recipe)
                db.session.commit()

                return new_recipe.to_dict(), 201

            except IntegrityError:
                return {"errors" : "422: Instructions must have 50 characters"}, 422

    

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)