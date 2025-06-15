import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

# API endpoints
BASE_URL = "http://localhost:8000/api"

def get_audit_logs():
    """Get the latest audit log data"""
    response = requests.get(f"{BASE_URL}/audit/latest")
    return response.json()

def get_cache_logs():
    """Get all cache logs"""
    response = requests.get(f"{BASE_URL}/cache/logs")
    return response.json()

def process_result_log(description: str):
    """Process a result log with the given description"""
    data = {
        "original_description": description
    }
    response = requests.post(f"{BASE_URL}/result/log", json=data)
    return response.json()

# Set page config
st.set_page_config(
    page_title="Fish Identification Demo",
    page_icon="🐟",
    layout="wide"
)

# Title
st.title("🐟 Fish Identification Demo")

# Create two columns for the layout
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Chat Interface")
    
    # Chat input
    user_input = st.text_area("Enter fish description:", height=100)
    
    if st.button("Process"):
        if user_input:
            with st.spinner("Processing..."):
                result = process_result_log(user_input)
                
                if result["flag"]:
                    st.success("✅ Identification Successful!")
                    st.write(f"Extracted Fish Name: {result['extracted_fish_name']}")
                    st.write(f"English Name: {result['fish_name_english']}")
                    st.write(f"Latin Name: {result['fish_name_latin']}")
                else:
                    st.warning("⚠️ Low confidence in identification. Please try again with a more detailed description.")
        else:
            st.warning("Please enter a fish description.")

with col2:
    st.header("Dashboard")
    
    # Get audit logs
    audit_data = get_audit_logs()
    
    # Display metrics
    st.subheader("System Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Processing Logs", audit_data["total_processing_logs"])
    with col2:
        st.metric("Result Logs", audit_data["total_result_logs"])
    with col3:
        st.metric("Cache Logs", audit_data["total_cache_logs"])
    
    # Cache Logs Table
    st.subheader("Cache Logs")
    cache_logs = get_cache_logs()
    
    if cache_logs:
        df = pd.DataFrame(cache_logs)
        st.dataframe(
            df[["id", "extracted_fish_name", "fish_name_english", "fish_name_latin"]],
            column_config={
                "id": "ID",
                "extracted_fish_name": "Extracted Name",
                "fish_name_english": "English Name",
                "fish_name_latin": "Latin Name"
            },
            hide_index=True
        )
    else:
        st.info("No cache logs available.")
