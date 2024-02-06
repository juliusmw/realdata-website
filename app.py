import streamlit as st
import requests
from geopy.geocoders import Nominatim

# Initialize the geolocator
geolocator = Nominatim(user_agent="geoapiExercises")

def geocode_address(address):
    """Convert address to latitude and longitude."""
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

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
    living_area = st.number_input("Living area (in square feet)",
                                  min_value=1, max_value=10000, value = 100, step=1)
    address = st.text_input("Enter an address (or leave blank to select on map)")

    #load map with default view
    start_latitude, start_longitude = 48.8566, 2.3522 # Paris
    map_location = st.empty()  # Placeholder for the map
    submitted = st.form_submit_button("Predict Price")
    #integrate default map
    #map_location = st.map(data=[[start_latitude, start_longitude]], zoom=11)

    if submitted:
        if address:  # If the user entered an address, geocode it
            latitude, longitude = geocode_address(address)
            if latitude and longitude:
                map_location.map(data=[[latitude, longitude]], zoom=11)
            else:
                st.error("Could not geocode the address. Please try again or select a point on the map.")
        else:
            # If no address is entered, use the map to get latitude and longitude
            st.error("Please enter an address or select a location on the map.")

        # Assuming the user selects a point on the map or an address is successfully geocoded
        if latitude and longitude:
            # Prepare the data for the API call
            data = {
                "living_area": living_area,
                "latitude": latitude,
                "longitude": longitude
            }
            # Call the prediction API
            predicted_price = call_prediction_api(data)
            # Display the predicted price
            st.markdown(f"**Predicted Price: ${predicted_price}**")

# Display the map for selecting a location
# This is a simplified example. For actual implementation, consider using st.pydeck_chart or another method to capture clicks.
if not address:  # Only display the map if no address is entered
    map_location.map(zoom=4)
