from django.views.generic import TemplateView
from django.shortcuts import render

class HomePageView(TemplateView):
    template_name = "home.html"

def myProfile(request):
    context = {}
    return render(request, 'my_profile.html', context)
