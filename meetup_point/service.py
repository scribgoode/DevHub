from meetup_point.models import Address
from cities_light.models import City, Country
import googlemaps
from dotenv import load_dotenv
from django.conf import settings

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
    # Look up the City object based on the provided city name and country name
    
    city = data.get("city")
    country = data.get("country")
    print("data:", data)
    print("country:",country.get("name"))
    try:
        country = Country.objects.get(name=country.get("name"))
        print('got country;')
        city = City.objects.get(name=city.get("name"), country=country)
        print('got city;')
    except Country.DoesNotExist:
        print(f"Country '{country.get("name")}' does not exist.")
        return None
    except City.DoesNotExist:
        print(f"City '{city.get("name")}' in country '{country.get("name")}' does not exist.")
        return None
    except Exception as e:
        print(e)
        return None

    # Check if the address already exists in the database
    existing_address = Address.objects.filter(
        street=data.get("street"),
        city=city,
        state=data.get("state"),
        zip_code=data.get("zip_code"),
        country=country
    ).first()

    print("exist:", existing_address)

    if existing_address and existing_address.verify_address():
        print("Address already exists in the database")
        return existing_address
    
    # Create a new Address object
    new_address = Address(
        street=data.get("street"),
        city=city,
        state=data.get("state"),
        zip_code=data.get("zip_code"),
        country=country
    )

    if new_address.verify_address():
        print("Address is valid -- saving to database")
        new_address.save()
        return new_address
    else:
        print("Address is invalid -- not saving to database")
        return None

def get_nearby_places(lat, lng, place_type):
    """Uses Google Places API to find cafes & restaurants near the midpoint."""

    try:
        api_key = settings.GOOGLE_API_KEY
        # Initialize the Google Maps client
        gmaps = googlemaps.Client(key=api_key)
        places_result = gmaps.places_nearby(
            location=(lat, lng),
            radius=1000,  # 1000 meters (1 km)
            type=place_type  # "cafe|restaurant"
        )

        # places = []
        # for place in places_result.get("results", []):
        #     places.append({
        #         "name": place["name"],
        #         "address": place.get("vicinity", "No address available"),
        #         "place_id": place["place_id"],
        #         "lat": place["geometry"]["location"]["lat"],
        #         "lng": place["geometry"]["location"]["lng"]
        #     })

        return places_result["results"]
    except Exception as e:
        print(e)
        return False