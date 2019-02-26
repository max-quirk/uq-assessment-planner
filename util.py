import dateparser
from logger import get_logger

_LOG = get_logger("util")


def formatDate(date):
    _LOG.debug("formatting date")
    # check if date contains no digits
    if not any(char.isdigit() for char in date):
        return None

    dates = date.split("-")
    if len(dates) > 1:
        date1 = dateparser.parse(dates[0])
        date2 = dateparser.parse(dates[1])
        if date1 and date2:
            if date1.date() == date2.date():
                date = dates[0]
                return dateparser.parse(date)
    date = dateparser.parse(date)
    return date


def splitName(name):  # Separates assessment type from assessment name
    _LOG.debug("splitting name")
    for index, letter in enumerate(name):
        try:
            if (
                letter.islower()
                and name[index + 1].isupper()
                or letter == ")"
                and name[index + 1].isupper()
            ):
                return name[index + 1 :]
        except IndexError:
            return name
    return name


def makeHTML(all_course_assessments):
    _LOG.debug("makeHTML")
    html = '<div class="row">'
    columns = len(all_course_assessments)

    for course in all_course_assessments:
        html += '<div class="column-%s">' % columns
        html += '<h2 class="course-code">' + course[0].get("course_code") + "</h2>"
        for assessment in course:
            html += (
                '<h4 class="assessment-name"><strong>'
                + assessment.get("name")
                + "</h4></strong>"
            )
            html += '<p class="due-date">' + assessment.get("due_date") + "</p>"
            html += '<p class="weighting">' + assessment.get("weighting") + "</p>"
        html += "</div>"
    html += "</div>"
    _LOG.debug("makeHTML end")
    return html


def makeChronologicalHTML(all_course_assessments):
    _LOG.debug("makeChronologicalHTML")
    formatable_assessments = []
    for course in all_course_assessments:
        for assessment in course:
            if formatDate(assessment.get("due_date")) != None:
                formatable_assessments.append(assessment)

    if not formatable_assessments:
        return ""

    formatable_assessments = sorted(
        formatable_assessments, key=lambda k: formatDate(k["due_date"])
    )
    html = ""
    for assessment in formatable_assessments:
        title = "%s - %s" % (
            assessment.get("course_code", "").upper(),
            assessment.get("name"),
        )
        html += "<tr>"
        html += "<td>%s</td>" % title
        html += "<td>%s</td>" % assessment.get("due_date")
        html += "<td>%s</td>" % assessment.get("weighting")
        html += "<td>%s</td>" % assessment.get("learning_obj")
        html += "</tr>"
    _LOG.debug("makeChronologicalHTML end")
    return html


def calExport(calendar, payload):
    _LOG.debug("exporting to calendar")
    calendar.events().insert(calendarId="primary", body=payload).execute()


def credentials_to_dict(credentials):
    print("creddys::", credentials)
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
