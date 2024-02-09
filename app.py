import streamlit as st
import requests
from geopy.geocoders import Nominatim
import pandas as pd
import pydeck as pdk
import pandas as pd
import streamlit as st

def geocode_address(address):
    """Convert address to latitude and longitude."""
    url = 'https://nominatim.openstreetmap.org/search'

    #Parameters
    params = {
        'q': address,
        'format': 'json',
    }
    # Send the GET request
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            # Extract latitude and longitude
            latitude = data[0]['lat']
            longitude = data[0]['lon']
            print("Location found ✅ " + address + " : " + latitude + " " + longitude)
            return latitude, longitude
        else:
            return "No results found", "No results found"
    else:
        return "Request failed", "Request failed"

def call_prediction_api(data):
    """Placeholder function to call the prediction API."""
    # Replace the URL with the actual API URL
    api_url = "https://placeholder-api-url.com/predict"
    response = requests.post(api_url, json=data)
    if response.status_code == 200:
        return response.json()['predicted_price']
    else:
        return "Error calling prediction API"

# Streamlit app layout
st.header("Predict house price")

# Form for user input
with st.form("house_price_form"):
    living_area = st.number_input("Living area (in square meters)",
                                  min_value=1, max_value=10000, value = 100, step=1)
    address = st.text_input("Enter an address (or leave blank to select on map)")

    #load map - default view is not possible with st.map
    map_location = st.empty()  # Placeholder for the map
    submitted = st.form_submit_button("Predict Price")

if submitted:
    latitude, longitude = geocode_address(address)
    # Convert latitude and longitude to float
    latitude = float(latitude)
    longitude = float(longitude)
    df_view = pd.DataFrame({'lat': [latitude], 'lon': [longitude]})
    #Display the map
    #st.map(data=df_view, zoom=15)
    st.map(data=df_view, size = 10 , zoom=15)

    if latitude and longitude:
            #TODO: Enhance API call based on final model prediction API
            # # Prepare the data for the API call
            # data = {
            #     "living_area": living_area,
            #     "latitude": latitude,
            #     "longitude": longitude
            # }
            # # Call the prediction API
            # predicted_price = call_prediction_api(data)
            predicted_price = 100000
            formatted_price = f"€{predicted_price:,.2f}"
            # Display the predicted price
            st.header(f"**Predicted Price: {formatted_price}**")
