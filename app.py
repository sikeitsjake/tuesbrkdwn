import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- CONFIGURATION ---
SHEET_NAME = "Crab Log Sheet"  # <--- CHANGE THIS to your exact sheet name

# --- UPDATED GOOGLE CONNECTION ---
def get_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # Use the 'service_account' method directly from gspread
    # This is more stable than the older oauth2client method
    gc = gspread.service_account(filename='creds.json')
    
    return gc.open(SHEET_NAME).sheet1

# --- USER INTERFACE ---
st.set_page_config(page_title="Crab Log", page_icon="🦀")

st.title("🦀 Crab Breakdown Log")
st.write("Enter the box counts below.")

# Create the form
with st.form("crab_entry", clear_on_submit=True):
    # 1. Who is logging?
    worker = st.selectbox("Worker Name", ["-- Select Name --", "Alex", "Brandon", "Jake", "Josh"])
    
    # 2. What kind of crabs?
    category = st.radio(
        "Crab Category",
        ["#1 Large Males", "#2 Medium Males", "Females", "Culls/Mixed"],
        index=None # Starts with nothing selected
    )
    
    # 3. How many?
    count = st.number_input("Number of Boxes", min_value=1, step=1)
    
    # 4. Any notes?
    notes = st.text_input("Notes (Optional)")

    # The Big Submit Button
    submit_button = st.form_submit_button("SUBMIT LOG ENTRY", use_container_width=True)

    if submit_button:
        if worker == "-- Select Name --" or category is None:
            st.error("⚠️ Please select both a Name and a Category!")
        else:
            try:
                sheet = get_sheet()
                # Create the data row
                timestamp = datetime.now().strftime("%m/%d/%Y")
                row = [timestamp, worker, category, count, notes]
                
                # Append to Google Sheets
                sheet.append_row(row)
                
                st.balloons()
                st.success(f"✅ Success! {count} boxes of {category} logged for {worker}.")
            except Exception as e:
                st.error(f"Error: {e}")

st.info("Tip: This data goes directly to the master Google Sheet.")