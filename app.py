import streamlit as st
import pandas as pd
import os
import shutil
from datetime import datetime
import plotly.express as px

# --- Configuration ---
FILE_PATH = "Klocwork_Release_Data.xlsx"
BACKUP_DIR = "backups"

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

st.set_page_config(page_title="Klocwork Health Dashboard", layout="centered")

# --- JLR Inspired CSS ---
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQyqBmbkC4ziLzvuB_Tk67UrhFFfNAKfR71giF8MKwcIwPKFBd3nBk4p4Dd&s=10");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 3rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        background-color: rgba(255, 255, 255, 0.90); /* 0.90 se thoda aur transparent ho jayega */
        backdrop-filter: blur(5px); /* Yeh background ko blur kar dega, text aur achha dikhega */

    }
            
    h1, h2, h3 {
        color: #1A1A1A !important;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-family: 'Segoe UI', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Data Loading ---
if os.path.exists(FILE_PATH):
    df = pd.read_excel(FILE_PATH)
else:
    st.error("Excel file not found!")
    st.stop()

st.title("Klocwork Health Dashboard")

# --- Backup & Restore Section ---
st.subheader("Data Management")
col_b1, col_b2 = st.columns(2)

if col_b1.button("💾 Create Manual Backup"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = f"{BACKUP_DIR}/backup_{timestamp}.xlsx"
    shutil.copyfile(FILE_PATH, backup_file)
    st.success(f"Backup saved at: {timestamp}")
    st.rerun()

backup_files = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.xlsx')]
if backup_files:
    selected_backup = col_b2.selectbox("Select Backup to Restore", backup_files)
    if st.button("🔄 Restore Selected Backup"):
        shutil.copyfile(f"{BACKUP_DIR}/{selected_backup}", FILE_PATH)
        st.success("Data Restored Successfully!")
        st.rerun()

# --- Add New Release ---
with st.expander("➕ Add New Release"):
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        new_tag = col1.text_input("Release Tag")
        new_count = col2.number_input("Defect Count", min_value=0)
        submitted = st.form_submit_button("Add to Database")
        if submitted:
            new_row = pd.DataFrame({"Release Tag": [new_tag], "Defect Count": [new_count]})
            df = pd.concat([new_row, df], ignore_index=True)
            df.to_excel(FILE_PATH, index=False)
            st.rerun()

# --- Edit/Delete ---
st.subheader("Edit/Delete Release Data")
edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

if st.button("Save Changes to Database"):
    edited_df.to_excel(FILE_PATH, index=False)
    st.success("Changes saved successfully!")
    st.rerun()

st.divider()

# --- Visual Analysis ---
st.subheader("Visual Analysis")
col_a, col_b = st.columns([1, 1])
n = col_a.slider("Select N releases", 5, len(edited_df), 5)
chart_mode = col_b.radio("Chart Type", ["Line", "Bar"], horizontal=True)

# Sort: OLD (Left) -> NEW (Right)
plot_df = edited_df.head(n).iloc[::-1]

if chart_mode == "Line":
    fig = px.line(plot_df, x='Release Tag', y='Defect Count', markers=True)
    fig.update_traces(line_color='#2E86C1', marker=dict(size=8))
else:
    fig = px.bar(plot_df, x='Release Tag', y='Defect Count')
    fig.update_traces(marker_color='#2E86C1', width=0.5)

fig.update_layout(
    plot_bgcolor='white', 
    margin=dict(t=80, b=20, l=20, r=20),
    title={
        'text': "Klocwork Health Summary by Release<br><span style='font-size:14px; color:gray;'>DI Platform · Squad4 · Open Issues per Release</span>",
        'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'
    }
)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')

st.plotly_chart(fig, use_container_width=True)