from pymongo import MongoClient #MongoClient class  from pymongo library need it to connect to mongo DB

# connecting to mongo DB
client = MongoClient('mongodb://localhost:27017')# connect to a mongo db server default port
db = client['our database name'] # connnect to our database
collection = db['users']

class User:

    def __init__(self, id, username,  email, password):
        
        self.id = id
        self.username = username
        self.email = email
        self.password = password

    def save(self): # method to save users data to the mongo db collection
        user_data = { # user data dictionary with users attributes
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password': self.password
        }
    collection.insert_one(user_data) # inserts the user_data dictionary into the mongo db collection

# testing to see if i can add users, creating a new user object with attributes call save method to save data in mongo
    user = User(id='011',
                username='kevin',
                email='kevin@gmail.com',
                password='pass123')
    user.save()

