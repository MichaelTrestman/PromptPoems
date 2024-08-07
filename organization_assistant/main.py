# Import required libraries
import yaml
import openai
from prompt_poet import Prompt
from functions import get_weather, get_traffic_data, get_aqi, get_calendar_events, extract_weather_info, extract_traffic_info, extract_aqi_info, extract_events_info
import googlemaps

# Set up API keys
OPENWEATHERMAP_API_KEY = "your_openweathermap_api_key"
GOOGLE_API_KEY = "your_google_api_key"
AQI_API_KEY = "your_aqi_api_key"
GOOGLE_CALENDAR_CREDENTIALS_FILE = "path_to_your_service_account_credentials.json"

# Initialize Google Maps client
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

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

user_weather = get_weather(user_city, user_country, OPENWEATHERMAP_API_KEY)
user_traffic = get_traffic_data(location, gmaps)
user_aqi = get_aqi(user_city, user_country, AQI_API_KEY)
calendar_events = get_calendar_events(GOOGLE_CALENDAR_CREDENTIALS_FILE)

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

# Create the prompt using Prompt Poet
prompt = Prompt(
    raw_template=yaml.dump(combined_yaml),
    template_data=template_data
)

# Set up OpenAI API key
openai.api_key = "your_openai_api_key"

# Get response from OpenAI
model = openai.ChatCompletion.create(
  model="gpt-4",
  messages=prompt.messages
)

# Extract and print the response
response = model.choices[0].message["content"]
print(response)
