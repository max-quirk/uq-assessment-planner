import os
from datetime import timedelta
import json

import flask
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask.cli import with_appcontext
import pandas as pd
import dateparser
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import json

from database import Db
from logger import get_logger
import settings
import util

_LOG = get_logger("app")


app = Flask(__name__)
app.debug = True
app.secret_key = settings.APP_SECRET
PORT = int(settings.PORT)


def get_db():
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(flask.g, "db"):
        flask.g.db = Db()
        flask.g.db.connect(settings.DATABASE_URL)

    return flask.g.db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(flask.g, "db"):
        flask.g.db.close()


def getProfileID(course_code):
    query = """
    SELECT course_profile_id FROM course WHERE course_code = %s
    """
    profileID = get_db().select(query, data=(course_code.upper(),))
    if profileID:
        return profileID[0][0]


def getAssessments(profileID, course_code):
    query = """
            SELECT assessment_name, due_date, weighting, learning_obj 
            FROM course_assessment
            WHERE course_code = %s
            """
    unformatted_assessments = get_db().select(query, data=(course_code.upper(),))
    if not unformatted_assessments:
        return None

    assessments = []

    for i, _ in enumerate(unformatted_assessments):
        name = unformatted_assessments[i][0]
        due_date = unformatted_assessments[i][1]
        weighting = unformatted_assessments[i][2]
        learning_obj = unformatted_assessments[i][3]

        assessment = {
            "course_code": course_code,
            "name": name,
            "due_date": due_date,
            "weighting": weighting,
            "learning_obj": learning_obj,
        }

        assessments.append(assessment)
    return assessments


@app.route("/", methods=["GET", "POST"])
def hello():
    if request.method == "GET":
        return render_template("title.html")

    course_1 = request.form.get("course-1")
    course_2 = request.form.get("course-2")
    course_3 = request.form.get("course-3")
    course_4 = request.form.get("course-4")
    course_5 = request.form.get("course-5")
    all_courses = []
    if course_1 is not None and course_1 != "":
        all_courses.append(course_1)
    if course_2 is not None and course_2 != "":
        all_courses.append(course_2)
    if course_3 is not None and course_3 != "":
        all_courses.append(course_3)
    if course_4 is not None and course_4 != "":
        all_courses.append(course_4)
    if course_5 is not None and course_5 != "":
        all_courses.append(course_5)

    all_course_assessment = []
    for course_code in all_courses:
        profileID = getProfileID(course_code)
        if profileID == 0:
            error_message = '<p style="color: red">Error: One of the courses you entered was invalid. Please try again</p>'
            all_courses = []
            return render_template("title.html", error_message=error_message)

        assessments = getAssessments(profileID, course_code)
        if assessments:
            all_course_assessment.append(assessments)

    by_course_as_html = util.makeHTML(all_course_assessment)
    chronological_html = util.makeChronologicalHTML(all_course_assessment)

    return render_template(
        "citation.html",
        by_course_as_html=by_course_as_html,
        chronological_html=chronological_html,
        state={"assessments": all_course_assessment},
    )


@app.route("/export", methods=["POST"])
def export():
    if "credentials" not in flask.session:
        _LOG.debug("credentials not in session. Requesting access to Google...")
        return jsonify({"redirect_url": flask.url_for("authorize", _external=True)})

    _LOG.debug("using credentials")
    credentials = google.oauth2.credentials.Credentials(**flask.session["credentials"])
    _LOG.debug(f"got credentials: {flask.session['credentials']}")
    calendar = googleapiclient.discovery.build(
        settings.GOOGLE_API_CALENDAR_SERVICE,
        settings.GOOGLE_API_VERSION,
        credentials=credentials,
    )
    _LOG.debug(f"got calendar: {calendar}")
    if not request.get_json():
        flask.abort(400)
    all_course_assessment = request.get_json()
    _LOG.debug(f"got state: {all_course_assessment}")
    for course_assessments in all_course_assessment:
        print(course_assessments)
        for assessment in course_assessments:
            print(assessment)
            course = assessment["course_code"].upper()
            assessment_name = assessment["name"]
            weighting = assessment["weighting"]
            learning_obj = assessment["learning_obj"]
            due_date = util.formatDate(assessment["due_date"])

            if util.formatDate(assessment["due_date"]) != None:
                title = "%s - %s" % (course, assessment_name)
                description = "Weighting: %s \nLearning objectives: %s" % (
                    weighting,
                    learning_obj,
                )
                end = due_date + timedelta(hours=1)
                event = {
                    "summary": title,
                    "description": description,
                    "start": {
                        "dateTime": due_date.isoformat(),  #'2018-12-29T09:00:00-07:00',
                        "timeZone": "Australia/Brisbane",
                    },
                    "end": {
                        "dateTime": end.isoformat(),
                        "timeZone": "Australia/Brisbane",
                    },
                }

                util.calExport(calendar, event)

    return jsonify(
        {
            "success": True,
            "message": "Events were successfully added to Google Calendar",
        }
    )


@app.route("/authorize")
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        json.loads(settings.GOOGLE_OAUTH_CLIENT_ID), scopes=settings.SCOPES
    )
    flow.redirect_uri = flask.url_for("oauth2callback", _external=True)
    authorization_url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    return redirect(authorization_url)


@app.route("/oauth2callback")
def oauth2callback():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        json.loads(settings.GOOGLE_OAUTH_CLIENT_ID), scopes=settings.SCOPES
    )
    flow.redirect_uri = flask.url_for("oauth2callback", _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    flask.session["credentials"] = util.credentials_to_dict(credentials)

    return render_template("oauth2_success.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/.well-known/acme-challenge/gLguitC8-PJzAcAHOGHvlK_q_71gSJQQcB_xdpVzENQ")
def verify():
    return "gLguitC8-PJzAcAHOGHvlK_q_71gSJQQcB_xdpVzENQ.jjDWwuoR6VaOPJCS3RY3gQwgiU77PLzwzYN8i2Os4Zs"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

