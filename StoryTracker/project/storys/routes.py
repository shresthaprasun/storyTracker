from flask import render_template, request, flash, redirect, url_for, g, current_app
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from . import story_blueprint
from .forms import CreateStory
from project.models import Story
from project import db

@story_blueprint.before_request
def before_request():
    g.user = current_user






@story_blueprint.route('/')
def index():
	stories = Story.query.all()
	return render_template('storys/index.html', stories=stories)


@story_blueprint.route('/story' , methods=["GET", "POST"])
@login_required
def story():
	createStoryForm = CreateStory()
	if request.method == 'POST' and createStoryForm.validate_on_submit():
		try:
			story = Story(createStoryForm.title.data, createStoryForm.description.data, createStoryForm.date_of_completion.data, current_user.id)
			db.session.add(story)
			db.session.commit()
		except IntegrityError as err:
			db.session.rollback()
			flash('ERROR! ({}) '.format(err), 'error')

		return redirect(url_for('storys.story'))

	return render_template('storys/create_story.html', createStoryForm=createStoryForm)




@story_blueprint.route('/follow/<int:story_id>')
@login_required
def follow_story(story_id):
	story = Story.query.get(story_id)
	current_user.stories_followed.append(story)
	db.session.commit()
	return redirect(url_for('storys.index'))
