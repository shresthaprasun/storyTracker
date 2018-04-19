from flask import g
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
# To keep things clean, we keep our Flask-Nav instance in here. We will define
# frontend-specific navbars in the respective frontend, but it is also possible
# to put share navigational items in here.

nav = Nav()

# @nav.navigation()
# def top_nav():
#     items = [View('Home', 'index'), View('Shopping Area', 'index')]

#     # only logged in users get to see the secret shop
#     if user_is_logged_in():
#         items.append(View('Secret Shop', 'secret'))

#     return Navbar('', *items)

@nav.navigation()
def usernavbar():
    return Navbar(
        'Story Tracker',
        View('Home', '.index'),
        View(g.user.username, '.profile'),
        View('Meet N Eat', '.index'),
        View('Notification', '.index'),
        View('Analytics', '.index'),
        View('For Business', '.index'),
        View('History', '.index'),
        View('Logout', '.logout'),
    )


@nav.navigation()
def homenavbar():
    return Navbar(
        'Story Tracker',
        View('Flask-Bootstrap', '.index'),
        View('Home', '.index'),
        View('Register', '.register'),
        View('Login', '.login'),
        # View('Forms Example', '.example_form'),
        # View('Debug-Info', 'debug.debug_root'),
        Subgroup(
            'Docs',
            Link('Flask-Bootstrap', 'http://pythonhosted.org/Flask-Bootstrap'),
            Link('Flask-AppConfig', 'https://github.com/mbr/flask-appconfig'),
            Link('Flask-Debug', 'https://github.com/mbr/flask-debug'),
            Separator(),
            Text('Bootstrap'),
            Link('Getting started', 'http://getbootstrap.com/getting-started/'),
            Link('CSS', 'http://getbootstrap.com/css/'),
            Link('Components', 'http://getbootstrap.com/components/'),
            Link('Javascript', 'http://getbootstrap.com/javascript/'),
            Link('Customize', 'http://getbootstrap.com/customize/'), ),
        Text('Using Flask-Bootstrap {}'.format(FLASK_BOOTSTRAP_VERSION)),
    )

