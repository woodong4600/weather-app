import streamlit as st
import requests
import pandas as pd
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="전 세계 날씨", layout="wide")

API_KEY = st.secrets["WEATHER_API_KEY"]

st.title("전 세계 날씨")

# =========================
# 세션 상태
# =========================
if "selected_location" not in st.session_state:
    st.session_state.selected_location = None

# =========================
# 사이드바
# =========================
st.sidebar.header("검색")

city_input = st.sidebar.text_input("도시 이름 입력 (영어만)")
gps_button = st.sidebar.button("내 위치(GPS) 사용")

st.sidebar.markdown("### 인기 도시")
popular_city = st.sidebar.selectbox(
    "빠른 선택",
    ["", "Seoul", "Busan", "Tokyo", "New York", "London"]
)

# 인기 도시 선택 시 덮어쓰기
if popular_city:
    city_input = popular_city

# =========================
# GPS
# =========================
if gps_button:
    loc = get_geolocation()
    if loc:
        lat = loc["coords"]["latitude"]
        lon = loc["coords"]["longitude"]
        st.session_state.selected_location = f"{lat},{lon}"

# =========================
# 🔥 검색 자동완성 (key를 city_input 기반으로 생성)
# =========================
if city_input:

    search_url = f"http://api.weatherapi.com/v1/search.json?key={API_KEY}&q={city_input}"
    search_response = requests.get(search_url)
    search_data = search_response.json()

    if len(search_data) > 0:

        options = []
        for item in search_data:
            label = f"{item['name']}, {item['region']}, {item['country']}"
            value = f"{item['lat']},{item['lon']}"
            options.append((label, value))

        # 🔥 핵심: key를 검색어 기반으로 변경
        selected_label = st.sidebar.selectbox(
            "검색 결과 선택",
            [o[0] for o in options],
            key=f"select_{city_input}"
        )

        for o in options:
            if o[0] == selected_label:
                st.session_state.selected_location = o[1]

# =========================
# 날씨 조회
# =========================
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

    col1, col2 = st.columns([2, 1])

    with col1:
        st.header(f"{location_name}, {country}")
        st.subheader(f"{temp}°C")
        st.write(condition)

        if temp >= 30:
            st.warning("너무 더워요!")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("습도", f"{humidity}%")
        with c2:
            st.metric("체감온도", f"{feelslike}°C")
        with c3:
            st.metric("자외선 지수", uv)

        st.markdown("---")
        st.write("대기질 (PM2.5):", f"{aqi} μg/m³")
        st.write("일출:", sunrise)
        st.write("일몰:", sunset)
        st.write("달 모양:", moon_phase)

        st.subheader("시간별 온도 변화")

        hours = data["forecast"]["forecastday"][0]["hour"]

        hour_list = []
        temp_list = []

        for h in hours:
            hour_list.append(h["time"].split(" ")[1])
            temp_list.append(h["temp_c"])

        df = pd.DataFrame({
            "시간": hour_list,
            "온도": temp_list
        }).set_index("시간")

        st.line_chart(df)

        st.markdown("---")
        st.subheader("추천 정보")

        if temp >= 30:
            st.write("옷: 반팔, 반바지")
            st.write("소지품: 선크림, 물")
            st.write("추천 운동: 실내 운동 또는 수영")
        elif temp >= 20:
            st.write("옷: 얇은 긴팔")
            st.write("추천 운동: 러닝, 자전거")
        elif temp >= 10:
            st.write("옷: 자켓")
            st.write("추천 운동: 산책")
        else:
            st.write("옷: 두꺼운 코트")
            st.write("추천 운동: 실내 요가")

    with col2:
        st.subheader("지역 지도")

        map_url = f"https://map.naver.com/v5/search/{location_name}"
        iframe = f"""
        <iframe src="{map_url}"
        width="100%" height="500"
        style="border:none;"></iframe>
        """
        st.components.v1.html(iframe, height=500)
