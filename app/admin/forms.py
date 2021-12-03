from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, PasswordField, SubmitField, IntegerField
from wtforms.widgets import HiddenInput
from wtforms.validators import DataRequired

from app.puzzle.forms import ProgramForm

class AdminSearchProgramForm(FlaskForm):
    ''' Form for searching through programs '''
    course = SelectField('Course')
    year = SelectField('Year')
    author = SelectField('Author')
    tag = SelectField('Tag')
    search = SubmitField('Search')

class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Sign In')

class TagAddForm(FlaskForm):
    name = StringField('Name', validators = [DataRequired()])
    hidden = BooleanField('Hidden?')
    submit = SubmitField('Add Tag')

class TagEditForm(TagAddForm):
    id = IntegerField(widget=HiddenInput())
    submit = SubmitField('Save Changes') 

class CourseAddForm(FlaskForm):
    name = StringField('Name', validators = [DataRequired()])
    year = IntegerField('Year', validators = [DataRequired()])
    semester = IntegerField('Semester', validators=[DataRequired()])
    current = BooleanField('Current?')
    submit = SubmitField('Add Course')

class CourseEditForm(CourseAddForm):
    id = IntegerField(widget=HiddenInput())
    submit = SubmitField('Save Changes') 

class CreateProgramForm(ProgramForm):
    ''' Form for creating program from admin view '''
    course_id = SelectField(coerce=int, label='Course')
    tag_id = SelectField(coerce=int, label='Tag')

class ProgramEditForm(CreateProgramForm):
    id = IntegerField(widget=HiddenInput())
    submit = SubmitField('Save Changes')
