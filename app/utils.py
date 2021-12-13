import random
import string

def generate_random_url(string_length=6):
    ''' Generate a random string for a program url'''
    letters = string.ascii_uppercase
    return ''.join(random.choice(letters) for i in range(string_length))

def generate_file_name(puzzle_url, puzzle_title):
    ''' Generate a file name for a given puzzle for download '''
    file_name = puzzle_title.lower().replace(' ', '_')
    file_name = f'{file_name}_{puzzle_url}.py'
    return file_name

def get_course_choices(courses):
    # Default value for unspecified course name
    course_choices = [(0,'-')]
    for course in courses:
        if course.name not in course_choices:
            course_choices.append((course.id, course.name))
    #course_names_in_tuples = [(name, name) for name in course_names]
    course_choices.sort()
    return course_choices

def get_author_choices(programs):
    # Default value for unspecified author name
    authors = [('-')]
    for program in programs:
        if program.author not in authors:
            authors.append(program.author)
    authors.sort()
    authors_in_tuples = [(author, author) for author in authors]
    return authors_in_tuples

def get_tag_choices(tags):
    # Default value for unspecified tag name
    tag_choices = [(0,'-')]
    for tag in tags:
        tag_choices.append(( tag.id, tag.name ))
    return tag_choices

def get_level_choices():
    level_choices = [(0,'-')]
    for count in range(1,5):
        level_choices.append(( count, 'Level '+str(count) ))
    return level_choices