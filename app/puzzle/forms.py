from flask import current_app
from flask_wtf import FlaskForm
from wtforms.fields import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import InputRequired, Length

class ProgramForm(FlaskForm):
    ''' Form for creation of a new program'''
    title = StringField('Title', [InputRequired(), 
        Length(min=4, max=100)], render_kw={'placeholder': 'Puzzle title'})
    author = StringField('Author', validators=[InputRequired(), Length(min=1, max=40)], 
        render_kw={'placeholder': 'Your first name'})
    description_placeholder = "Describe the problem that your code solves"
    puzzle_description = TextAreaField('Puzzle description', validators = [InputRequired(), 
        Length(min=4, max=2000)], render_kw={'rows': '5', 'placeholder': description_placeholder})
    code = TextAreaField('Code', [InputRequired(), Length(min=1, max=10000)],
        render_kw={'style': 'display: none;'})

class SearchProgramForm(FlaskForm):
    ''' Form for searching through programs '''
    course = SelectField('Course')
    tag = SelectField('Tag')
    author = SelectField('Author')
    search = SubmitField('Search')
