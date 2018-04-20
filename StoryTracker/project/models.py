from project import db, bcrypt
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from datetime import datetime
from markdown import markdown
from flask import url_for
import bleach
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime


class ValidationError(ValueError):
    """Class for handling validation errors during
       import of recipe data via API
    """
    pass




class User(db.Model):
    """
    Class that represents a user of the application

    The following attributes of a user are stored in this table:
        email address
        password (hashed using Bcrypt)
        authenticated flag (indicates if a user is logged in or not)
        date that the user registered on
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    hashed_password = db.Column(db.Binary(60), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    birth_date = db.Column(db.DateTime, nullable=True)
    registered_on = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.String, default='user')
    email_confirmation_sent_on = db.Column(db.DateTime, nullable=True)
    email_confirmed = db.Column(db.Boolean, nullable=True, default=False)
    email_confirmed_on = db.Column(db.DateTime, nullable=True)

    def __init__(self,username, email, plaintext_password,birth_date, role='user',email_confirmation_sent_on=None):
        self.username = username
        self.email = email
        self.hashed_password = bcrypt.generate_password_hash(plaintext_password)
        self.authenticated = False        
        self.birth_date = birth_date
        self.registered_on = datetime.now()
        self.role = role
        self.email_confirmation_sent_on = email_confirmation_sent_on
        self.email_confirmed = False
        self.email_confirmed_on = None

    def set_password(self, plaintext_password):
        self.hashed_password = bcrypt.generate_password_hash(plaintext_password)

    def is_correct_password(self, plaintext_password):
        return bcrypt.check_password_hash(self.hashed_password, plaintext_password)

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    @property
    def is_active(self):
        """Always True, as all users are active."""
        return True

    @property
    def is_anonymous(self):
        """Always False, as anonymous users aren't supported."""
        return False

    def get_id(self):
        """Return the id of a user to satisfy Flask-Login's requirements."""
        return str(self.id)

    def __repr__(self):
        return '<User {}>'.format(self.email)






class Story(db.Model):
    """
    Class that represents a news/story of the application

    The following attributes of a story are stored in this table:
        title
        description
        videos
        images
    """
    __tablename__ = 'stories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, unique=True, nullable=True)


    def __repr__(self):
        return '<Story {}>'.format(self.title)





