import os
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow


app = Flask(__name__)

# Replace with your own Google Calendar API credentials
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = '../timemate-408921-036bf6bcf7d4.json'
# Set the redirect URI for Google's OAuth callback
REDIRECT_URI = 'http://localhost:5000/oauth2callback'

calendar_service = build('calendar', 'v3', credentials=service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES))
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return 'Welcome to Rocketbrew Calendar Integration -- TimeMate!'

@app.route('/integrate-google-calendar', methods=['POST'])
def integrate_google_calendar():
    # Handle Google Calendar integration logic here
    # Redirect the user to Google's authorization URL and handle the callback

    # Assume the integration is successful
    return jsonify({"message": "Google Calendar integration successful"}), 200

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
# @app.route('/authorize')
# def authorize():
#     flow = InstalledAppFlow.from_client_secrets_file(
#         SERVICE_ACCOUNT_FILE, SCOPES, redirect_uri=REDIRECT_URI
#     )
#     authorization_url, state = flow.authorization_url(
#         access_type='offline', prompt='consent'
#     )
#     session['oauth_state'] = state
#     return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    # state = session['oauth_state']
    # flow = InstalledAppFlow.from_client_secrets_file(
    #     SERVICE_ACCOUNT_FILE, SCOPES, state=state, redirect_uri=REDIRECT_URI
    # )
    # flow.fetch_token(authorization_response=request.url)
    #
    # using the service account, consider change to 2factor Oauth
    events = calendar_service.events().list(calendarId='primary', maxResults=10).execute()

    return jsonify(events)
if __name__ == '__main__':
    app.run(debug=True)
