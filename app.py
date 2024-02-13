import streamlit as st
import requests
from geopy.geocoders import Nominatim
import pandas as pd
import pydeck as pdk
import pandas as pd
import streamlit as st
import json

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
            osm_id = data[0]['osm_id']
            osm_type = data[0]['osm_type']
            address_display_name = data[0]['display_name']
            print("Location found ✅ " + address + " : " + latitude + " " + longitude)
            return latitude, longitude, osm_id, osm_type, address_display_name
        else:
            return "No results found", "No results found"
    else:
        return "Request failed", "Request failed"

def get_postalcode(osm_id, osm_type):
    url = 'https://nominatim.openstreetmap.org/details'
    params = {
        'osmtype': 'W' if osm_type == 'way' else 'R' if osm_type == 'relation' else 'N',
        'osmid': osm_id,
        'format': 'json'
    }
    response = requests.get(url, params=params)
    #print(response.url)
    if response.status_code == 200:
        data = response.json()
        if data:
            # Extract postal code
            postal_code = data['calculated_postcode']
            print("Postal code found ✅: " + postal_code)
            return postal_code
        else:
            return "No results found", "No results found"
    else:
        return "Request failed", "Request failed"

def call_prediction_api(data):
    """Placeholder function to call the prediction API."""
    # Replace the URL with the actual API URL
    #api_url = "http://localhost:8000/predict_price"
    api_url_local = "http://localhost:8000/predict_price"
    params = {
        'living_area': data['living_area'],
        'latitude': data['latitude'],
        'longitude': data['longitude'],
        'property_type': data['property_type'],
        'built': data['built'],
        'number_of_rooms': data['number_of_rooms'],
        'postal_code': data['postal_code'],
        'number_of_dependency': data['number_of_dependency']
    }
    response = requests.get(api_url_local, params=params)
    if response.status_code == 200:
        data = response.json()
        # Extract the predicted price
        predicted_price = data['predicted_price']
        print('Predicted price ✅: ' + str(predicted_price))
        return predicted_price
    else:
        return "Error calling prediction API"

def calculate_price_range(predicted_price, percentage=10):
    """Calculate the price range based on a percentage.

    Args:
        predicted_price (float): The API's predicted price.
        percentage (int, optional): The percentage to calculate the range. Defaults to 10.

    Returns:
        tuple: A tuple containing the minimum and maximum prices.
    """
    min_price = predicted_price * (1 - percentage / 100)
    max_price = predicted_price * (1 + percentage / 100)
    return min_price, max_price

def generate_gradient_bar(min_price, max_price, predicted_price):
    """Generate HTML for a horizontal gradient bar.

    Args:
        min_price (float): The minimum price.
        max_price (float): The maximum price.
        predicted_price (float): The predicted price.

    Returns:
        str: HTML string for the gradient bar.
    """
    # Calculate the relative position of the predicted price within the range
    if max_price != min_price:  # Prevent division by zero
        position = (predicted_price - min_price) / (max_price - min_price) * 100
    else:
        position = 50  # Default to the middle if min and max are the same

    # Generate HTML for the gradient bar
    gradient_bar_html = f"""
    <style>
    .gradient-bar {{
        height: 20px;
        width: 100%;
        background: linear-gradient(to right, green, red);
        position: relative;
    }}
    .price-marker {{
        height: 30px;
        width: 2px;
        background-color: black;
        position: absolute;
        left: {position}%;
        top: -5px;
    }}
    </style>
    <div class="gradient-bar">
        <div class="price-marker"></div>
    </div>
    """
    return gradient_bar_html


#start of web-interface design - Documentation: https://docs.streamlit.io/

# Streamlit app layout
st.header("Predict house price")

# Form for user input
with st.form("house_price_form"):
    living_area = st.number_input("Living area (in square meters)",
                                  min_value=1, max_value=10000, value = 100, step=1)
    number_of_rooms = st.number_input("Number of rooms (where you live, eat or sleep)", min_value=1, max_value=100, value = 3)
    property_type_selected = st.radio(
        "What is the type of your property?",
        ["Apartment 🏢", "House 🏡"]
    )
    built_status = st.radio(
        "What is the type of your property?",
        ["Built ✅", "Off-Plan 🚧"],
        captions = ["Apartment / house exists.", "You buy it before it is built, when only the plans for it exist."]
    )
    number_of_dependency = st.number_input("Do you have a dependency (e.g. garage, cellar, etc.)?", min_value=0, max_value=10, value = 0)

    address = st.text_input("Enter an address (or leave blank to select on map)")

    #load map - default view is not possible with st.map
    map_location = st.empty()  # Placeholder for the map
    submitted = st.form_submit_button("Predict Price")

if submitted:
    latitude, longitude, osm_id, osm_type, address_display_name = geocode_address(address)
    #get postal code based on address data
    postal_code = get_postalcode(osm_id = osm_id, osm_type= osm_type)
    postal_code = int(postal_code)
    #determine poperty type based on user input; apartment is english vs. appartment is french spelling
    if property_type_selected == 'Apartment 🏢':
        property_type = 'appartment'
    else:
        property_type = 'house'
    #determine built status based on user input
    if built_status == 'Built ✅':
        built = 'built' #default value
    else:
        built = 'off-plan'
    # Convert number of rooms
    number_of_rooms = float(number_of_rooms)
    # Convert dependency status - TODO: check if this is correct
    number_of_dependency = int(number_of_dependency)

    # Convert latitude and longitude to float
    latitude = float(latitude)
    longitude = float(longitude)
    df_view = pd.DataFrame({'lat': [latitude], 'lon': [longitude]})
    #Display the map
    extended_address_display = f"**Location 📍**: {address_display_name}"
    st.markdown(extended_address_display)
    st.map(data=df_view, size = 10 , zoom=15)

    if latitude and longitude:
            # Prepare the data for the API call
            data = {
                "living_area": living_area,
                "latitude": latitude,
                "longitude": longitude,
                "property_type": property_type,
                "built": built,
                "number_of_rooms": number_of_rooms,
                "postal_code": postal_code,
                "number_of_dependency": number_of_dependency
            }
            # Call the prediction API
            predicted_price = call_prediction_api(data)


            if predicted_price != "Error calling prediction API":
                # Calculate and display the predicted price
                formatted_price = f"€{predicted_price:,.2f}"
                st.header(f"**Predicted Price: {formatted_price}**")

                # Calculate and display the price range
                percentage = 10  # Define the percentage for the range calculation
                # Calculate the price range
                min_price, max_price = calculate_price_range(predicted_price, percentage)
                #generat the gradient bar
                gradient_bar_html = generate_gradient_bar(min_price, max_price, predicted_price)
                # Display the gradient bar in Streamlit
                st.markdown(gradient_bar_html, unsafe_allow_html=True)
                # You can also display the price range text if you'd like
                st.write(f"**Price Range:** €{min_price:,.2f} - €{max_price:,.2f}")
                # formatted_min_price = f"€{min_price:,.2f}"
                # formatted_max_price = f"€{max_price:,.2f}"
                #st.write(f"**Price Range:** {formatted_min_price} - {formatted_max_price}")
            else:
                st.write("There was an error in predicting the price. Please try again.")
