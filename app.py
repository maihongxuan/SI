from flask import Flask, render_template, request, redirect
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
import ssl

app = Flask(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

SERVICE_ACCOUNT_FILE = "D:\\sideq-445817-097811988485.json"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)


calendar_service = build('calendar', 'v3', credentials=credentials)
sheets_service = build('sheets', 'v4', credentials=credentials)
spreadsheet_id = '1pGdIvdIDGsR7x6YN_et2PMg5r0ikLDp2uZhiURjoOsY'
range_name = 'Sheet1!A1:D10'

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/list_events')
def list_events():
    try:
        events_result = calendar_service.events().list(
            calendarId='primary', maxResults=100, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])
    except Exception as e:
        print(f"Error fetching events: {e}")
        events = []

    event_list = []
    for i, event in enumerate(events):
        start_datetime = event.get('start', {}).get('dateTime', '')
        date = ''
        time = ''
        if start_datetime:
            start_obj = datetime.datetime.fromisoformat(start_datetime[:-1])
            date = start_obj.strftime('%Y-%m-%d')
            time = start_obj.strftime('%H:%M')

        event_info = {
            'id': event['id'],  # Store event ID for clickable rows
            'name': event.get('summary', 'No Title'),
            'datetime': f"{date} {time}",
            'description': event.get('description', 'No Description'),
            'order': i + 1
        }
        event_list.append(event_info)

    print("Events list prepared")  # Debug print
    return render_template('listEvents.html', events=event_list)

@app.route('/add_event', methods=['POST'])
def add_event():
    title = request.form['title']
    date = request.form['date']
    time = request.form['time']
    description = request.form['description']

    start_datetime = f"{date}T{time}:00"
    end_datetime = f"{date}T{time}:00"  # Modify this to have a different end time if needed

    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'Asia/Ho_Chi_Minh',
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'Asia/Ho_Chi_Minh',
        },
    }

    try:
        created_event = calendar_service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (created_event.get('htmlLink')))
        return render_template('addanEvent.html', event_link=created_event.get('htmlLink'))
    except Exception as e:
        print(f'An error occurred: {e}')
    return redirect('/')

@app.route('/event_details/<event_id>')
def event_details(event_id):
    try:
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
    except Exception as e:
        print(f'An error occurred: {e}')
        return redirect('/list_events')

    event_info = {
        'name': event.get('summary', 'No Title'),
        'datetime': event.get('start', {}).get('dateTime', 'No Date').replace('T', ' ').replace('Z', ''),
        'description': event.get('description', 'No Description')
    }
    return render_template('eventDetails.html', event=event_info)
@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

@app.route('/income')
def income():
    # Fetch data from Google Sheets
    sheet = sheets_service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    # Return the income template with the fetched data
    return render_template('income.html', data=values)

@app.route('/add_an_event')
def add_an_event():
    return render_template('addanEvent.html')


if __name__ == '__main__':
    app.run(debug=True)
