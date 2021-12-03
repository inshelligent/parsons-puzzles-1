import json

from flask import render_template, request, Response, redirect, url_for
from sqlalchemy import desc, asc
from flask_login import login_required

from app import db
from app.puzzle import puzzle
from app.models import Program, Tag, Course
from app.utils import (
    get_course_choices, get_year_choices, get_author_choices, generate_random_url, generate_file_name,
)
from .forms import SearchProgramForm, ProgramForm

@puzzle.route('/prog101')
def prog101_puzzles():
    ''' Show all the current programs for PROG101 '''
    puzzles = Program.query.filter(Program.is_instructor == True) \
                .join(Course).filter(Course.name == 'PROG101') \
                .join(Tag).filter(Tag.hidden == False) \
                .order_by(desc(Tag.name), asc(Program.created)) \
                .all()
    return render_template('puzzles_list.html', puzzles = puzzles, course = 'PROG101', title = 'Programming Puzzles')

@puzzle.route('/all', methods = ['GET', 'POST'])
def all_puzzles():
    ''' Show all of the puzzles in the database, except those for current course that are hidden '''
    form = SearchProgramForm(request.args)

    courses = Course.query.all()
    programs = Program.query.all()
    form.course.choices = get_course_choices(courses)
    form.year.choices = get_year_choices(courses)
    form.author.choices = get_author_choices(programs)

    query = Program.query.outerjoin(Tag).join(Course) \
                .filter(((Course.current == True) & ((Tag.hidden == False) | (Program.tag_id == None ))) | (Course.current == False)) 

    if form.course.data is not None and form.course.data != 'None' and form.course.data != '-':
        query = query.filter(Course.name == form.course.data)

    if form.year.data is not None and form.year.data != 'None' and form.year.data != '-':
        query = query.filter(Course.year == form.year.data)
    
    if form.author.data is not None and form.author.data != 'None' and form.author.data != '-':
        query = query.filter(Program.author == form.author.data)

    query = query.order_by(Program.created.desc())
    page = request.args.get('page', 1, type = int)
    posts_per_page = 10

    puzzles_page = query.paginate(page, posts_per_page, False)

    return render_template('puzzle_search.html', 
        puzzles_page = puzzles_page, title = 'All Puzzles', form = form
    )

@puzzle.route('/<string:program_url>')
def puzzle_detail(program_url):
    ''' Show specific program as a puzzle. '''
    puzzle = (Program.query.filter_by(url=program_url).first_or_404())
    return render_template('puzzle.html', puzzle = puzzle)

@puzzle.route('/download/<string:program_url>')
@login_required
def download_puzzle(program_url):
    ''' Send a response with the given program as python file for download '''
    puzzle = Program.query.filter_by(url=program_url).first_or_404()
    puzzle_code = puzzle.code
    file_name = generate_file_name(program_url, puzzle.title)
    return Response(puzzle_code, mimetype='text/plain', headers={'Content-Disposition': f'attachment;filename={file_name}'})

@puzzle.route('/', methods=('GET', 'POST'))
def create():
    ''' Create a new puzzle and store it in the database '''
    form = ProgramForm(request.form)
    if form.validate_on_submit():
        # Algorithm continues to generate urls until a unique one is found
        unique_url = False
        while unique_url == False:
            program_url = generate_random_url()
            # Checks if the generated url is unique
            program_with_url = Program.query.filter_by(url=program_url).first()
            if program_with_url is None:
                unique_url = True

        course = Course.query.filter(Course.name == 'EDPF5023', Course.semester == 2).first()

        # Create and store the new program in the database
        program = Program()
        form.populate_obj(program)
        program.course = course
        program.url = program_url
        program.is_instructor = False

        db.session.add(program)
        db.session.commit()

        # Direct the user to the detail page for the created program
        return redirect(url_for('puzzle.puzzle_detail', program_url=program_url))

    # If there was a submission of code, send this back to client
    submitted_code = None
    if form.code.data:
        submitted_code = json.dumps(form.code.data)

    return render_template('create.html', form=form, code=submitted_code)