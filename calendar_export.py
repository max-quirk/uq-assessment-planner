#!/usr/bin/python3.4
from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from datetime import timedelta 

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'

def calExport(course, assessment_name, weighting, learning_obj, due_date):
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    print('starting export function')
    title = "%s - %s" % (course, assessment_name)
    description = 'Weighting: %s \n Learning objectives: %s' % (weighting, learning_obj)
    end = due_date + + timedelta(hours=1)
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
    print('failed here')
    store = file.Storage('token.json')
    print('no it didnt')
    creds = store.get()
    print('no it didnt')
    if not creds or creds.invalid:
        print('no it didnt')
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        print('no it didnt')
        creds = tools.run_flow(flow, store)
        print('no it didnt')
    
    print('no it didntX')
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    print('no it didntX')
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('no it didntX')
    print('event added')
