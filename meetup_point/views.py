from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.conf import settings

import urllib

import googlemaps
import requests

from meetup_point.models import Address
from meetup_point.service import saveAddress
from meetup_point.service import calculate_midpoint
from meetup_point.service import get_nearby_places
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def meetup_home(request):
    return render(request, 'meetup_point/home.html', {})

@csrf_exempt
def find_halfway_view(request):
    # midpoint = None
    # nearby_places = []
    # return render(request, 'meetup_point/find_meetup_spot.html', {"midpoint": midpoint, "places": nearby_places})

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            addressOne = saveAddress(data.get("addressOne"))
            addressTwo = saveAddress(data.get("addressTwo"))

            print("addressOne", addressOne)
            print("addressTwo", addressTwo)
            if addressOne and addressTwo:
                midpoint = calculate_midpoint(addressOne.lat, addressOne.lng, addressTwo.lat, addressTwo.lng)
                print("midpoint:", midpoint)
            #midpoint = {"lat": 41.8907275, "lng": -87.64590630000001}
            # Fetch nearby places (cafes/restaurants)
            #nearby_places = get_nearby_places(midpoint["lat"], midpoint["lng"], "cafe|restaurant")
            #nearby_places = ["hello"]
            places_query = 'cafe|restaurant'

            # Redirect to the find_meetup_spot view with lat, lng, and places as query parameters - &places={places_query}
            redirect_url = f"/meetup_point/find_meetup_spot/?lat={midpoint['lat']}&lng={midpoint['lng']}&places={places_query}"
            print("redirect_url:", redirect_url)
            return JsonResponse({"redirect_url": redirect_url})
           # return redirect(redirect_url, {"midpoint": midpoint, "places": nearby_places}, permanent=True)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

def find_meetup_spot(request):
    print(request.method)

    # Retrieve the query parameters
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    places_query = request.GET.get('places')
    nearby_places = get_nearby_places(lat, lng, places_query)

    # Get the current authenticated user ID
    user_id = request.user.id

    # Debugging output
    print(f"Latitude: {lat}, Longitude: {lng}")
    print(f"Places query: {places_query}")
    print(f"User ID: {user_id}")

    return render(request, 'meetup_point/find_meetup_spot.html', {
        'lat': lat,
        'lng': lng,
        'nearby_places': nearby_places,
        'api_key': settings.GOOGLE_API_KEY,
        'user_id': user_id
    })

def get_directions_view(request):
    print('get_directions_view')

    print(request)

    # # Retrieve the origin and destination coordinates
    origin = {'lat': request.GET.get('oriLat'), 'lng': request.GET.get('oriLng')}
    destination = {'lat': request.GET.get('destLat'), 'lng': request.GET.get('destLng')}
    api_key = settings.GOOGLE_API_KEY

    def get_directions(origin, destination):
        # Construct the API URL
        url = f"https://routes.googleapis.com/directions/v2:computeRoutes?key={api_key}"

        # Define the request payload
        request_body = {
            "origin": {
                "location": {
                    "latLng": {
                        "latitude": origin.get("lat"),
                        "longitude": origin.get("lng")
                    }
                }
            },
            "destination": {
                "location": {
                    "latLng": {
                        "latitude": destination.get("lat"),
                        "longitude": destination.get("lng")
                    }
                }
            },
            "travelMode": "DRIVE",  # Options: "DRIVE", "WALK", "BICYCLE", "TRANSIT"
            "computeAlternativeRoutes": False,  # Set to True if you want alternative routes
            "routeModifiers": {
                "avoidTolls": False,
                "avoidHighways": False
            }
        }

        # Set the headers
        headers = {
            "Content-Type": "application/json",
            "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline"  # Adding FieldMask header
        }

        # Make the POST request
        response = requests.post(url, headers=headers, data=json.dumps(request_body))

        print('received response', response)
        return response

    # Use the helper function
    response = get_directions(origin, destination)
    request_orig = {
        "lat": 41.8747,
        "lng": -87.6486
    }
    response_request = get_directions(request_orig, destination)

    # Check response
    if response.status_code == 200 and response_request.status_code == 200:
        route_user_data = response.json()
        route_request_data = response_request.json()
        route_data = {
            "user_route": route_user_data.get("routes", []),
            "request_route": route_request_data.get("routes", [])
        }
        return JsonResponse(route_data)
    else:   
        print(f"Error: {response.status_code}")
        print(response.text)