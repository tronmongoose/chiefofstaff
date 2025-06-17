# Tools/functions for agent to call
import os
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
print(f"Debug - OpenWeather API Key loaded: {'Yes' if OPENWEATHER_API_KEY else 'No'}")

@tool
def get_weather(location: str) -> str:
    """
    Call this tool whenever the user asks for weather, forecast, temperature, or climate.
    """
    if not OPENWEATHER_API_KEY:
        return "Weather API key not set."

    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=imperial"
    response = requests.get(url)
    
    if response.status_code != 200:
        return f"Failed to get weather for {location}."

    data = response.json()
    temp = data['main']['temp']
    description = data['weather'][0]['description']
    return f"The weather in {location} is {temp}°F with {description}."

@tool
def get_todo_list() -> str:
    """
    Returns Erik's current todo list.
    """
    return "Erik Huckle's todo list:\n1) Build AI agent\n2) Test LangGraph\n3) Celebrate progress"

# Collect tools into list for function calling
TOOLS = [get_weather, get_todo_list]