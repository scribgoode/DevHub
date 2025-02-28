import os
from django.db import models
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
            print(api_key)
            if not api_key:
                raise ValueError("Google Maps API key not found in environment variables")

            # Initialize the Google Maps client
            gmaps = googlemaps.Client(key=api_key)

            # Construct the full address
            full_address = f"{self.street}, {self.city}, {self.state} {self.zip_code}"

            # Use the Geocoding API to verify the address
            validation_result = gmaps.geocode(full_address)
            print(validation_result)
            self.lat = validation_result[0]['geometry']['location']['lat']
            self.lng = validation_result[0]['geometry']['location']['lng']

            if validation_result:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
