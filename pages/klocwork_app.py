import streamlit as st
import pandas as pd
import gspread
import json
import plotly.express as px
from google.oauth2 import service_account

# --- CSS Load ---
def load_css():
    try:
        with open("css/style.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found at css/style.css")
load_css()

# --- Auth Function (Consistent) ---
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
    if "GSPREAD_JSON" in st.secrets:
        creds_dict = json.loads(st.secrets["GSPREAD_JSON"])
    else:
        with open('klocdata-ce7e1565a827.json') as f:
            creds_dict = json.load(f)
    return gspread.authorize(service_account.Credentials.from_service_account_info(creds_dict, scopes=scope))

# --- Data Load ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ihEevHcYY3joMBGqT4T_MdxXVhfVkvk-Otp1M24RkU/edit"
client = get_gspread_client()
sheet = client.open_by_url(SHEET_URL).worksheet("Sheet1")
# df = pd.DataFrame(sheet.get_all_records())
@st.cache_data(ttl=600) 
def load_kloc_data():
    return pd.DataFrame(sheet.get_all_records())

df = load_kloc_data()


# --- Main UI ---
st.title("🧪Klocwork Health Dashboard")

# Add New Release
with st.expander("➕ Add New Release"):
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        tag = c1.text_input("Release Tag")
        count = c2.number_input("Defect Count", min_value=0)
        if st.form_submit_button("Add to Database"):
            sheet.append_row([tag, count])
            st.rerun()

# Editable Table
edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

if st.button("Save Changes"):
    sheet.clear()
    sheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())
    st.success("Changes Saved!")
    st.rerun()

# Visualization
st.subheader("Visual Analysis")
if not edited_df.empty:
    n = st.slider("Select N releases for view", 5, len(edited_df), 5)
    plot_df = edited_df.tail(n)
    fig = px.line(plot_df, x='Release Tag', y='Defect Count', markers=True)
    fig.update_layout(xaxis_title="Release", yaxis_title="Total Defects")
    st.plotly_chart(fig, use_container_width=True)

if st.sidebar.button("⬅️ Back to Home"):
    st.switch_page("app.py")