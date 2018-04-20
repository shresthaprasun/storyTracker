from flask import render_template, request, flash, redirect, url_for, g, current_app
from flask_login import current_user, login_required

from . import story_blueprint
from .forms import CreateStory


@story_blueprint.before_request
def before_request():
    g.user = current_user

@story_blueprint.route('/story')
def story():
	createStoryForm = CreateStory()
	return render_template('storys/index.html', createStoryForm=createStoryForm)