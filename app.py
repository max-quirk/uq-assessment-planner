from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import csv
import scrape.helpers as helpers
from calendar_export import calExport
import dateparser
import os
from oauth2client import file, client, tools

app = Flask(__name__)
app.debug = True

all_course_assessment = []
port = int(os.environ.get('PORT', 5000))

def formatDate(date):
    return dateparser.parse(date)

def getProfileID(course_code):
    base_url = 'http://www.uq.edu.au/study/course.html?course_code=%s' \
        % course_code
    soup = helpers.get_soup(base_url)
    if soup is None or soup.find(id="course-notfound"):
        return None
    profileID = soup.find(class_='profile-available')['href'].split('=')[-1]
    return profileID


def getAssessments(profileID, course_code):
    ECP_url = "https://www.courses.uq.edu.au/student_section_loader.php?section=5&profileId=%s" % profileID

    # gets all tables on the page
    all_tables = pd.read_html(ECP_url, match='Assessment Task')
    # gets table containing desired information
    table = all_tables[2]
    table_length = table.shape[0] - 1
    print(table)
    assessments = []
    i = 1

    while i <= table_length:
        name = table.at[i, 0]
        print(splitName)
        due_date = table.at[i, 1]
        weighting = table.at[i, 2]
        learning_obj = table.at[i, 3]

        assessment = {
            'course_code': course_code,
            'name': splitName(name),
            'due_date': due_date,
            'weighting': weighting,
            'learning_obj': learning_obj
        }
        assessments.append(assessment)

        i += 1

    return assessments


def splitName(name):  # Separates assessment type from assessment name
    for index, letter in enumerate(name):
        try:
            if letter.islower() and name[index + 1].isupper() \
                    or letter == ')' and name[index + 1].isupper():
                return name[index+1:]
        except IndexError:
            return name
    return name


def makeHTML(all_course_assessments):
    html = ''
    html += '<div class="row">'
    columns = len(all_course_assessments)

    for course in all_course_assessments:
        html += '<div class="column-%s">' % columns
        html += '<h2 class="course-code">' + \
            course[0].get('course_code') + '</h2>'
        for assessment in course:
            html += '<h4 class="assessment-name"><strong>' + \
                assessment.get('name') + '</h4></strong>'
            html += '<p class="due-date">' + \
                assessment.get('due_date') + '</p>'
            html += '<p class="weighting">' + \
                assessment.get('weighting') + '</p>'
        html += '</div>'
    html += '</div>'
    return html

def makeChronologicalHTML(all_course_assessments):
    formatable_assessments = []
    for course in all_course_assessment:
        for assessment in course:
            if formatDate(assessment.get('due_date')) != None:
                formatable_assessments.append(assessment)

    formatable_assessments = sorted(formatable_assessments, key=lambda k: formatDate(k['due_date'])) 

    html = ''
    for assessment in formatable_assessments:
        title = '%s - %s' % (assessment.get('course_code').upper(), assessment.get('name'))
        html += '<tr>'
        html += '<td>%s</td>' % title
        html += '<td>%s</td>' % assessment.get('due_date')
        html += '<td>%s</td>' % assessment.get('weighting')
        html += '<td>%s</td>' % assessment.get('learning_obj')
        html += '</tr>'
    

    return html


@app.route("/", methods=['GET', 'POST'])
def hello():
    print(request.method)
    if request.method == 'GET':
        return render_template('title.html')

    course_1 = request.form.get('course-1')
    course_2 = request.form.get('course-2')
    course_3 = request.form.get('course-3')
    course_4 = request.form.get('course-4')
    course_5 = request.form.get('course-5')
    all_courses = []
    if course_1 is not None and course_1 != '':
        all_courses.append(course_1)
    if course_2 is not None and course_2 != '':
        all_courses.append(course_2)
    if course_3 is not None and course_3 != '':
        all_courses.append(course_3)
    if course_4 is not None and course_4 != '':
        all_courses.append(course_4)
    if course_5 is not None and course_5 != '':
        all_courses.append(course_5)

    print(all_courses)

    for course_code in all_courses:
        profileID = getProfileID(course_code)
        if profileID == None:
            error_message = '<p style="color: red">Error: One of the courses you entered was invalid. Please try again</p>'
            return render_template('title.html', error_message=error_message)
        assessments = getAssessments(profileID, course_code)
        all_course_assessment.append(assessments)

    by_course_as_html = makeHTML(all_course_assessment)
    chronological_html = makeChronologicalHTML(all_course_assessment)

    return render_template('citation.html', by_course_as_html=by_course_as_html, chronological_html=chronological_html)


@app.route("/export", methods=['GET', 'POST'])
def export():
    print('exporting')
    for course_assessments in all_course_assessment:
        for assessment in course_assessments:
            print(assessment)
            if formatDate(assessment['due_date']) != None:
                calExport(
                    assessment['course_code'].upper(), 
                    assessment['name'], 
                    assessment['weighting'], 
                    assessment['learning_obj'], 
                    formatDate(assessment['due_date']),
                )
    print('SUCCESSFULLY ADDED ALL EVENTS')

    return jsonify({'success': 'All events added'})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)
