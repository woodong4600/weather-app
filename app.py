import streamlit as st
import requests
import pandas as pd
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="Global Weather", layout="wide")

API_KEY = st.secrets["WEATHER_API_KEY"]

st.title("Global Weather")

# =========================
# 🔹 Sidebar Search
# =========================
st.sidebar.header("Search")

city_input = st.sidebar.text_input("Enter city name (English only)")
gps_button = st.sidebar.button("Use My Location (GPS)")

st.sidebar.markdown("### Popular Cities")
popular_city = st.sidebar.selectbox(
    "Quick Select",
    ["", "Seoul", "Busan", "Tokyo", "New York", "London", "Paris"]
)

selected_location = None

# =========================
# GPS
# =========================
if gps_button:
    location = get_geolocation()
    lat = location["coords"]["latitude"]
    lon = location["coords"]["longitude"]
    selected_location = f"{lat},{lon}"

# Popular city override
if popular_city:
    city_input = popular_city

# =========================
# 🔹 Instant Auto Complete
# =========================
if not gps_button and city_input:

    search_url = f"http://api.weatherapi.com/v1/search.json?key={API_KEY}&q={city_input}"
    search_response = requests.get(search_url)
    search_data = search_response.json()

    if len(search_data) > 0:

        options = []
        for item in search_data:
            label = f"{item['name']}, {item['region']}, {item['country']}"
            value = f"{item['lat']},{item['lon']}"
            options.append((label, value))

        selected_label = st.sidebar.selectbox(
            "Select Location",
            [o[0] for o in options]
        )

        for o in options:
            if o[0] == selected_label:
                selected_location = o[1]

# =========================
# 🔹 Weather Data
# =========================
if selected_location:

    weather_url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={selected_location}&days=1&aqi=yes"
    response = requests.get(weather_url)
    data = response.json()

    location_name = data["location"]["name"]
    country = data["location"]["country"]
    lat = data["location"]["lat"]
    lon = data["location"]["lon"]

    temp = data["current"]["temp_c"]
    condition = data["current"]["condition"]["text"]
    humidity = data["current"]["humidity"]
    feelslike = data["current"]["feelslike_c"]
    uv = data["current"]["uv"]
    aqi = data["current"]["air_quality"]["pm2_5"]

    sunrise = data["forecast"]["forecastday"][0]["astro"]["sunrise"]
    sunset = data["forecast"]["forecastday"][0]["astro"]["sunset"]
    moon_phase = data["forecast"]["forecastday"][0]["astro"]["moon_phase"]

    col1, col2 = st.columns([2, 1])

    # =========================
    # Main Weather Section
    # =========================
    with col1:
        st.header(f"{location_name}, {country}")
        st.subheader(f"{temp}°C")
        st.write(condition)

        if temp >= 30:
            st.warning("Too Hot!")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Humidity", f"{humidity}%")
        with c2:
            st.metric("Feels Like", f"{feelslike}°C")
        with c3:
            st.metric("UV Index", uv)

        st.markdown("---")
        st.write("Air Quality (PM2.5):", f"{aqi} μg/m³")
        st.write("Sunrise:", sunrise)
        st.write("Sunset:", sunset)
        st.write("Moon Phase:", moon_phase)

        # =========================
        # Hourly Graph
        # =========================
        st.subheader("Hourly Temperature")

        hours = data["forecast"]["forecastday"][0]["hour"]

        hour_list = []
        temp_list = []

        for h in hours:
            hour_list.append(h["time"].split(" ")[1])
            temp_list.append(h["temp_c"])

        df = pd.DataFrame({
            "Time": hour_list,
            "Temperature": temp_list
        }).set_index("Time")

        st.line_chart(df)

        # =========================
        # Recommendation Section
        # =========================
        st.markdown("---")
        st.subheader("Recommendations")

        if temp >= 30:
            st.write("Clothes: T-shirt, Shorts")
            st.write("Items: Sunscreen, Water")
            st.write("Activity: Indoor workout or swimming")
        elif temp >= 20:
            st.write("Clothes: Light long sleeves")
            st.write("Items: Sunglasses")
            st.write("Activity: Running, Cycling")
        elif temp >= 10:
            st.write("Clothes: Jacket")
            st.write("Items: Light outerwear")
            st.write("Activity: Walking")
        else:
            st.write("Clothes: Heavy coat")
            st.write("Items: Gloves, Scarf")
            st.write("Activity: Indoor yoga")

        if "rain" in condition.lower():
            st.write("Bring an umbrella.")
        if uv >= 7:
            st.write("Use sunscreen.")

    # =========================
    # Naver Map
    # =========================
    with col2:
        st.subheader("Map")

        map_url = f"https://map.naver.com/v5/search/{location_name}"
        iframe = f"""
        <iframe src="{map_url}"
        width="100%" height="500"
        style="border:none;"></iframe>
        """
        st.components.v1.html(iframe, height=500)