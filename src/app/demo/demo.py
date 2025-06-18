import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

BASE_URL = "http://localhost:8000/api"

def get_audit_logs():
    """Get the latest audit log data"""
    response = requests.get(f"{BASE_URL}/audit/latest")
    return response.json()

def get_cache_logs():
    """Get all cache logs"""
    response = requests.get(f"{BASE_URL}/cache/logs")
    return response.json()

def get_top_fish():
    """Get top 5 identified fish"""
    try:
        response = requests.get(f"{BASE_URL}/result/top-fish")
        response.raise_for_status()  # This will raise an exception for 4XX/5XX status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching top fish data: {str(e)}")
        return None

def process_result_log(description: str, no_peb: str = "", no_seri: str = ""):
    """Process a result log with the given description"""
    data = {
        "original_description": description,
        "no_peb": no_peb,
        "no_seri": no_seri
    }
    response = requests.post(f"{BASE_URL}/result/log", json=data)
    return response.json()

# Initialize session state
if 'last_result' not in st.session_state:
    st.session_state.last_result = None
if 'refresh_dashboard' not in st.session_state:
    st.session_state.refresh_dashboard = False

# Only refresh if the refresh flag is set
if st.session_state.refresh_dashboard:
    st.session_state.refresh_dashboard = False
    st.rerun()

st.set_page_config(
    page_title="Fish Identification Demo",
    page_icon="🐟",
    layout="wide"
)

st.title("🐟 Fish Identification Demo")

# Create main layout columns
main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    st.header("Dashboard")
    
    # Use a container for the dashboard content
    dashboard_container = st.container()
    with dashboard_container:
        audit_data = get_audit_logs()
        
        st.subheader("System Statistics")
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        
        with stat_col1:
            st.metric("Processing Logs", audit_data["total_processing_logs"])
        with stat_col2:
            st.metric("Result Logs", audit_data["total_result_logs"])
        with stat_col3:
            st.metric("Cache Logs", audit_data["total_cache_logs"])
        
        # Add Top 5 Identified Fish section
        st.subheader("Top 5 Identified Fish")
        try:
            top_fish_response = get_top_fish()
            if top_fish_response and "items" in top_fish_response and top_fish_response["items"]:
                df_top = pd.DataFrame(top_fish_response["items"])
                
                required_columns = ["fish_name_english", "fish_name_latin", "count"]
                if all(col in df_top.columns for col in required_columns):
                    columns_to_display = required_columns.copy()
                    column_config = {
                        "fish_name_english": "English Name",
                        "fish_name_latin": "Latin Name",
                        "count": st.column_config.NumberColumn(
                            "Count",
                            help="Number of successful identifications",
                            format="%d"
                        )
                    }
                    
                    st.dataframe(
                        df_top[columns_to_display],
                        column_config=column_config,
                        hide_index=True
                    )
                else:
                    st.info("No successful fish identifications available yet.")
            else:
                st.info("No successful fish identifications available yet.")
        except Exception as e:
            st.warning(f"Unable to fetch top fish data: {str(e)}")
            st.info("No successful fish identifications available yet.")
        
        st.subheader("Cache Logs")
        cache_logs = get_cache_logs()
        
        if cache_logs:
            df = pd.DataFrame(cache_logs)
            st.dataframe(
                df[["extracted_fish_name", "fish_name_english", "fish_name_latin"]],
                column_config={
                    "extracted_fish_name": "Extracted Name",
                    "fish_name_english": "English Name",
                    "fish_name_latin": "Latin Name"
                },
                hide_index=True
            )
        else:
            st.info("No cache logs available.")

with main_col2:
    st.header("Chat Interface")
    
    # Use session state to store input values
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    if 'no_peb' not in st.session_state:
        st.session_state.no_peb = ""
    if 'no_seri' not in st.session_state:
        st.session_state.no_seri = ""

    # Create a form for all inputs
    with st.form("fish_identification_form"):
        user_input = st.text_area(
            "Enter fish description:",
            value=st.session_state.user_input,
            height=100,
            key="user_input"
        )
        
        # Create a container for the PEB and SERI inputs
        input_container = st.container()
        with input_container:
            input_col1, input_col2 = st.columns(2)
            with input_col1:
                no_peb = st.text_input(
                    "PEB Input",
                    value=st.session_state.no_peb,
                    placeholder="Enter PEB value",
                    key="no_peb"
                )
            with input_col2:
                no_seri = st.text_input(
                    "SERI Input",
                    value=st.session_state.no_seri,
                    placeholder="Enter SERI value",
                    key="no_seri"
                )
        
        # Move the Process button inside the form
        submitted = st.form_submit_button("Process")
    
    # Display previous result if it exists
    if st.session_state.last_result:
        if st.session_state.last_result["flag"]:
            st.success("✅ Identification Successful!")
            st.write(f"Extracted Fish Name: {st.session_state.last_result['extracted_fish_name']}")
            st.write(f"English Name: {st.session_state.last_result['fish_name_english']}")
            st.write(f"Latin Name: {st.session_state.last_result['fish_name_latin']}")
        else:
            st.warning("⚠️ Low confidence in identification. Please try again with a more detailed description.")
    
    if submitted:
        if user_input:
            with st.spinner("Processing..."):
                result = process_result_log(user_input, no_peb, no_seri)
                st.session_state.last_result = result
                
                if result["flag"]:
                    st.success("✅ Identification Successful!")
                    st.write(f"Extracted Fish Name: {result['extracted_fish_name']}")
                    st.write(f"English Name: {result['fish_name_english']}")
                    st.write(f"Latin Name: {result['fish_name_latin']}")
                    # Set refresh flag to True
                    st.session_state.refresh_dashboard = True
                    # Rerun only if refresh is needed
                    if st.session_state.refresh_dashboard:
                        st.session_state.refresh_dashboard = False
                        st.rerun()
                else:
                    st.warning("⚠️ Low confidence in identification. Please try again with a more detailed description.")
        else:
            st.warning("Please enter a fish description.")

