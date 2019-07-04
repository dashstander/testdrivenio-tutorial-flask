# services/users/project/api/users/py

from flask import Blueprint, request, render_template
from flask_restful import Resource, Api
from project import db
from project.api.models import User
from sqlalchemy import exc

users_blueprint = Blueprint('users', __name__, template_folder='./templates')
api = Api(users_blueprint)


class UsersPing(Resource):
    def get(self):
        return {'status': 'success', 'message': 'pong!'}


class Users(Resource):
    def get(self, user_id):
        """Get single user details"""

        response_object = {'status': 'fail', 'message': 'User does not exist.'}

        try:
            user = User.query.filter_by(id=user_id).first()

            if not user:
                return response_object, 404
            else:
                response_object.pop('message')
                response_object['status'] = 'success'
                response_object['data'] = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'active': user.active
                }
        except exc.DataError:
            return response_object, 404

        return response_object, 200


class UsersList(Resource):
    def get(self):
        """Get all user details"""

        response_object = {'status': 'success'}

        response_object['data'] = {
            'users': [u.to_json() for u in User.query.all()]
        }

        return response_object, 200

    def post(self):
        post_data = request.get_json()

        response_object = {'status': 'fail', 'message': 'Invalid payload.'}
        sorry_message = 'Sorry. That email already exists.'
        if not post_data:
            return response_object, 400

        username = post_data.get('username')
        email = post_data.get('email')
        password = post_data.get('password')

        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                db.session.add(User(username=username, email=email, password=password))
                db.session.commit()
                response_object['status'] = 'success'
                response_object['message'] = f'{email} was added!'

                return response_object, 201
            else:
                response_object['message'] = sorry_message
                return response_object, 400
        except (exc.IntegrityError, ValueError):
            db.session.rollback()
            return response_object, 400


@users_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        db.session.add(User(username=username, email=email, password=password))
        db.session.commit()

    users = User.query.all()
    return render_template('index.html', users=users)


api.add_resource(UsersPing, '/users/ping')
api.add_resource(UsersList, '/users')
api.add_resource(Users, '/users/<user_id>')
