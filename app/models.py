from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

from app import db, login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f'<User: { self.username }'
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text(), nullable = False)
    #semester = db.Column(db.Integer)
    #year = db.Column(db.Integer)
    current = db.Column(db.Boolean)
    programs = db.relationship('Program', back_populates = 'course')

    def __repr__(self):
        return f'<Course - {self.name}>'

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text(), nullable = False)
    hidden = db.Column(db.Boolean)
    programs = db.relationship('Program', back_populates = 'tag')

    def __repr__(self):
        return f'<Tag - {self.name}>'

class Program(db.Model):
    ''' Model that stores a program, which is displayed as puzzle in the UI'''
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(), nullable=False)
    author = db.Column(db.Text(), nullable=False)
    puzzle_description = db.Column(db.Text(), nullable=False)
    code = db.Column(db.Text(), nullable=False)
    url = db.Column(db.String(), unique=True, nullable=False)
    is_instructor = db.Column(db.Boolean)
    created = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    level = db.Column(db.Integer)

    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    tag = db.relationship('Tag', back_populates = 'programs')

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    course = db.relationship('Course', back_populates = 'programs')

    def __repr__(self):
        return f'<Program - {self.title}>'
