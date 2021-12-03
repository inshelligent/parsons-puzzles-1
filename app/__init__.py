import os
from datetime import datetime

import click
from flask.cli import with_appcontext
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flaskext.markdown import Markdown
from flask_login import LoginManager

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('PARSON_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, os.environ.get('PARSON_SQLITE_FILE'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# register the database
db = SQLAlchemy(app)

Markdown(app)
login = LoginManager(app)
login.login_view = 'admin.login'

from app import routes, models

# apply the blueprints to the app
from app.puzzle import puzzle
app.register_blueprint(puzzle, url_prefix = '/puzzle')
from app.admin import admin
app.register_blueprint(admin, url_prefix = '/admin')

# Click commands for performing migration of data

@app.cli.command('init-db')
def init_db():
    ''' Clear existing data and create new tables.'''

    click.echo('Drop all...')
    db.drop_all()

    click.echo('Create all...')
    db.create_all()

    click.echo('Create an example course...')
    programming_course = models.Course (
        name = 'PROG101',
        semester = 2,
        year = 2021,
        current = True
    )
    db.session.add(programming_course)

    click.echo('Create tags for Weeks 0-2...')
    tags = {}
    for n in range(0, 3):
        tag = models.Tag(name = f'Week {n}', hidden = False)
        db.session.add(tag)
        tags[str(n)] = tag
    
    click.echo('Create an admin user from .env settings...')
    admin_username = os.environ.get('PARSON_ADMIN_USERNAME')
    admin_email = os.environ.get('PARSON_ADMIN_EMAIL')
    admin_password = os.environ.get('PARSON_ADMIN_PASSWORD')
    admin_user = models.User(username = admin_username, email = admin_email)
    admin_user.set_password(admin_password)
    db.session.add(admin_user)

    click.echo('Create an example program tagged for Week 1...')
    program = models.Program (
        title = 'Hello World',
        puzzle_description = "This is a program that prints 'Hello world!'",
        code = "print('Hello world!')\n'Hello world!' #distractor",
        url = 'AAA111',
        is_instructor = True,
        created = datetime.now(),
        author = os.environ.get('PARSON_ADMIN_USERNAME'),
        course = programming_course,
        tag = tags['1']
    )
    db.session.add(program)

    # Commit the newly created records to the database
    db.session.commit()