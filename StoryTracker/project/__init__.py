from flask import Flask, render_template, make_response, jsonify, g
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


#######################
#### Configuration ####
#######################


# Create the instances of the Flask extensions (flask-sqlalchemy, flask-login, etc.) in
# the global scope, but without any arguments passed in.  These instances are not attached
# to the application at this point.
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
login = LoginManager()
login.login_view = "users.login"


######################################
#### Application Factory Function ####
######################################
 
def create_app(config_filename=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config_filename)
    initialize_extensions(app)
    register_blueprints(app)
    return app

##########################
#### Helper Functions ####
##########################

def initialize_extensions(app):
    # Since the application instance is now created, pass it to each Flask
    # extension instance to bind it to the Flask application instance (app)
    with app.app_context():
        db.init_app(app)

        bcrypt.init_app(app)
        mail.init_app(app)
        login.init_app(app)
        
        from project.nav import nav
        nav.init_app(app)



def register_blueprints(app):
    # Since the application instance is now created, register each Blueprint
    # with the Flask application instance (app)
    
    from project.users import users_blueprint
    from project.storys import story_blueprint

    
    app.register_blueprint(users_blueprint)
    app.register_blueprint(story_blueprint)



# Initialize the extension
app = create_app('flask.cfg')
# db = SQLAlchemy(app)
Bootstrap(app)


# from project.users import users_blueprint

    # app.register_blueprint(recipes_blueprint)
# app.register_blueprint(users_blueprint)



from project.models import User, Story, User_Story

admin = Admin(app, name='app', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Story, db.session))
admin.add_view(ModelView(User_Story, db.session))
# with app.app_context():
#     db.init_app(app)



############################
#### custom error pages ####
############################

from project.models import ValidationError


@app.errorhandler(ValidationError)
def bad_request(e):
    response = jsonify({'status': 400, 'error': 'bad request',
                        'message': e.args[0]})
    response.status_code = 400
    return response


@app.errorhandler(400)
def page_not_found(e):
    return make_response(jsonify({'error': 'Not found'}), 400)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# @app.errorhandler(404)
# def not_found(e):
#     response = jsonify({'status': 404, 'error': 'not found', 'message': 'invalid resource URI'})
#     response.status_code = 404
#     return response


@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403


@app.errorhandler(410)
def page_not_found(e):
    return render_template('410.html'), 410