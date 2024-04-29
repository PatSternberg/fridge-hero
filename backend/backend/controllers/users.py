import jwt
import re
from datetime import datetime, timedelta
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient
import json




class PasswordValidator:
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, User=None):
        if len(password) < self.min_length:
            raise ValidationError(
                ("This password must contain at least %(min_length)d characters."),
                code="password_too_short",
                params={"min_length": self.min_length},
            )

        special_characters = "!@#$%^&*()-_+={}[]|\:"

        if not any(char in special_characters for char in password):
            raise ValidationError(
                ("This password must contain at least one special character."),
                code="password_no_special_character",
            )


class EmailValidator:
    def validate(self, email, user=None):
        if not re.match(r'^[\w\.-]+@[\w\.-]+$', email):
            raise ValidationError(
                ("Invalid email format."),
                code="invalid_email_format",
            )


def generate_token(user_id):
    payload = {
        'user_id': str(user_id),
        'exp': datetime.utcnow() + timedelta(minutes=10)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')


def get_db_handle(db_name, host, port, username, password):
    client = MongoClient(host=host, port=int(port), username=username, password=password)
    db_handle = client[db_name]
    return db_handle, client


@csrf_exempt
def signup(request): # Disables CSRF protection for this view
    if request.method == 'POST':
        print("Received signup request:", request.body)
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Initialize validators
        password_validator = PasswordValidator()
        email_validator = EmailValidator()

        try:
            # Validate password
            password_validator.validate(password)
            # Validate email
            email_validator.validate(email)

            # Get the database handle
            db, client = get_db_handle(db_name='fridge_hero',
                                       host='localhost',
                                       port=27017,
                                       username='',
                                       password='')

            users_collection = db['users']

             # if the email already exists
            if users_collection.find_one({'email': email}):
                return JsonResponse({'error': 'Email already in use.'}, status=400)


            # Insert the new user
            user_id = users_collection.insert_one({
                'username': username,
                'email': email,
                'password': password
            }).inserted_id

            # Clean up: close the MongoDB client
            client.close()

            return JsonResponse({'message': 'User created successfully', 'user_id': str(user_id)}, status=201)
        except ValidationError as e:
            # Validation failed
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Something went wrong: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def login(request):
    print('Getting this far')
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        # Get the database handle
        db, client = get_db_handle(db_name='fridge_hero',
                                   host='localhost', 
                                   port=27017, username='', 
                                   password='')

        users_collection = db['users']

        try:
            # Retrieve the user from the database
            user = users_collection.find_one({'email': email})
            if not user:
                # User not found
                return JsonResponse({'error': 'User not found'}, status=404)
            
            # Check if the password matches
            if password != user['password']:
                # Password incorrect
                return JsonResponse({'error': 'Password incorrect'}, status=401)
            
            # Generate token for the authenticated user
            token = generate_token(user['_id'])

            # Clean up: close the MongoDB client
            client.close()

            # Return token along with user_id
            response = JsonResponse({'message': 'Login successful', 'user_id': str(user['_id'])}, status=200)
            # response['authorization'] = f'Bearer {token}'
            return response
        except Exception as e:
            return JsonResponse({'error': f'Something went wrong: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
