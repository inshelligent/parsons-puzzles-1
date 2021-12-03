from flask import Blueprint

puzzle = Blueprint('puzzle', __name__, template_folder='templates')

from app.puzzle import routes