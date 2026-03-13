import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import folium
from streamlit_folium import st_folium
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()

retry = Retry(total=3, backoff_factor=1)

adapter = HTTPAdapter(max_retries=retry)

session.mount("https://", adapter)


# st.title("Click on map to select location")

# m = folium.Map(location=[-1.2921, 36.8219], zoom_start=5)

# map_data = st_folium(m, height=200, width=300)

# if map_data["last_clicked"]:
#     LAT = map_data["last_clicked"]["lat"]
#     LON = map_data["last_clicked"]["lng"]

# st.title("Enter Location Coordinates")

# col1, col2 = st.columns(2)

# with col1:
#     LAT = st.number_input(
#         "Latitude",
#         min_value=-90.0,
#         max_value=90.0,
#         value=-1.2921,
#         format="%.6f"
#     )

# with col2:
#     LON = st.number_input(
#         "Longitude",
#         min_value=-180.0,
#         max_value=180.0,
#         value=36.8219,
#         format="%.6f"
#     )

#st.write("Selected coordinates:")
# st.write("Latitude:", latitude)
# st.write("Longitude:", longitude)

#exit()
# Nairobi coordinates
#LAT = -1.280702
#LON = 36.946810
#-------------

st.set_page_config(layout="wide")

st.title("""Pick a location by name search,entering coordinates or pick from the map""")

# -------------------------
# Session state defaults
# -------------------------
if "lat" not in st.session_state:
    st.session_state.lat = -1.2921
if "lon" not in st.session_state:
    st.session_state.lon = 36.8219


# -------------------------
# Search place
# -------------------------
st.subheader("Search for a place")

place = st.text_input("Enter place name")

if st.button("Search"):

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": place,
        "format": "json"
    }

    headers = {
        "User-Agent": "streamlit-location-app"
    }

    response = session.get(url, params=params, headers=headers)

    if response.status_code == 200:

        data = response.json()

        if len(data) > 0:

            st.session_state.lat = float(data[0]["lat"])
            st.session_state.lon = float(data[0]["lon"])

            st.success("Location found")
            st.write("Latitude:", st.session_state.lat)
            st.write("Longitude:", st.session_state.lon)

        else:
            st.warning("No location found")

    else:
        st.error(f"API error: {response.status_code}")

#st.session_state.lat = lat
#st.session_state.lon = lon
# -------------------------
# Manual coordinate input
# -------------------------
st.subheader("Enter coordinates manually")

col1, col2 = st.columns(2)

with col1:
    lat = st.number_input(
        "Latitude",
        min_value=-90.0,
        max_value=90.0,
        value=st.session_state.lat,
        format="%.6f"
    )

with col2:
    lon = st.number_input(
        "Longitude",
        min_value=-180.0,
        max_value=180.0,
        value=st.session_state.lon,
        format="%.6f"
    )

st.session_state.lat = lat
st.session_state.lon = lon


# -------------------------
# Map display
# -------------------------
st.subheader("Click on the map")

m = folium.Map(
    location=[st.session_state.lat, st.session_state.lon],
    zoom_start=12
)

folium.Marker(
    [st.session_state.lat, st.session_state.lon],
    tooltip="Selected location"
).add_to(m)

map_data = st_folium(m, height=200, width=800)

if map_data["last_clicked"]:
    st.session_state.lat = map_data["last_clicked"]["lat"]
    st.session_state.lon = map_data["last_clicked"]["lng"]


# -------------------------
# Final output
# -------------------------
#st.subheader("Selected Coordinates")

#st.write("Latitude:", st.session_state.lat)
#st.write("Longitude:", st.session_state.lon)
#----------------function
@st.cache_data
def get_place_name(lat, lon):

    url = "https://nominatim.openstreetmap.org/reverse"

    params = {
        "lat": lat,
        "lon": lon,
        "format": "json"
    }

    headers = {
        "User-Agent": "streamlit-location-app"
    }

    response = session.get(url, params=params, headers=headers, timeout=10)

    if response.status_code == 200:
        data = response.json()
        return data.get("display_name", "Unknown location")

    return "Location not found"

st.divider()

st.subheader("Selected Location")

lat = st.session_state.lat
lon = st.session_state.lon

place_name = get_place_name(lat, lon)

st.success(f"📍 {place_name}")

col1, col2 = st.columns(2)

with col1:
    st.metric("Latitude", f"{lat:.6f}")

with col2:
    st.metric("Longitude", f"{lon:.6f}")
#---------------

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": lat,
    "longitude": lon,

    # Hourly data
    "hourly": (
        "temperature_2m,"
        "relative_humidity_2m,"
        "precipitation,"
        "rain,"
        "windspeed_10m,"
        "cloudcover,"
        "weathercode"
    ),

    # Daily summaries
    "daily": (
        "weathercode,"
        "temperature_2m_max,"
        "temperature_2m_min,"
        "precipitation_sum"
    ),

    # Next 7 days
    "forecast_days": 7,

    # Local timezone
    "timezone": "Africa/Nairobi"
}

response = session.get(url, params=params,verify = False)
response.raise_for_status()
data = response.json()

daily_df = pd.DataFrame(data["daily"])
daily_df["time"] = pd.to_datetime(daily_df["time"])

#daily_df

WEATHER_CODE_MAP = {
    0: "Clear sky",

    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",

    45: "Fog",
    48: "Depositing rime fog",

    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",

    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",

    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",

    66: "Light freezing rain",
    67: "Heavy freezing rain",

    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",

    77: "Snow grains",

    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",

    85: "Slight snow showers",
    86: "Heavy snow showers",

    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

WEATHER_CODE_EMOJI = {
    0:  "☀️ Clear sky",

    1:  "🌤️ Mainly clear",
    2:  "⛅ Partly cloudy",
    3:  "☁️ Overcast",

    45: "🌫️ Fog",
    48: "🌫️ Rime fog",

    51: "🌦️ Light drizzle",
    53: "🌦️ Moderate drizzle",
    55: "🌧️ Dense drizzle",

    56: "🧊🌦️ Freezing drizzle",
    57: "🧊🌧️ Dense freezing drizzle",

    61: "🌧️ Light rain",
    63: "🌧️ Moderate rain",
    65: "🌧️ Heavy rain",

    66: "🧊🌧️ Freezing rain",
    67: "🧊🌧️ Heavy freezing rain",

    71: "🌨️ Light snow",
    73: "🌨️ Moderate snow",
    75: "❄️ Heavy snow",

    77: "❄️ Snow grains",

    80: "🌦️ Rain showers",
    81: "🌧️ Heavy rain showers",
    82: "⛈️ Violent rain showers",

    85: "🌨️ Snow showers",
    86: "❄️ Heavy snow showers",

    95: "⛈️ Thunderstorm",
    96: "⛈️ Thunderstorm + hail",
    99: "⛈️ Severe thunderstorm + hail"
}

daily_df["weather_description"] = (
    daily_df["weathercode"]
    .map(WEATHER_CODE_MAP)
    .fillna("Unknown")
)

daily_df["weather_emoji"] = (
    daily_df["weathercode"]
    .map(WEATHER_CODE_EMOJI)
    .fillna("🌡️ Unknown")
)

wf= daily_df[[
    "time",
    #"weather_description",
    "weather_emoji",
    "temperature_2m_min",
    "temperature_2m_max",
    "precipitation_sum"
]]
wf= wf.rename(columns = {"time":"Id_date","weather_emoji":"Description","temperature_2m_min":"Min_Temp","temperature_2m_max":"Max_Temp","precipitation_sum":"Precipitation"}
         )

wf


#,"weather_description":"Description"