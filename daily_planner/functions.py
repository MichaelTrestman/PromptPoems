# Import required libraries
import requests
import googlemaps
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI

# Function to get weather data
def get_weather(city, country, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data

# Function to get traffic data
def get_traffic_data(location, gmaps_client):
    traffic_info = gmaps_client.directions(
        origin=location,
        destination=location,
        mode="driving",
        departure_time=datetime.now()
    )
    
    if traffic_info:
        traffic_warnings = traffic_info[0]['warnings']
        return traffic_warnings
    return "No traffic information available"

# Function to get AQI data
def get_aqi(city, country, api_key):
    url = f"http://api.airvisual.com/v2/city?city={city}&state=Oregon&country={country}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    return data['data']['current']['pollution']

# Function to get Google Calendar events
def get_calendar_events(credentials_file, days=7):
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)

    now = datetime.utcnow().isoformat() + 'Z'
    end_time = (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'

    events_result = service.events().list(calendarId='primary', timeMin=now, timeMax=end_time, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events

# Functions to extract relevant information
def extract_weather_info(weather_data):
    try:
        temperature = weather_data['main']['temp']
        description = weather_data['weather'][0]['description']
        return {
            "temperature": temperature,
            "description": description
        }
    except:
        return {
            "temperature": "data not available",
            "description": "data not available"
        }
    

def extract_traffic_info(traffic_data):
    return traffic_data

def extract_aqi_info(aqi_data):
    try:
        aqi = aqi_data['aqius']
        main_pollutant = aqi_data['mainus']
        return {
            "aqi": aqi,
            "main_pollutant": main_pollutant
        }
    except:
        return {
            "aqi": "data not available",
            "main_pollutant": "data not available"
        }

def extract_events_info(events):
    events_info = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event['summary']
        events_info.append({"start": start, "summary": summary})
    return events_info

def safe_get_data(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return ""
