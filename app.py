import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- CONFIGURATION ---
SHEET_NAME = "Tuesday Breakdown" # <--- THIS MUST BE THE GOOGLE SHEET NAME

# --- GOOGLE CONNECTION ---
def get_sheet():
    # 1. Access the secrets dictionary
    creds_info = st.secrets["gcp_service_account"]
    # 2. Authenticate using the dictionary
    gc = gspread.service_account_from_dict(creds_info)
    # 3. Open the sheet
    return gc.open(SHEET_NAME).sheet1

# --- USER INTERFACE ---
st.set_page_config(page_title="Tuesday Crab Log", page_icon="🦀")

st.title("🦀 Tuesday Crab Breakdown Form")
st.write("Enter the box counts below.")

# Create the form
with st.form("crab_entry", clear_on_submit=True):
    # 1. Who is logging?
    worker = st.selectbox("Team Member Name", ["-- Select Name --", "Alex", "Brandon", "Jake", "Josh"])
    
    # 2. What kind of crabs?
    category = st.radio(
        "Crab Category",
        ["#1 Males", "#2 Males", "Females"],
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