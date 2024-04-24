from pymongo import MongoClient #MongoClient class  from pymongo library need it to connect to mongo DB
from django.db import models

class User(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)


    def save(self, *args, **kwargs):#method yo save user data into the database
        super().save(*args, **kwargs)

    def __str__(self):
        return self.id

# below is python code to connect to the mongo db not sure about django implementation of it



# # connecting to mongo DB
# client = MongoClient('mongodb://localhost:27017')# connect to a mongo db server default port
# db = client['our database name'] # connnect to our database
# collection = db['users']

#     def save(self): # method to save users data to the mongo db collection
#         user_data = { # user data dictionary with users attributes
#             'id': self.id,
#             'username': self.username,
#             'email': self.email,
#             'password': self.password
#         }
#     collection.insert_one(user_data) # inserts the user_data dictionary into the mongo db collection

# # testing to see if i can add users, creating a new user object with attributes call save method to save data in mongo
#     user = User(id='011',
#                 username='kevin',
#                 email='kevin@gmail.com',
#                 password='pass123')
#     user.save()