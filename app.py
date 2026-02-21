import streamlit as st
import requests
import pandas as pd
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="전 세계 날씨", layout="wide")

API_KEY = st.secrets["WEATHER_API_KEY"]

# -------------------------
# 세션 초기화
# -------------------------
if "selected_location" not in st.session_state:
    st.session_state.selected_location = None

if "search_trigger" not in st.session_state:
    st.session_state.search_trigger = 0

st.title("전 세계 날씨 앱")

# -------------------------
# 사이드바
# -------------------------
st.sidebar.header("검색")

city_input = st.sidebar.text_input("도시 이름 입력 (영어)")
search_button = st.sidebar.button("검색")
gps_button = st.sidebar.button("내 위치 사용")

st.sidebar.markdown("### 빠른 검색")

popular_cities = [
    "Seoul","Busan","Tokyo","London","Paris",
    "New York","Los Angeles","Singapore","Bangkok","Dubai"
]

quick_city = st.sidebar.selectbox("도시 선택", [""] + popular_cities)

# -------------------------
# 빠른 검색 선택 시 → 검색창 값만 변경
# -------------------------
if quick_city:
    city_input = quick_city

# -------------------------
# GPS 버튼
# -------------------------
if gps_button:
    st.session_state.selected_location = None
    loc = get_geolocation()
    if loc:
        lat = loc["coords"]["latitude"]
        lon = loc["coords"]["longitude"]
        st.session_state.selected_location = f"{lat},{lon}"

# -------------------------
# 검색 버튼 눌렀을 때만 실행
# -------------------------
if search_button and city_input:
    st.session_state.selected_location = None

    search_url = f"http://api.weatherapi.com/v1/search.json?key={API_KEY}&q={city_input}"
    search_response = requests.get(search_url)
    search_data = search_response.json()

    if len(search_data) > 0:
        st.session_state.selected_location = search_data[0]["name"]

# -------------------------
# 날씨 표시
# -------------------------
if st.session_state.selected_location:

    weather_url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={st.session_state.selected_location}&days=1&aqi=yes&lang=ko"
    response = requests.get(weather_url)
    data = response.json()

    location_name = data["location"]["name"]
    country = data["location"]["country"]

    temp = data["current"]["temp_c"]
    condition = data["current"]["condition"]["text"]
    humidity = data["current"]["humidity"]
    feelslike = data["current"]["feelslike_c"]
    uv = data["current"]["uv"]
    aqi = data["current"]["air_quality"]["pm2_5"]

    sunrise = data["forecast"]["forecastday"][0]["astro"]["sunrise"]
    sunset = data["forecast"]["forecastday"][0]["astro"]["sunset"]
    moon_phase = data["forecast"]["forecastday"][0]["astro"]["moon_phase"]

    # 날씨 아이콘
    icon = ""
    if "맑음" in condition:
        icon = "☀️"
    elif "비" in condition:
        icon = "☔"
    elif "눈" in condition:
        icon = "☃️"

    col1, col2 = st.columns([2,1])

    with col1:
        st.header(f"{location_name}, {country}")
        st.subheader(f"{temp}°C {icon}")
        st.write(condition)

        if temp >= 30:
            st.warning("너무 더워요!")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("습도", f"{humidity}%")
        with c2:
            st.metric("체감 온도", f"{feelslike}°C")
        with c3:
            st.metric("자외선 지수", uv)

        st.markdown("---")
        st.write("대기질(PM2.5):", f"{aqi} μg/m³")
        st.write("일출:", sunrise)
        st.write("일몰:", sunset)
        st.write("달 모양:", moon_phase)

        # 시간별 그래프
        st.subheader("시간별 기온")

        hours = data["forecast"]["forecastday"][0]["hour"]

        hour_list = []
        temp_list = []

        for h in hours:
            hour_list.append(h["time"].split(" ")[1])
            temp_list.append(h["temp_c"])

        df = pd.DataFrame({
            "시간": hour_list,
            "기온": temp_list
        }).set_index("시간")

        st.line_chart(df)

        st.markdown("---")
        st.subheader("추천 정보")

        if temp >= 30:
            st.write("옷차림: 반팔, 반바지")
            st.write("소지품: 선크림, 물")
            st.write("추천 운동: 실내 운동")
        elif temp >= 20:
            st.write("옷차림: 얇은 긴팔")
            st.write("추천 운동: 러닝")
        elif temp >= 10:
            st.write("옷차림: 자켓")
            st.write("추천 운동: 산책")
        else:
            st.write("옷차림: 두꺼운 코트")
            st.write("추천 운동: 실내 요가")

    with col2:
        st.subheader("지도")

        map_url = f"https://map.naver.com/v5/search/{location_name}"
        iframe = f"""
        <iframe src="{map_url}"
        width="100%" height="500"
        style="border:none;"></iframe>
        """
        st.components.v1.html(iframe, height=500)
