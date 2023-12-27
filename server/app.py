import os
from flask import Flask, request, jsonify, session, redirect, url_for, render_template, render_template_string 
import spacy
import json
from datetime import datetime, timedelta
from parsedatetime import Calendar
from dateutil import parser, tz
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime
from dateutil import parser
import traceback




app = Flask(__name__)

# Replace with your own Google Calendar API credentials
SCOPES = ['https://www.googleapis.com/auth/calendar']
# Set the redirect URI for Google's OAuth callback
REDIRECT_URI = 'https://127.0.0.1:5000/oauth2callback'

app.secret_key = os.urandom(24)
# load spacy nlp model
nlp = spacy.load("en_core_web_sm")
# Create a Google Calendar API service
credentials = None

def create_google_calendar_service(credentials):
    return build('calendar', 'v3', credentials=credentials)

@app.route('/')
def index():
    return 'Welcome to Rocketbrew Calendar Integration -- TimeMate!'

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
        # Print the stack trace
        traceback.print_exc()
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
        creds = Credentials.from_authorized_user_info(
            json.loads(credentials_json), SCOPES
        )
         # Parse dates using spaCy
        parsed_date = extract_dates_with_spacy(user_text_input)
        parsed_time = extract_times_with_spacy(user_text_input)

        # Build the Calendar service using the obtained credentials
        calendar_service = build('calendar', 'v3', credentials=creds )
           # Parse the user input date to a datetime object
        # Create calendar events for parsed dates

        # Retrieve the user's timezone
        user_timezone = request.form.get('user_timezone')
        # for date_str in parsed_dates:
        create_calendar_event(calendar_service, parsed_date, parsed_time, "Meeting", "Powered by TimeMate", user_timezone)
        success_message = "Additional information processed and event created successfully!"
        return render_template('additional_info_form.html', success_message=success_message)
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return render_template('additional_info_form.html', error_message=error_message), 400
def create_calendar_event(calendar_service, extracted_date, extracted_time, summary, description, user_timezone):

    # import ipdb; ipdb.set_trace()

    parsed_date = None
    if extracted_date:
        parsed_date = parse_relative_date(extracted_date)
    if not parsed_date:
        print("No valid date found")
        return jsonify({"error": "No valid date found"}), 400

    parsed_time = None
    if extracted_time:
        parsed_time = parse_relative_time(extracted_time)
    if not parsed_time:
        print("No valid time found")
        return jsonify({"error": "No valid time found"}), 400

    # Set the timezone to the user's local timezone
    local_timezone = tz.gettz(user_timezone)

    # Convert the parsed date and time to the user's local timezone
    parsed_datetime_local = datetime(
        parsed_date.year,
        parsed_date.month,
        parsed_date.day,
        parsed_time.hour,
        parsed_time.minute,
        tzinfo=local_timezone
    )

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": parsed_datetime_local.isoformat(),
            "timeZone": user_timezone,
        },
        "end": {
            "dateTime": (parsed_datetime_local + timedelta(hours=1)).isoformat(),
            "timeZone": user_timezone,
        },
    }

    # Insert the event into the primary calendar
    calendar_service.events().insert(calendarId="primary", body=event).execute()

def extract_dates_with_spacy(user_input):
    # import ipdb; ipdb.set_trace()
    doc = nlp(user_input)
    
    # Extract entities recognized as dates
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    if dates:
        # Assuming the first date found is the most relevant
        return dates[0]
    else:
        return None


def extract_times_with_spacy(user_input):
    doc = nlp(user_input)
    
    # Extract entities recognized as times
    times = [ent.text for ent in doc.ents if ent.label_ == "TIME"]
    
    if times:
        # Assuming the first time found is the most relevant
        return times[0]
    else:
        return None

def parse_relative_date(date_text):
    if date_text is None:
        return None
    cal = Calendar()
    parsed_result, success = cal.parseDT(date_text)
    
    if success:
        return parsed_result
    else:
        return None

def parse_relative_time(time_text):
    
     # Calculate the time of the next rounded hour
    next_round_hour = (datetime.min + timedelta(hours=(datetime.now().hour + 1))).time()

    if time_text is None:
        return next_round_hour

    try:
        # Parse the time using dateutil.parser
        parsed_time = parser.parse(time_text).time()
        return parsed_time

    except ValueError:
        # Return the next rounded hour if parsing fails
        return next_round_hour
if __name__ == '__main__':
    app.run(ssl_context = 'adhoc', debug=True)
