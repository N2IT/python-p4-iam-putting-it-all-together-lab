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
        if 'username' in data_form:
            new_user = User(
                username = data_form['username'],
                image_url = data_form['image_url'],
                bio = data_form['bio']
            )

            new_user.password_hash = data_form['password']
            session['user_id'] = new_user.id

            db.session.add(new_user)
            db.session.commit()

            return new_user.to_dict(), 201

        else:
            return {'message' : '422: Unprocessable Entry'}, 422

class CheckSession(Resource):
    def get(self):
        if session['user_id']:
            user = User.query.filter(User.id == session.get('user_id')).first()
            return user.to_dict(), 200
        else:
            return {'message' : '401 : Unauthorized'}, 401

class Login(Resource):
    def post(self):
        form_data = request.get_json()
        username = form_data['username']
        password = form_data['password']

        user = User.query.filter(User.username == username).first()

        if user is None:
            return {'error' : 'Invalid Username or password'}, 401

        if user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        
        return {'error' : '401: Unauthorized'}


class Logout(Resource):
    def delete(self):
        breakpoint()
        session['user_id'] = session.get('user_id')
        if session['user_id']:
            session['user_id'] = None
            return {}, 204
        
        return {'error' : '401: Unauthorized'}, 401
        
        

class RecipeIndex(Resource):
    pass

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)