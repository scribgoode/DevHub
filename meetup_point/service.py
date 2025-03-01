from meetup_point.models import Address
import googlemaps
from dotenv import load_dotenv
import os
# Load environment variables from the .env file (if present)
load_dotenv(verbose=True, override=True)
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

def calculate_midpoint(lat1, lng1, lat2, lng2):
    """
    Calculate the midpoint of a line segment defined by two points (lat1, lng1) and (lat2, lng2).
    
    Parameters:
    lat1, lng1: Coordinates of the first point.
    lat2, lng2: Coordinates of the second point.

    Returns:
    A tuple representing the midpoint (lat, lng).
    """
    midpoint_lat = (lat1 + lat2) / 2
    midpoint_lng = (lng1 + lng2) / 2
    return {'lat': midpoint_lat, 'lng': midpoint_lng}

def saveAddress(data):
    new_address = Address(
        street=data.get("street"),
        city=data.get("city"),
        state=data.get("state"),
        zip_code=data.get("zipcode"),
    )
    print("before verify_address()")
    if new_address.verify_address():
        print("Address is valid -- saving to database")
        new_address.save()
        return new_address
    else:
        print("Address is invalid -- not saving to database")

def get_nearby_places(lat, lng, place_type):
    """Uses Google Places API to find cafes & restaurants near the midpoint."""

    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google Maps API key not found in environment variables")

        # Initialize the Google Maps client
        gmaps = googlemaps.Client(key=api_key)
        places_result = gmaps.places_nearby(
            location=(lat, lng),
            radius=1000,  # 1000 meters (1 km)
            type=place_type  # "cafe|restaurant"
        )

        places = []
        for place in places_result.get("results", []):
            places.append({
                "name": place["name"],
                "address": place.get("vicinity", "No address available"),
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"]
            })

        return places
    except Exception as e:
        print(e)
        return False