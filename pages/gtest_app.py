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
    except:
        pass
load_css()

# --- Auth Function ---
def get_gspread_client():
    if "GSPREAD_JSON" in st.secrets:
        creds_dict = json.loads(st.secrets["GSPREAD_JSON"])
    else:
        with open('klocdata-ce7e1565a827.json') as f:
            creds_dict = json.load(f)
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
    return gspread.authorize(service_account.Credentials.from_service_account_info(creds_dict, scopes=scope))

# --- Data Load ---
client = get_gspread_client()
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/17ihEevHcYY3joMBGqT4T_MdxXVhfVkvk-Otp1M24RkU/edit").worksheet("Sheet2")
@st.cache_data(ttl=600) 
def load_gtest_data():
    return pd.DataFrame(sheet.get_all_records())

df = load_gtest_data()


st.title("🧪 GTest Health Dashboard")

# --- UI Components ---
with st.expander("➕ Add New Release Metrics"):
    with st.form("gtest_form", clear_on_submit=True):
        c1, c2, c3, c4, c5 = st.columns(5)
        rel = c1.text_input("Release")
        lc = c2.number_input("Line Coverage", 0.0, 100.0)
        fc = c3.number_input("Function Coverage", 0.0, 100.0)
        bc = c4.number_input("Branches Coverage", 0.0, 100.0)
        dc = c5.number_input("Decision Coverage", 0.0, 100.0)
        if st.form_submit_button("Add to Database"):
            sheet.append_row([rel, lc, fc, bc, dc])
            st.rerun()

edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

if st.button("Save Changes"):
    sheet.clear()
    sheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())
    st.success("Changes Saved!")
    st.rerun()

# --- Visualization (Fixed with Mapping) ---
st.subheader("Coverage Analysis")
if not edited_df.empty:
    # Google Sheet headers ke exact naam yahan map karo
    metrics = {
        "Line": "Line Coverage", 
        "Func": "Function Coverage", 
        "Branch": "Branches Coverage", 
        "Deci": "Decision Coverage"
    }
    selected = st.selectbox("Select Metric", list(metrics.keys()))
    target_col = metrics[selected]
    
    fig = px.line(edited_df, x='Release', y=target_col, markers=True)
    fig.update_layout(xaxis_title="Release", yaxis_title=target_col)
    st.plotly_chart(fig, use_container_width=True)

if st.sidebar.button("⬅️ Back"): st.switch_page("app.py")