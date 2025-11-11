import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Optional
import pytz
import requests
import json
from streamlit_javascript import st_javascript
from weather import geocode_city, get_forecast

st.set_page_config(page_title="Weather App", page_icon="⛅", layout="centered")

st.title("⛅ Weather App")
st.caption("Powered by Open-Meteo — no API key needed")

# Sidebar UI
with st.sidebar:
    st.header("Search Location 🌍")
    city = st.text_input("City", value="Bijnor")
    units = st.radio("Units", options=["metric", "imperial"], index=0, horizontal=True)
    search = st.button("Find Location 🔍")
    st.markdown("---")
    st.write("Or get weather for your **current location** ⬇️")
    use_current = st.button("📍 Use My Location")

# Session initialization
if 'selected' not in st.session_state:
    st.session_state.selected = None
if 'options' not in st.session_state:
    st.session_state.options = []

def format_option(opt: dict) -> str:
    parts = [opt.get("name", "")]
    admin1 = opt.get("admin1")
    country = opt.get("country")
    if admin1:
        parts.append(admin1)
    if country:
        parts.append(country)
    return ", ".join([p for p in parts if p])

# Function to fetch current location
def get_current_location():
    coords = st_javascript("""
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const coords = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                };
                window.streamlitAPI.setComponentValue(JSON.stringify(coords));
            },
            (error) => {
                window.streamlitAPI.setComponentValue(JSON.stringify({error: error.message}));
            }
        );
    """)
    if coords:
        try:
            loc = json.loads(coords)
            if "error" in loc:
                st.error(f"⚠️ {loc['error']}")
                return None, None
            else:
                return loc["latitude"], loc["longitude"]
        except Exception as e:
            st.error(f"Error parsing location: {e}")
    return None, None

# Logic: If user clicked Use My Location
if use_current:
    st.info("Fetching your current location... please allow permission in browser.")
    lat, lon = get_current_location()
    if lat and lon:
        st.success(f"📍 Current Location: {lat:.4f}, {lon:.4f}")
        selected = {"name": "Your Location", "latitude": lat, "longitude": lon, "country": ""}
    else:
        selected = None
else:
    # Manual city search
    if st.session_state.selected is None or search:
        matches = geocode_city(city)
        st.session_state.options = matches
        if matches:
            st.session_state.selected = matches[0]
        else:
            st.session_state.selected = None

    # If multiple results, allow pick
    if st.session_state.options:
        labels = [format_option(m) for m in st.session_state.options]
        idx = st.selectbox("Did you mean:", options=list(range(len(labels))), format_func=lambda i: labels[i])
        selected = st.session_state.options[idx]
    else:
        selected = None
        if not use_current:
            st.warning("No results found. Try another city.")

# Now fetch and display weather
if selected:
    lat = selected["latitude"]; lon = selected["longitude"]
    st.subheader(f"📍 {format_option(selected)}")
    st.write(f"**Coordinates:** {lat:.2f}, {lon:.2f}")

    data = get_forecast(lat, lon, units=units)

    # Current weather
    current = data.get("current_weather", {})
    if current:
        col1, col2, col3 = st.columns(3)
        col1.metric("Temperature", f"{current.get('temperature','?')}°")
        col2.metric("Wind", f"{current.get('windspeed','?')} {'km/h' if units=='metric' else 'mph'}")
        col3.metric("Condition Code", str(current.get("weathercode","—")))
        st.caption("Note: Weather codes follow the Open-Meteo WMO code table.")

    # Daily forecast (7 days)
    daily = data.get("daily", {})
    if daily and "time" in daily:
        st.markdown("### 7-Day Forecast")
        for i, date_str in enumerate(daily["time"]):
            tmax = daily["temperature_2m_max"][i]
            tmin = daily["temperature_2m_min"][i]
            prcp = daily.get("precipitation_sum", [None]*len(daily["time"]))[i]
            wind = daily.get("windspeed_10m_max", [None]*len(daily["time"]))[i]
            st.write(f"- **{date_str}**: High {tmax}°, Low {tmin}°, Precip {prcp} mm, Max Wind {wind} {'km/h' if units=='metric' else 'mph'}")

    # Hourly chart for next 24 hours
    hourly = data.get("hourly", {})
    if hourly and "time" in hourly:
        st.markdown("### Next 24 Hours — Temperature")
        times = hourly["time"]
        temps = hourly["temperature_2m"]
        start_idx = 0
        if current and "time" in current and current["time"] in times:
            start_idx = times.index(current["time"])
        end_idx = min(start_idx + 24, len(times))
        times_24 = times[start_idx:end_idx]
        temps_24 = temps[start_idx:end_idx]

        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(range(len(temps_24)), temps_24, marker="o")
        ax.set_xlabel("Hour")
        ax.set_ylabel(f"Temp (°{'C' if units=='metric' else 'F'})")
        hour_labels = [t.split("T")[-1][:5] for t in times_24]
        ax.set_xticks(range(len(hour_labels)))
        ax.set_xticklabels(hour_labels, rotation=45, ha="right")
        ax.grid(True, linestyle="--", alpha=0.4)
        st.pyplot(fig)

    st.markdown("---")
    st.caption("Made by Dikshit❤️")

