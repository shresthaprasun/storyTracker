#################
#### imports ####
#################

from flask import render_template, request, flash, redirect, url_for, g, current_app
from flask_login import login_user, current_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError
from smtplib import SMTPException, SMTPAuthenticationError
from flask_mail import Message
from threading import Thread
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime


from . import users_blueprint
from .forms import RegisterForm, LoginForm, EmailForm, PasswordForm
from project.models import User
from project import db, login, mail
from project.oauth import OAuthSignIn


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@users_blueprint.before_request
def before_request():
    g.user = current_user


##########################
#### helper functions ####
##########################

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'info')



def send_async_email(app, msg):
    
    with app.app_context():
        # flash("Reached to mail.send")
        mail.send(msg)


def send_email(subject, recipients, html_body):
    app = current_app._get_current_object()
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()


def send_confirmation_email(user_email):
    app = current_app._get_current_object()
    confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
 
    confirm_url = url_for(
        'users.confirm_email',
        token=confirm_serializer.dumps(user_email, salt='email-confirmation-salt'),
        _external=True)
 
    html = render_template(
        'users/email_confirmation.html',
        confirm_url=confirm_url)
 
    send_email('Confirm Your Email Address', [user_email], html)




def send_password_reset_email(user_email):
    app = current_app._get_current_object()
    password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    password_reset_url = url_for(
        'users.reset_with_token',
        token = password_reset_serializer.dumps(user_email, salt='password-reset-salt'),
        _external=True)

    html = render_template(
        'users/email_password_reset.html',
        password_reset_url=password_reset_url)

    send_email('Password Reset Requested', [user_email], html)

################
#### routes ####
################

# @users_blueprint.route('/')
# def index():
#     return render_template('users/index.html')


@users_blueprint.route('/profile')
@login_required
def profile():
    return render_template('users/user_profile.html')


@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # If the User is already logged in, don't allow them to try to register
    if current_user.is_authenticated:
        flash('Already registered!  Redirecting to your User Profile page...')
        return redirect(url_for('users.profile'))

    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            new_user = User(form.username.data,form.email.data, form.password.data,form.dob.data)
            new_user.authenticated = True
            db.session.add(new_user)
            db.session.commit()
            # msg = Message(subject='Registration',
            #                 body='Thanks for registering with Food and Friends!',
            #                 recipients=[new_user.email])
            # mail.send(msg)
            # login_user(new_user)
            send_confirmation_email(new_user.email)
            flash('Thanks for registering, {}!'.format(new_user.email))
            return redirect(url_for('users.profile'))
        except IntegrityError:
            db.session.rollback()
            flash('ERROR! Email ({}) already exists.'.format(form.email.data), 'error')
        except SMTPAuthenticationError:
            db.session.rollback()
            flash('ERROR! Message not send to email ({}) .'.format(form.email.data), 'error')
    return render_template('users/register.html', form=form)


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # If the User is already logged in, don't allow them to try to log in again
    if current_user.is_authenticated:
        flash('Already logged in!  Redirecting to your User Profile page...')
        return redirect(url_for('users.profile'))

    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            flash('User Email:'+form.email.data)
            if user and user.is_correct_password(form.password.data):
                user.authenticated = True
                flash('Before logging in, {}!'.format(user.email))
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=form.remember_me.data)
                flash('Thanks for logging in, {}!'.format(current_user.email))
                return redirect(url_for('users.profile'))

        flash('ERROR! Incorrect login credentials.')
    return render_template('users/login.html', form=form)


@users_blueprint.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    flash('Goodbye!')
    return redirect(url_for('users.login'))



#users email confirmation
@users_blueprint.route('/confirm/<token>')
def confirm_email(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = confirm_serializer.loads(token, salt='email-confirmation-salt', max_age=3600)
    except:
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('users.login'))
 
    user = User.query.filter_by(email=email).first()
 
    if user.email_confirmed:
        flash('Account already confirmed. Please login.', 'info')
    else:
        user.email_confirmed = True
        user.email_confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('Thank you for confirming your email address!')
 
    return redirect(url_for('stories.index'))


# Oauth 
@users_blueprint.route('/authorize/<provider>')
def oauth_authorize(provider):
    # if not current_user.is_anonymous:
    #     return redirect(url_for('site.index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@users_blueprint.route('/callback/<provider>')
def oauth_callback(provider):
    # if not current_user.is_anonymous:
    #     return redirect(url_for('site.index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('stories.index'))
    user = User.query.filter_by(email=email).first()
    if user and user.is_correct_password(social_id):
        user.authenticated = True
        flash('Before logging in, {}!'.format(user.email))
        db.session.add(user)
        db.session.commit()
    if not user:     
       
        user = User(username=username, email=email,plaintext_password=social_id,birth_date=None)
        user.authenticated = True
        db.session.add(user)
        db.session.commit()
        # db.session.add(user.follow(user))
        # db.session.commit()
    login_user(user, True)
    # g.user = current_user

    # # return redirect(url_for('login'))
    return redirect(request.args.get('next') or url_for('users.profile'))


#Forget Password

@users_blueprint.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        password_reset_serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('users.login'))

    form = PasswordForm()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=email).first_or_404()
        except:
            flash('Invalid email address!', 'error')
            return redirect(url_for('users.login'))

        # user.password = form.password.data
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('users.login'))

    return render_template('users/reset_password_with_token.html', form=form, token=token)


@users_blueprint.route('/reset', methods=["GET", "POST"])
def reset():
    form = EmailForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first_or_404()
        except:
            flash('Invalid email address!', 'error')
            return render_template('users/password_reset_email.html', form=form)

        if user.email_confirmed:
            flash('Email COnfirmed')
            send_password_reset_email(user.email)
            flash('Please check your email for a password reset link.', 'success')
        else:
            flash('Your email address must be confirmed before attempting a password reset.', 'error')
        return redirect(url_for('users.login'))

    return render_template('users/password_reset_email.html', form=form)



@users_blueprint.route('/email_change', methods=["GET", "POST"])
@login_required
def user_email_change():
    form = EmailForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                user_check = User.query.filter_by(email=form.email.data).first()
                
                if user_check is None:
                    user = current_user
                    user.email = form.email.data
                    user.email_confirmed = False
                    user.email_confirmed_on = None
                    user.email_confirmation_sent_on = datetime.now()
                    db.session.add(user)
                    db.session.commit()
                    send_confirmation_email(user.email)
                    flash('Email changed!  Please confirm your new email address (link sent to new email).', 'success')
                    return redirect(url_for('users.profile'))
                else:
                    flash('Sorry, that email already exists!', 'error')
            except IntegrityError:
                db.session.rollback()
                flash('ERROR! Email ({}) already exists.'.format(form.email.data), 'error')
            except SMTPAuthenticationError:
                db.session.rollback()
                flash('ERROR! Message not send to email ({}) .'.format(form.email.data), 'error')
    
    return render_template('users/email_change.html', form=form)


@users_blueprint.route('/password_change', methods=["GET", "POST"])
@login_required
def user_password_change():
    form = PasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = current_user
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Password has been updated!', 'success')
            return redirect(url_for('users.profile'))
    print ("Test 5")
    return render_template('users/password_change.html', form=form)


@users_blueprint.route('/resend_confirmation')
@login_required
def resend_email_confirmation():
    try:
        send_confirmation_email(current_user.email)
        flash('Email sent to confirm your email address.  Please check your email!', 'success')
    except IntegrityError:
        flash('Error!  Unable to send email to confirm your email address.', 'error')

    return redirect(url_for('users.profile'))