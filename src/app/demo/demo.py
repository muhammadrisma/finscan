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
    
    user_input = st.text_area("Enter fish description:", height=100)
    
    # Create a container for the PEB and SERI inputs
    input_container = st.container()
    with input_container:
        input_col1, input_col2 = st.columns(2)
        with input_col1:
            no_peb = st.text_input("PEB Input", placeholder="Enter PEB value")
        with input_col2:
            no_seri = st.text_input("SERI Input", placeholder="Enter SERI value")
    
    # Display previous result if it exists
    if st.session_state.last_result:
        if st.session_state.last_result["flag"]:
            st.success("✅ Identification Successful!")
            st.write(f"Extracted Fish Name: {st.session_state.last_result['extracted_fish_name']}")
            st.write(f"English Name: {st.session_state.last_result['fish_name_english']}")
            st.write(f"Latin Name: {st.session_state.last_result['fish_name_latin']}")
        else:
            st.warning("⚠️ Low confidence in identification. Please try again with a more detailed description.")
    
    if st.button("Process"):
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

