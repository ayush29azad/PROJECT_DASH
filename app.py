import streamlit as st
import pandas as pd
import gspread
import json
import plotly.express as px
from google.oauth2 import service_account

# --- Configuration ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ihEevHcYY3joMBGqT4T_MdxXVhfVkvk-Otp1M24RkU/edit"
SHEET_NAME = "Sheet1"

st.set_page_config(page_title="Klocwork Health Dashboard", layout="centered")

# --- CSS ---
st.markdown("""
    <style>
    .main .block-container { background-color: rgba(255, 255, 255, 0.95); padding: 3rem; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    h1 { color: #1A1A1A !important; text-align: center; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- Updated Authentication Logic ---
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
    
    # Cloud (Secrets) ya Local (File) se load karo
    if "GSPREAD_JSON" in st.secrets:
        creds_dict = json.loads(st.secrets["GSPREAD_JSON"])
    else:
        with open('klocdata-ce7e1565a827.json') as f:
            creds_dict = json.load(f)
            
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client

# --- Main App ---
client = get_gspread_client()
sheet = client.open_by_url(SHEET_URL).worksheet(SHEET_NAME)
df = pd.DataFrame(sheet.get_all_records())

st.title("Klocwork Health Dashboard")

# --- UI Components ---
with st.expander("➕ Add New Release"):
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        tag = c1.text_input("Release Tag")
        count = c2.number_input("Defect Count", min_value=0)
        if st.form_submit_button("Add to Database"):
            sheet.append_row([tag, count])
            st.rerun()

edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

if st.button("Save Changes"):
    sheet.clear()
    sheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())
    st.success("Saved!")
    st.rerun()

# --- Visualization ---
st.subheader("Visual Analysis")
n = st.slider("Select N releases", 5, len(edited_df), 5)
plot_df = edited_df.tail(n)
fig = px.line(plot_df, x='Release Tag', y='Defect Count', markers=True)
st.plotly_chart(fig, use_container_width=True)