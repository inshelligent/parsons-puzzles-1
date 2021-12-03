import json

from flask import render_template, url_for, flash, request
from werkzeug.utils import redirect
from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.admin import admin
from app.models import User, Program, Course, Tag
from app.utils import (
    get_author_choices, get_course_choices, get_tag_choices, generate_random_url
)
from .forms import (
    AdminSearchProgramForm, CreateProgramForm, ProgramEditForm,
    LoginForm, TagAddForm, TagEditForm, CourseAddForm, CourseEditForm
)

@admin.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            form.username.errors.append('Invalid username or password')
            return render_template('login.html', title = 'Admin Login', form = form, action = 'logging in')
        login_user(user)
        return redirect(url_for('admin.index'))
    return render_template('login.html', title = 'Admin Login', form = form, action = 'logging in')

@admin.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@admin.route('/manage')
@login_required
def manage():
    form = AdminSearchProgramForm(request.args)

    courses = Course.query.all()
    programs = Program.query.all()
    tags = Tag.query.all()

    form.course.choices = get_course_choices(courses)
    #form.year.choices = get_year_choices(courses)
    form.author.choices = get_author_choices(programs)
    form.tag.choices = get_tag_choices(tags)

    query = Program.query.join(Course)

    if form.course.data is not None and form.course.data != 'None' and form.course.data != '-':
        query = query.filter(Course.name == form.course.data)

    #if form.year.data is not None and form.year.data != 'None' and form.year.data != '-':
    #    query = query.filter(Course.year == form.year.data)
    
    if form.author.data is not None and form.author.data != 'None' and form.author.data != '-':
        query = query.filter(Program.author == form.author.data)

    if form.tag.data is not None and form.tag.data != 'None' and form.tag.data != '-':
        query = query.filter(Program.tag_id == int(form.tag.data))

    query = query.order_by(Program.created.desc())
    page = request.args.get('page', 1, type = int)
    posts_per_page = 20

    puzzles_page = puzzles_page = query.paginate(page, posts_per_page, False)

    return render_template('manage_puzzles.html', puzzles_page = puzzles_page, title = 'Manage Puzzles', form = form)

@admin.route('/')
@admin.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('admin.manage'))
    else:
        return redirect(url_for('admin.login'))

@admin.route('/tag')
@login_required
def tag_list():
    tags = Tag.query.all()
    return render_template('tag_list.html', tags = tags, title = 'Manage Tags')

@admin.route('/add_tag', methods = ['GET','POST'])
@login_required
def tag_add():
    form = TagAddForm()
    if form.validate_on_submit():
        tag = Tag()
        form.populate_obj(tag)

        db.session.add(tag)
        db.session.commit()
        
        return render_template(
            'tag_success.html', 
            title = 'Added Tag Successfully',
            tag_name = tag.name
        )
    return render_template('tag_add.html', title = 'Add Tag', form = form)

@admin.route('/tag/<int:id>', methods = ['GET', 'POST'])
@login_required
def tag_edit(id):
    tag = Tag.query.get_or_404(id)
    form = TagEditForm(obj=tag)
    if form.validate_on_submit():
        form.populate_obj(tag)
        db.session.commit()
        return redirect(url_for('admin.tag_list'))
    return render_template('tag_edit.html', title = 'Edit Tag', tag = tag, form = form)

@admin.route('/tag/<int:id>/delete')
@login_required
def tag_delete(id):
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for('admin.tag_list'))

@admin.route('/course')
@login_required
def course_list():
    courses = Course.query.all()
    return render_template('course_list.html', title = 'Manage Courses', courses = courses)

@admin.route('/add_course', methods = ['GET', 'POST'])
@login_required
def course_add():
    form = CourseAddForm()
    if form.validate_on_submit():
        course = Course()
        form.populate_obj(course)

        db.session.add(course)
        db.session.commit()
        
        return render_template(
            'course_success.html', 
            title = 'Added Course Successfully',
            course_name = course.name
        )
    return render_template('course_add.html', title = 'Add Course', form = form)

@admin.route('/course/<int:id>/delete')
@login_required
def course_delete(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('admin.course_list'))

@admin.route('/course/<int:id>', methods = ['GET', 'POST'])
@login_required
def course_edit(id):
    course = Course.query.get_or_404(id)
    form = CourseEditForm(obj=course)
    if form.validate_on_submit():
        form.populate_obj(course)
        db.session.commit()
        return redirect(url_for('admin.course_list'))
    return render_template('course_edit.html', title = 'Edit Tag', course = course, form = form)

@admin.route('/puzzle/<int:id>/delete')
@login_required
def puzzle_delete(id):
    program = Program.query.get_or_404(id)
    db.session.delete(program)
    db.session.commit()
    return redirect(url_for('admin.manage'))

@admin.route('/add_puzzle', methods = ['GET','POST'])
@login_required
def create_puzzle():
    ''' Create a new puzzle and store it in the database '''
    form = CreateProgramForm()

    tags = Tag.query.all()
    form.tag_id.choices = [(tag.id, tag.name) for tag in tags]
    courses = Course.query.order_by(Course.name.desc()).all()
    form.course_id.choices = [(course.id, f'{course.name}') for course in courses]
    form.author.data = current_user.username

    if form.validate_on_submit():
        # Algorithm continues to generate urls until a unique one is found
        unique_url = False
        while unique_url == False:
            program_url = generate_random_url()
            # Checks if the generated url is unique
            program_with_url = Program.query.filter_by(url=program_url).first()
            if program_with_url is None:
                unique_url = True

        # Create and store the new program in the database
        program = Program()
        form.populate_obj(program)
        if form.tag_id.data == '-':
            program.tag_id = None
        program.url = program_url
        program.is_instructor = True

        db.session.add(program)
        db.session.commit()

        # Direct the user to the detail page for the created program
        return redirect(url_for('puzzle.puzzle_detail', program_url=program_url))

    # If there was a submission of code, send this back to client
    submitted_code = None
    if form.code.data:
        submitted_code = json.dumps(form.code.data)

    return render_template('create_admin.html', form = form, code= submitted_code, title = 'Create Puzzle (Admin)')

@admin.route('/puzzle/<int:id>', methods = ['GET','POST'])
@login_required
def edit_puzzle(id):
    program = Program.query.get_or_404(id)
    form = ProgramEditForm(obj = program)
    tags = Tag.query.all()
    form.tag_id.choices = [(tag.id, tag.name) for tag in tags]
    courses = Course.query.order_by(Course.name.desc()).all()
    form.course_id.choices = [(course.id, f'{course.name}') for course in courses]
    submitted_code = json.dumps(form.code.data)
    
    if form.validate_on_submit():
        form.populate_obj(program)
        if form.tag_id.data == '-':
            program.tag_id = None
        db.session.commit()
        return redirect(url_for('puzzle.puzzle_detail', program_url=program.url))

    return render_template('program_edit.html', title = 'Edit Program', program = program, form = form, code = submitted_code)