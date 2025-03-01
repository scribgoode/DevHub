import os
from django.db import models
from django.forms import ValidationError
import googlemaps
from dotenv import load_dotenv

# Load environment variables from the .env file (if present)
load_dotenv(verbose=True, override=True)
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Create your models here.
class Address(models.Model):
    street = models.CharField(max_length = 64)
    city = models.CharField(max_length = 64)
    state = models.CharField(max_length = 2)
    zip_code = models.CharField(max_length = 5)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    def verify_address(self):
        # Get the Google Maps API key from environment variables
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("Google Maps API key not found in environment variables")

            # Initialize the Google Maps client
            gmaps = googlemaps.Client(key=api_key)

            # Construct the full address
            full_address = f"{self.street}, {self.city}, {self.state} {self.zip_code}"
            print("full address:" , full_address)

            # Use the Geocoding API to verify the address
            validation_result = gmaps.geocode(full_address)

            # ❌ 1. Check if the address is valid
            if validation_result[0].get("partial_match", False):
                return False

            # ❌ Ensure required address components exist
            address_components = {comp["types"][0]: comp["long_name"] for comp in validation_result[0]["address_components"]}
            required_components = ["street_number", "route", "locality", "administrative_area_level_1", "country"]

            if not all(comp in address_components for comp in required_components):
                return False
            
            # ✅ Get latitude and longitude
            self.lat = validation_result[0]['geometry']['location']['lat']
            self.lng = validation_result[0]['geometry']['location']['lng']


             # ❌ 4. Reverse Geocode to verify the location is real
            reverse_results = gmaps.reverse_geocode((self.lat, self.lng))
            if not reverse_results or "street_number" not in {comp["types"][0] for comp in reverse_results[0]["address_components"]}:
                return False

            return True
        except Exception as e:
            print(e)
            return False
