from django.views.generic import TemplateView
from django.shortcuts import render
from .models import Engineer
from django.contrib.auth.decorators import login_required

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


#this is apart of testing for the implementation of the video chat
@login_required
def index(request):
    return render(request, 'video_chat/index.html', {})


