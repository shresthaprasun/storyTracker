from flask import Blueprint
story_blueprint = Blueprint('storys', __name__, template_folder='templates')

from . import routes