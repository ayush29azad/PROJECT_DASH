import streamlit as st
import base64

st.set_page_config(page_title="DDS Manager", layout="wide", initial_sidebar_state="expanded")

# Background Image Loader
def get_b64(file):
    with open(file, "rb") as f: return base64.b64encode(f.read()).decode()

img_b64 = get_b64("images/car.jpg")

st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{img_b64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
""", unsafe_allow_html=True)

# Load CSS
with open("css/styleMain.css", "r") as f: st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_logo_b64(file):
    with open(file, "rb") as f:
        # SVG ke liye content-type alag hota hai
        data = base64.b64encode(f.read()).decode()
    return f"data:image/svg+xml;base64,{data}"

logo_b64 = get_logo_b64("images/jlr_logo.svg")

# Ab header section mein use karo
st.markdown(f"""
    <div class="header-block">
        <div class="header-text">
            <h1>DI QUALITY DASHBOARD</h1>
            <p>Quality Dashboard | Monitoring Health Metrics</p>
        </div>
        <div>
            <img src="{logo_b64}" width="100">
        </div>
    </div>
""", unsafe_allow_html=True)
# Buttons
c1, c2 = st.columns(2)
with c1: 
    if st.button("🚀 KLOCKWORK DASHBOARD"): st.switch_page("pages/klocwork_app.py")
with c2: 
    if st.button("🧪 GTEST DASHBOARD"): st.switch_page("pages/gtest_app.py")