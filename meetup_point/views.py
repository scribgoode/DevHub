from django.shortcuts import render

# Create your views here.
def meetup_home(request):
    return render(request, 'meetup_point/home.html', {})