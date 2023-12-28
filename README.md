
# TimeMate - Schedule Meetings with Ease

TimeMate is a web application that simplifies the process of scheduling meetings on Google Calendar. It leverages natural language processing to interpret user input and create calendar events seamlessly.

## Features

### 1. Schedule Meetings Easily

TimeMate allows users to schedule meetings effortlessly by providing a natural language interface. Users can input meeting details, such as date, time, and event description, using everyday language.

### 2. Google Calendar Integration

The application seamlessly integrates with Google Calendar, enabling users to schedule and manage events directly from the TimeMate interface.

### 3. Natural Language Processing

TimeMate uses spaCy, a natural language processing library, to extract meaningful information from user input. This makes the scheduling process intuitive and user-friendly.

### 4. Timezone Support

Users can specify their timezone, ensuring that scheduled events are accurate and aligned with their local time.

### 5. OAuth2 Authentication

TimeMate employs OAuth2 authentication to securely connect with Google Calendar. Users can authorize the application to access their calendar data, allowing for a personalized scheduling experience.

### 6. Responsive Web Design

The application features a responsive design, making it accessible and user-friendly across various devices, including desktops, tablets, and smartphones.

## Getting Started

### Prerequisites

- Python 3.x
- Flask
- spaCy
- Google Calendar API credentials

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/TimeMate.git
    cd TimeMate
    ```

2. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up Google Calendar API credentials:**

   - Visit the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project and enable the Google Calendar API.
   - Download the credentials JSON file and save it as `client_secret_web.json` in the project directory.

4. **Set the Flask app:**

    ```bash
    export FLASK_APP=app.py
    ```

5. **Run the app:**

    ```bash
    flask run
    ```

6. **Open the app in your web browser at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).**
