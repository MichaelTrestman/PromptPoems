# Import required libraries
import yaml
import os
import openai
from prompt_poet import Prompt
from functions import safe_get_data, get_weather, get_traffic_data, get_aqi, get_calendar_events, extract_weather_info, extract_traffic_info, extract_aqi_info, extract_events_info
import googlemaps
from langchain_openai import ChatOpenAI

# Set up API keys and Google API credentials
openai.api_key = os.environ['OPENAI_API_KEY']
openweathermap_api_key = os.environ['OPENWEATHERMAP_API_KEY']
google_api_key = os.environ['GOOGLE_API_KEY']
aqi_api_key = os.environ['AQI_API_KEY']
google_calendar_credentials_file = "credentials.json"

# Initialize Google Maps client
gmaps = googlemaps.Client(key=google_api_key)

# Load and combine YAML files
with open('raw_template.yaml', 'r') as file:
    raw_template_yaml = yaml.safe_load(file)

with open('few_shot_examples.yaml', 'r') as file:
    few_shot_examples_yaml = yaml.safe_load(file)

combined_yaml = raw_template_yaml + few_shot_examples_yaml

# Get user's location and data
user_city = input("Enter your city: ")
user_country = input("Enter your country (2-letter country code): ")
location = f"{user_city}, {user_country}"

user_weather = safe_get_data(get_weather, user_city, user_country, openweathermap_api_key)
user_traffic = safe_get_data(get_traffic_data, location, gmaps)
user_aqi = safe_get_data(get_aqi, location, gmaps)
calendar_events = safe_get_data(get_calendar_events, google_calendar_credentials_file)

user_weather_info = extract_weather_info(user_weather)
traffic_info = extract_traffic_info(user_traffic)
aqi_info = extract_aqi_info(user_aqi)
events_info = extract_events_info(calendar_events)

# Template data
template_data = {
    "user_city": user_city,
    "user_country": user_country,
    "user_temperature": user_weather_info["temperature"],
    "user_description": user_weather_info["description"],
    "traffic_status": traffic_info,
    "aqi": aqi_info["aqi"],
    "main_pollutant": aqi_info["main_pollutant"],
    "events": events_info
}
print(template_data)
print("``````")
# Create the prompt using Prompt Poet
prompt = Prompt(
    raw_template=yaml.dump(combined_yaml),
    template_data=template_data
)
model = ChatOpenAI(model="gpt-4o-mini")
response = model.invoke(prompt.messages)
print(response)
print("0000000000")
# Extract and print the response
response = model.choices[0].message["content"]
print(response)
