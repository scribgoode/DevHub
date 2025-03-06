import os
from django.db import models
from django.forms import ValidationError
import googlemaps
from django.conf import settings
from cities_light.models import Country, City

class Address(models.Model):
    street = models.CharField(max_length=64, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zip_code = models.CharField(max_length=5, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.street}, {self.city.name if self.city else ''}, {self.state} {self.zip_code}, {self.country.name if self.country else ''}"

    def verify_address(self):
        print('here')
        # Get the Google Maps API key from environment variables
        try:
            api_key = settings.GOOGLE_API_KEY
            
            # Initialize the Google Maps client
            gmaps = googlemaps.Client(key=api_key)

            # Construct the full address
            full_address = f"{self.street}, {self.city.name}, {self.state} {self.zip_code}, {self.city.country.name}"
            print("full address:", full_address)

            # Use the Geocoding API to verify the address
            validation_result = gmaps.geocode(full_address)

            # Check if the address is valid
            if validation_result[0].get("partial_match", False):
                return False

            # Ensure required address components exist
            address_components = {comp["types"][0]: comp["long_name"] for comp in validation_result[0]["address_components"]}
            required_components = ["street_number", "route", "locality", "administrative_area_level_1", "country"]

            if not all(comp in address_components for comp in required_components):
                return False
            
            # Get latitude and longitude
            print("validation_result:", validation_result[0]['geometry']['location'])
            self.lat = validation_result[0]['geometry']['location']['lat']
            self.lng = validation_result[0]['geometry']['location']['lng']

            # Reverse Geocode to verify the location is real
            reverse_results = gmaps.reverse_geocode((self.lat, self.lng))
            if not reverse_results or "street_number" not in {comp["types"][0] for comp in reverse_results[0]["address_components"]}:
                return False

            self.save()
            return True
        except Exception as e:
            print(e)
            return False
