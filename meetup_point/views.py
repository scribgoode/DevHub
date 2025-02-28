from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from meetup_point.models import Address
from meetup_point.service import saveAddress
from meetup_point.service import calculate_midpoint

# Create your views here.
def meetup_home(request):
    return render(request, 'meetup_point/home.html', {})

@csrf_exempt
def find_halfway_view(request):
    if request.method == "POST":
        try:
            data = json.dumps(request.body)
            
            adressOne = saveAddress(data.get("addressOne"))
            addressTwo = saveAddress(data.get("addressTwo"))

            if adressOne and addressTwo:
                midpoint = calculate_midpoint(adressOne.lat, adressOne.lng, addressTwo.lat, addressTwo.lng)
                print(midpoint)
            


            return JsonResponse({"message": "Address saved successfully"}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        