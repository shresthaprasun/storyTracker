# Check the PYTHONPATH environment variable before beginning to ensure that the
# top-level directory is included.  If not, append the top-level.  This allows
# the modules within the .../project/ directory to be discovered.
import sys
import os

print('Creating database tables for Food and Friends...')

if os.path.abspath(os.curdir) not in sys.path:
    print('...missing directory in PYTHONPATH... added!')
    sys.path.append(os.path.abspath(os.curdir))


# Create the database tables, add some initial data, and commit to the database
from project import db
from project.models import User

# from flask import current_app

# current_app.config.get('SQLALCHEMY_DATABASE_URI')

# Drop all of the existing database tables
db.drop_all()

# Create the database and the database table
db.create_all()

# Insert user data
user1 = User(email='prasun4nepal@gmail.com')
user2 = User(email='prasun@knaurtech.com')
user3 = User(email='blaa@blaa.com')
db.session.add(user1)
db.session.add(user2)
db.session.add(user3)

# Commit the changes for the users
db.session.commit()