from flask import render_template, url_for, redirect

from app import app

@app.route('/research')
def research():
    ''' Show page with research about Parson's puzzles '''
    return render_template('research.html')

@app.route('/levels')
def levels():
    ''' Show page with info about difficulty levels '''
    return render_template('levels.html')

@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('puzzle.all_puzzles'))

