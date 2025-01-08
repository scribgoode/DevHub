from django.views.generic import TemplateView
from django.shortcuts import render
from .models import Engineer

'''
class HomePageView(TemplateView):
    template_name = "home.html"
'''

def home(request):
    profiles = Engineer.objects.all()
    context = {'profiles': profiles,}
    return render(request, 'home.html', context)

def myProfile(request, id):
    profile = Engineer.objects.get(id=id)
    context = {'profile': profile}
    return render(request, 'my_profile.html', context)


