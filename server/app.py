import os
from flask import Flask, request, jsonify, session, redirect, url_for, render_template 
# from google.oauth2 import service_account, credentials
import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime
from dateutil import parser



app = Flask(__name__)

# Replace with your own Google Calendar API credentials
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = '../timemate-408921-036bf6bcf7d4.json'
# Set the redirect URI for Google's OAuth callback
REDIRECT_URI = 'https://127.0.0.1:5000/oauth2callback'

app.secret_key = os.urandom(24)

# Create a Google Calendar API service
credentials = None

def create_google_calendar_service(credentials):
    return build('calendar', 'v3', credentials=credentials)

@app.route('/')
def index():
    return 'Welcome to Rocketbrew Calendar Integration -- TimeMate!'


@app.route('/create-event', methods=['POST'])
def create_google_calendar_event():
    data = request.get_json()

    # Extract date and time information from the text input (you may need a more sophisticated parsing logic)
    date_string = data.get('date')
    parsed_date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

    # Create a Google Calendar event
    event = {
        'summary': 'Example Event',
        'description': 'Conversation transition to a call',
        'start': {
            'dateTime': parsed_date.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (parsed_date + timedelta(hours=1)).isoformat(),
            'timeZone': 'UTC',
        },
    }

    calendar_service.events().insert(calendarId='primary', body=event).execute()

    return jsonify(event)
    # return jsonify({"message": "Google Calendar event created successfully"}), 200
#
@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
        '../client_secret_web.json',
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline', prompt='consent'
    )
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    try:
        state = session['oauth_state']
        flow = Flow.from_client_secrets_file(
            '../client_secret_web.json',
            scopes=SCOPES,
            state=state,
            redirect_uri=REDIRECT_URI
        )
        flow.fetch_token(authorization_response=request.url)
        session['credentials'] = flow.credentials.to_json()

        return redirect(url_for('prompt_additional_info'))

    except Exception as e:
        return jsonify({"error": str(e)}), 400   

@app.route('/prompt-additional-info')
def prompt_additional_info():
    # Render a template for the user to provide additional information
    return render_template('additional_info_form.html')

# create calendar event based on user input

@app.route('/process-additional-info', methods=['POST'])
def process_additional_info():
    try:
        # Retrieve additional information from the form submission
        user_text_input = request.form.get('text_input')


        # Use the saved credentials from the session
        credentials_json = session.get('credentials')

        if not credentials_json:
            return jsonify({"error": "User credentials not found"}), 400
        # print(credentials)
        creds = Credentials.from_authorized_user_info(
            json.loads(credentials_json), SCOPES
        )
        # print(creds)
        # creds = create_credentials(credentials_json)
        # # Build the Calendar service using the obtained credentials
        calendar_service = build('calendar', 'v3', credentials=creds )
           # Parse the user input date to a datetime object
        start_datetime = datetime.strptime(user_text_input.strip(), '%Y-%m-%d')

        # Calculate end datetime by adding 30 minutes
        end_datetime = start_datetime + timedelta(minutes=30)

        # Set default values for summary and description
        summary = 'Default Event Summary'
        description = 'Default Event Description'

        # Create an event
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_datetime.isoformat(), 'timeZone': 'UTC'},
            'end': {'dateTime': end_datetime.isoformat(), 'timeZone': 'UTC'},
        }

        # Insert the event into the primary calendar
        calendar_service.events().insert(calendarId='primary', body=event).execute()

        return "Additional information processed and event created successfully!"

    except Exception as e:
        return jsonify({"error": str(e)}), 400
if __name__ == '__main__':
    app.run(ssl_context = 'adhoc', debug=True)
