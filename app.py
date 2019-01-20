from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import csv
import scrape.helpers as helpers
# from calendar_export import calExport
import dateparser
import os
from oauth2client import file, client, tools
import sys
import flask
import google_auth_oauthlib.flow
import google.oauth2.credentials
import googleapiclient.discovery
from datetime import datetime, timedelta 
from database import Db

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPE = 'https://www.googleapis.com/auth/calendar'
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'
db = Db(detailed=False)
db.connect("uq_catalogue", "maxquirk", "", "localhost")

app = Flask(__name__)
app.debug = True

all_course_assessment = []
port = int(os.environ.get('PORT', 5000))


def formatDate(date):
    # print(date)
    # #check if date contains no digits
    # if not any(char.isdigit() for char in date):
    #     return None

    # dates = date.split('-')
    # if len(dates) > 1:
    #     date1 = dateparser.parse(dates[0])
    #     date2 = dateparser.parse(dates[1])
    #     if date1 and date2:
    #         if date1.date() == date2.date():
    #             date = dates[0]
    #             return dateparser.parse(date)
    # print('parsing date...')
    # date = dateparser.parse(date)
    # print('parsed')
    # return date 
    return None

def getProfileID(course_code):
    print('getting profile id...')
    query = "SELECT course_profile_id FROM course WHERE course_code = '%s'" % (course_code.upper())
    profileID = db.select(query)
    if profileID:
        print('finished getting profile id')
        return profileID[0][0]
    # base_url = 'http://www.uq.edu.au/study/course.html?course_code=%s' \
    #     % course_code
    # soup = helpers.get_soup(base_url)
    # if soup is None or soup.find(id="course-notfound"):
    #     return None
    # profileID = soup.find(class_='profile-available')['href'].split('=')[-1]
    # return profileID


def getAssessments(profileID, course_code):
    # ECP_url = "https://www.courses.uq.edu.au/student_section_loader.php?section=5&profileId=%s" % profileID
    print('getting assessments...')
    query = """
            SELECT assessment_name, due_date, weighting, learning_obj 
            FROM course_assessment
            WHERE course_code = '%s'
            """ % (course_code.upper())
    unformatted_assessments = db.select(query)

    if not unformatted_assessments:
        return 

    assessments = []

    for i, unformatted_assessment in enumerate(unformatted_assessments):
        name = unformatted_assessments[i][0]
        due_date = unformatted_assessments[i][1]
        weighting = unformatted_assessments[i][2]
        learning_obj = unformatted_assessments[i][3]

        assessment = {
                'course_code': course_code,
                'name': name,
                'due_date': due_date,
                'weighting': weighting,
                'learning_obj': learning_obj
        }

        assessments.append(assessment)
    # ECP_url = 'https://www.courses.uq.edu.au/student_section_loader.php?section=5&profileId=%s' % profileID
    # # gets all tables on the page
    # all_tables = pd.read_html(ECP_url, match='Assessment Task')
    # # gets tables containing desired information
    # all_tables = all_tables[2:]
    # assessments = []
    # for table in all_tables:
    #     table_length = table.shape[0] - 1
    #     i = 1

    #     while i <= table_length:
            
    #         name = table.at[i, 0]
    #         print(splitName(name))
    #         due_date = table.at[i, 1]
    #         weighting = table.at[i, 2]
    #         learning_obj = table.at[i, 3]

    #         assessment = {
    #             'course_code': course_code,
    #             'name': splitName(name),
    #             'due_date': due_date,
    #             'weighting': weighting,
    #             'learning_obj': learning_obj
    #         }
    #         assessments.append(assessment)

    #         i += 1

    print('finished getting assessments')
    
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
    print('making html...')
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
    print('finished making html')
    return html

def makeChronologicalHTML(all_course_assessments):
    print('making chronological html...')
    formatable_assessments = []
    for course in all_course_assessment:
        for assessment in course:
            print(assessment)
            if formatDate(assessment.get('due_date')) != None:
                formatable_assessments.append(assessment)
    print(formatable_assessments)
    if formatable_assessments:
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
    
        print('finished making chronological html')
        return html

    return ''

def calExport(calendar, event):
    event = calendar.events().insert(calendarId='primary', body=event).execute()

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
    sys.stdout.flush()
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    print('didnt authorize')
    credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])
    print('got to here')

    calendar = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    for course_assessments in all_course_assessment:
        for assessment in course_assessments:
            print(assessment)
            course = assessment['course_code'].upper()
            assessment_name = assessment['name']
            weighting = assessment['weighting']
            learning_obj = assessment['learning_obj']
            due_date = formatDate(assessment['due_date'])

            if formatDate(assessment['due_date']) != None:
                title = "%s - %s" % (course, assessment_name)
                description = 'Weighting: %s \nLearning objectives: %s' % (weighting, learning_obj)
                end = due_date + timedelta(hours=1)
                event = {
                    'summary': title,
                    'description': description,
                    'start': {
                        'dateTime': due_date.strftime("%Y-%m-%dT%H:%M:%S"), #'2018-12-29T09:00:00-07:00',
                        'timeZone': 'Australia/Brisbane',
                    },
                    'end': {
                        'dateTime': end.strftime("%Y-%m-%dT%H:%M:%S"),
                        'timeZone': 'Australia/Brisbane',
                    }
                }

                calExport(calendar, event)

    print('SUCCESSFULLY ADDED ALL EVENTS')

    return jsonify({'success': 'All events added'})

@app.route("/authorize")
def authorize():
    print('debug1')
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('client_secret.json', scopes=SCOPE)
    print('debug2')
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    print('debug3')
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    print('debug4')
    #flask.session['state'] = state
    print('debug6')
    print(authorization_url)
    return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    #state = flask.session['state']
    print('fucks sake')
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPE)
    print('fucks sake')
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    print('fucks sake')

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    print('fucks sake')
    flow.fetch_token(authorization_response=authorization_response)
    print('fucks sake')

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    print('fucks sake')
    flask.session['credentials'] = credentials_to_dict(credentials)
    print('fucks sake')

    return flask.redirect('export')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

@app.route('/.well-known/acme-challenge/gLguitC8-PJzAcAHOGHvlK_q_71gSJQQcB_xdpVzENQ')
def verify():
    return 'gLguitC8-PJzAcAHOGHvlK_q_71gSJQQcB_xdpVzENQ.jjDWwuoR6VaOPJCS3RY3gQwgiU77PLzwzYN8i2Os4Zs'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)
