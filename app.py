from json.scanner import NUMBER_RE
from re import A
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from math import trunc
import time

# --- CONFIGURATION ---
SHEET_NAME = "Tuesday Breakdown" # <--- THIS MUST BE THE GOOGLE SHEET NAME
NUMBER_OF_MSG = "Number of"
CRAB_SIZE_LIST = ["Small", "Medium", "Bushel", "Large", "Extra Large"]

# Check if the user is authenticated
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Function that checks if the PIN is correct, and sets the user as authenticated
def check_password():
    """Returns True if the correct password is used"""
    if st.session_state["pin_input"] == "5618": # <-- Sets the pin for the app
        st.session_state.authenticated = True
        del st.session_state["pin_input"]
    else:
        st.error("Incorrect PIN. Please try again.")

# If the user isnt authenticated, then they have to login
if not st.session_state.authenticated:
    st.title("🔐 Tuesday Log Access 🔐")
    st.text_input(
        "Enter 4-Digit Access PIN",
        type="password",
        max_chars=4,
        key="pin_input",
        on_change=check_password
    )
    st.stop()

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
st.write("Fill in the following form to the best of your abilities:")

# Create the form
with st.form("crab_entry", clear_on_submit=False):

    # 1. Who is logging?
    worker = st.selectbox("Team Member Name", ["-- Select Name --", "Alex", "Brandon", "Jake", "Josh"])

    # Visual Markdown
    st.markdown("---")

    col1, col2, col3= st.columns(3)

    with col1:
        st.subheader("Maryland Inventory")
        # 2. How many Maryland 1's?
        num_MD_1s = st.number_input(f"{NUMBER_OF_MSG} Maryland 1's", min_value=0, step=1)

        # 3. How many Maryland 2's?
        num_MD_2s = st.number_input(f"{NUMBER_OF_MSG} Maryland 2's", min_value=0, step=1)

        # Visual Divider
        st.divider()
        st.subheader("Maryland Dozen Count")

        # 4. What came out of Maryland boxes?
        num_MD_SM = st.number_input("Dozens of Maryland Smalls", min_value=0.0, step=0.5)
        num_MD_MD = st.number_input("Dozens of Maryland Mediums", min_value=0.0, step=0.5)
        num_MD_LG = st.number_input("Dozens of Maryland Larges", min_value=0.0, step=0.5)
        num_MD_XL = st.number_input("Dozens of Maryland XLs", min_value=0.0, step=0.5)
        num_MD_bush = st.number_input("Bushels of Maryland 1's", min_value=0.0, step=0.5)

    with col2:
        st.subheader("Louisiana Inventory")
        # 5. How many Louisiana 1's?
        num_LA_1s = st.number_input(f"{NUMBER_OF_MSG} Louisiana 1's", min_value=0, step=1)

        # 6. How many Louisiana 2's?
        num_LA_2s = st.number_input(f"{NUMBER_OF_MSG} Louisiana 2's", min_value=0, step=1)

        # Visual Divider
        st.divider()
        st.subheader("Louisiana Dozen Count")

        # 7. What came out of Louisiana Boxes?
        num_LA_SM = st.number_input("Dozens of Louisiana Smalls", min_value=0.0, step=0.5)
        num_LA_MD = st.number_input("Dozens of Louisiana Mediums", min_value=0.0, step=0.5)
        num_LA_LG = st.number_input("Dozens of Louisiana Larges", min_value=0.0, step=0.5)
        num_LA_XL = st.number_input("Dozens of Louisiana XLs", min_value=0.0, step=0.5)
        num_LA_bush = st.number_input("Bushels of Louisiana 1's", min_value=0.0, step=0.5)
    
    with col3:
        st.subheader("Female Inventory")

        # How many boxes of Females?
        num_fem_boxes = st.number_input(f"{NUMBER_OF_MSG} Females", min_value=0, step=1)

        # Visual Divider
        st.divider()
        st.subheader("Female Dozen Count")

        # What came out of the female boxes?
        num_regf = st.number_input("Dozens of Regular Females", min_value=0.0, step=0.5)
        num_lgf = st.number_input("Dozens of Large Females", min_value=0.0, step=0.5)
        num_xlf = st.number_input("Dozens of XL Females", min_value=0.0, step=0.5)

    # SAFTEY CHECKBOX
    st.markdown("---") # Visual Seperator
    st.subheader("Data Confirmation")
    confirm_data = st.checkbox(f"I, {worker}, have verified all counts are correct and I am ready to submit.")

    # The Big Submit Button
    submit_button = st.form_submit_button("SUBMIT LOG ENTRY", use_container_width=True)

    # Get the current day of the week
    date_obj = datetime.now()
    day_of_week = date_obj.strftime("%a")

    # When the submit button is pressed do these checks
    if submit_button:

        # Form can only be submitted on Tuesdays
        if day_of_week != "Tues":
            st.error("⚠️ This form is only to be submitted on Tuesdays!")

        # Check to make sure the user submits their data correctly
        elif not confirm_data:
            st.error("⚠️ Submission Blocked! Please complete the form and click the Confirmation Box.")
        
        # Team Member must be submitted and a Crab Category must be selected
        elif worker == "-- Select Name --":
            st.error("⚠️ Please select a Name!")
        else:
            try:
                sheet = get_sheet()
                # Create the data row
                timestamp = datetime.now().strftime("%m/%d/%Y")

                # This is the data that will be appended. MUST BE AN ARRAY OF SINGLE VALUES
                row = [
                    timestamp, 
                    worker, 
                    num_MD_1s, num_MD_2s, num_MD_SM, num_MD_MD, num_MD_LG, num_MD_XL, num_MD_bush,
                    num_LA_1s, num_LA_2s, num_LA_SM, num_LA_MD, num_LA_LG, num_LA_XL, num_LA_bush,
                    num_fem_boxes, num_regf, num_lgf, num_xlf
                    ]
                
                # Append to Google Sheets
                sheet.append_row(row)
                
                # Show success animation
                st.balloons()
                st.success(f"✅ Success! Thank you {worker} for submitting your data!")

                # Clear the app.
                time.sleep(2)
                st.rerun()
            
            # If any error occurs, show that on the app.
            except Exception as e:
                st.error(f"Error: {e}")

st.info("Tip: This data goes directly to the master Google Sheet.")