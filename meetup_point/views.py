from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

import urllib
from meetup_point.models import Address
from meetup_point.service import saveAddress
from meetup_point.service import calculate_midpoint
from meetup_point.service import get_nearby_places

# Create your views here.
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
            print('after finding midpoint')
            # Fetch nearby places (cafes/restaurants)
            #nearby_places = get_nearby_places(midpoint["lat"], midpoint["lng"], "cafe|restaurant")
            #nearby_places = ["hello"]
            places_query = 'cafe|restaurant'

            # Redirect to the find_meetup_spot view with lat, lng, and places as query parameters - &places={places_query}
            redirect_url = f"/meetup_point/find_meetup_spot/?lat={midpoint['lat']}&lng={midpoint['lng']}&places={places_query}"
        
            print(type(redirect_url))
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

    # Debugging output
    print(f"Latitude: {lat}, Longitude: {lng}")

    return render(request, 'meetup_point/find_meetup_spot.html', {
        'lat': lat,
        'lng': lng,
        'nearby_places': nearby_places,
    })
