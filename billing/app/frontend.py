import streamlit as st
import requests
import pandas as pd
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

st.title("Billing System Frontend")

# Provider Management
st.header("Provider Management")
provider_name = st.text_input("Enter provider name")
if st.button("Create Provider"):
    response = requests.post(f"{API_BASE_URL}/provider", json={"name": provider_name})
    if response.status_code == 201:
        st.success(f"Provider created with ID: {response.json()['id']}")
    else:
        error_msg = response.json().get("error", "Unknown error occurred")
        st.error(error_msg)

provider_id = st.text_input("Provider ID for update")
new_provider_name = st.text_input("New Provider Name")
if st.button("Update Provider"):
    response = requests.put(f"{API_BASE_URL}/provider/{provider_id}", json={"name": new_provider_name})
    if response.status_code == 200:
        st.success("Provider updated successfully")
    else:
        error_msg = response.json().get("error", "Unknown error occurred")
        st.error(error_msg)

# Rate Management
st.header("Rate Management")
uploaded_file = st.file_uploader("Upload rates.xlsx", type=["xlsx"])
if uploaded_file and st.button("Upload Rates"):
    files = {"file": uploaded_file}
    response = requests.post(f"{API_BASE_URL}/rates", files=files)
    if response.status_code == 201:
        st.success("Rates uploaded successfully")
    else:
        st.error("Failed to upload rates")

if st.button("Download Current Rates"):
    response = requests.get(f"{API_BASE_URL}/rates")
    if response.status_code == 200:
        st.download_button("Download Rates.xlsx", response.content, "rates.xlsx")
    else:
        st.error("Failed to fetch rates")

# Truck Management
st.header("Truck Management")
truck_id = st.text_input("Enter Truck License Plate")
truck_provider_id = st.text_input("Enter Provider ID for Truck")
if st.button("Register Truck"):
    response = requests.post(f"{API_BASE_URL}/truck", json={"id": truck_id, "provider_id": truck_provider_id})
    if response.status_code == 201:
        st.success("Truck registered successfully")
    else:
        error_msg = response.json().get("error", "Unknown error occurred")
        st.error(error_msg)

if st.button("Update Truck Provider"):
    response = requests.put(f"{API_BASE_URL}/truck/{truck_id}", json={"provider_id": truck_provider_id})
    if response.status_code == 200:
        st.success("Truck provider updated successfully")
    else:
        error_msg = response.json().get("error", "Unknown error occurred")
        st.error(error_msg)

# Get Truck Data
st.header("Truck Data")
truck_id_query = st.text_input("Enter Truck ID for data retrieval")
truck_date_from = st.text_input("From (yyyymmddhhmmss)", "20250318000000", key="date_from")
truck_date_to = st.text_input("To (yyyymmddhhmmss)", "", key="date_to")
if st.button("Get Truck Data"):
    response = requests.get(f"{API_BASE_URL}/truck/{truck_id_query}?from={truck_date_from}&to={truck_date_to}")
    try:     
        if response.status_code == 200:
            st.json(response.json())
        else:
            error_msg = response.json().get("error", "Unknown error occurred")
            st.error(error_msg)
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: Truck ID empty")

# Get Bill Data
st.header("Billing Information")
bill_provider_id = st.text_input("Enter Provider ID for Billing")
date_from = st.text_input("From (yyyymmddhhmmss)", "")
date_to = st.text_input("To (yyyymmddhhmmss)", "")
if st.button("Get Bill"):
    response = requests.get(f"{API_BASE_URL}/bill/{bill_provider_id}?from={date_from}&to={date_to}")
    if response.status_code == 200:
        bill_data = response.json()
        st.json(bill_data)
        
        # Displaying bill details in a table
        if "products" in bill_data:
            df = pd.DataFrame(bill_data["products"])
            st.dataframe(df)
    else:
        st.error("Failed to fetch bill data")
