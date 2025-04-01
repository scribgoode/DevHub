from datetime import datetime
import time
from django.utils.timezone import make_naive, is_aware
from django.urls import reverse
from django.views.generic import TemplateView
from django.template.loader import get_template
from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from .models import Engineer, Project, Reviews
from cities_light.models import City
from text_chat.models import Room, Message
from video_chat.models import Meeting, MeetingRequest, MeetingReview
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from accounts.serializers import EngineerSerializer, RoomSerializer, MessageSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Q
from video_chat.forms import MeetingRequestForm
from django.contrib import messages
from accounts.forms import ProjectCreationForm, EditProfileForm
import requests
from django.db.models import Case, When

from django.utils.timezone import now, activate, localtime
from tzlocal import get_localzone

'''
class HomePageView(TemplateView):
    template_name = "home.html"
'''

def signUp(request):
    return render(request, 'accounts/signup.html')

def login(request): 
    return render(request, 'accounts/login.html')  

def home(request):
    profiles = Engineer.objects.all()
    pitch = request.GET.get('pitch')
    preference = request.GET.get('preference')
    status = request.GET.get('status')
    city = request.GET.get('city') 
    search = request.GET.get('search') 

    if 'search' in request.GET:
        profiles = profiles.filter(Q(first_name__icontains=search) | Q(projects__description__icontains=search))

    if 'city' in request.GET:
        if city != 'any':
            profiles = profiles.filter(city__name=city)

    if 'status' in request.GET:
        #status = request.GET['status'] 
        if status != 'any':
            profiles = profiles.filter(status=status)

    if 'preference' in request.GET:
        #preference = request.GET['preference']
        if preference != 'any':
            profiles = profiles.filter(meeting_preference=preference)
            
    if 'pitch' in request.GET:
        #pitch = request.GET['pitch']
        if pitch == 'true':
            profiles = profiles.filter(elevator_pitch__isnull=False).exclude(elevator_pitch='')
        if pitch == 'false':
            profiles = profiles.filter(Q(elevator_pitch=True) | Q(elevator_pitch=''))

    projects = Project.objects.all()
    cities = City.objects.all()
    context = {'profiles': profiles,
               'cities': cities,
               'status': status,
               'preference': preference,
               'pitch': pitch,
               'city': city,
               'search': search,
               'projects': projects,} 
    
    return render(request, 'home.html', context)

def Profile(request, id):
    if request.method == 'POST':
        meeting_request_form = MeetingRequestForm(request.POST)
        if MeetingRequest.objects.filter(sender=request.user, recipient=Engineer.objects.get(id=id), status="pending").exists():
            messages.warning(request, 'You already have a meeting request pending for this user. You have to wait until they accept, decline, or the date has passed.')
        elif meeting_request_form.is_valid():
            meeting_request = meeting_request_form.save(commit=False)
            meeting_request.sender = request.user
            meeting_request.recipient = Engineer.objects.get(id=id)
            if meeting_request.type == 'in-person':
                # check if both users have addresses
                if request.user.address is not None and Engineer.objects.get(id=id).address is not None:
                    # Convert address objects to JSON-serializable format
                    address_one = {
                        'street': request.user.address.street,
                        'city': {
                            'id': request.user.address.city.id,
                            'name': request.user.address.city.name,
                            'country': {
                                'id': request.user.address.city.country.id,
                                'name': request.user.address.city.country.name
                            }
                        },
                        'state': request.user.address.state,
                        'zip_code': request.user.address.zip_code,
                        'country': {
                            'id': request.user.address.country.id,
                            'name': request.user.address.country.name
                        }
                    }
                    address_two = {
                        'street': Engineer.objects.get(id=id).address.street,
                        'city': {
                            'id': Engineer.objects.get(id=id).address.city.id,
                            'name': Engineer.objects.get(id=id).address.city.name,
                            'country': {
                                'id': Engineer.objects.get(id=id).address.city.country.id,
                                'name': Engineer.objects.get(id=id).address.city.country.name
                            }
                        },
                        'state': Engineer.objects.get(id=id).address.state,
                        'zip_code': Engineer.objects.get(id=id).address.zip_code,
                        'country': {
                            'id': Engineer.objects.get(id=id).address.country.id,
                            'name': Engineer.objects.get(id=id).address.country.name
                        }
                    }

                    # Generate the URL for the find_halfway view
                    find_halfway_url = request.build_absolute_uri(reverse('find_halfway_view'))
                    # Send a POST request to the find_halfway view
                    print('before posting')
                    response = requests.post(
                        find_halfway_url,
                        json={
                            'addressOne': address_one,
                            'addressTwo': address_two
                        }
                    )
                    print('after posting')
                    if response.status_code == 200:
                        data = response.json()
                        redirect_url = f"{data['redirect_url']}?sender={request.user.id}&recipient={Engineer.objects.get(id=id).id}"
                        print('redirect_url:', redirect_url)
                        meeting_request.locationUpdateURL = redirect_url
                        meeting_request.save()
                        return redirect(redirect_url)
                    else:
                        messages.error(request, 'Failed to find halfway point.')
                else:
                    messages.warning(request, 'Both users must have an address to request an in-person meeting.')
            elif meeting_request.type == 'video':
                meeting_request.status = 'pending'
                meeting_request.save()
                return redirect('profile', id=request.user.id)  # Redirect to the profile page after form submission
            else:
                messages.warning(request, 'Meeting request created successfully, but failed to find half way point. THIS SHOULD NOT HAVE HAPPENED!')
                return redirect('profile', id=id)  # Redirect to the profile page after form submission\
            
        if 'favorite' in request.POST:
            current_user = Engineer.objects.get(id=request.user.id)
            current_user.favorites.add(Engineer.objects.get(id=id))
            current_user.save()
            messages.success(request, 'Profile added to favorites.')
            print(current_user.favorites.all(), 'print statement for favorites')
    else:
        meeting_request_form = MeetingRequestForm()

    profile = Engineer.objects.get(id=id)
    projects = Project.objects.filter(pal__id=id)
    context = {'profile': profile,
               'form': meeting_request_form,
               'projects': projects}
    return render(request, 'profile.html', context)

def myProfile(request):
    # Activate the system's timezone
    system_timezone = get_localzone()
    activate(system_timezone)

    # Get the current time in the system's timezone
    current_time = localtime(now())
    current_time_unix = int(time.mktime(current_time.timetuple()))
    print(type(current_time_unix))
    print(current_time_unix)
    print(f"Current Time in {system_timezone}: {current_time}")

    print(request.POST)
    if request.method == 'POST':
        form_type = request.POST.get("form_type")
        print("form type:", form_type)
        if form_type ==  "meeting_request_decision":
            meeting_request = MeetingRequest.objects.get(sender__id=request.POST.get('meeting_request_sender_id'), recipient__id=request.POST.get('meeting_request_recipient_id'), status='pending')
            if request.POST.get('decision') == 'accept':
                #meeting_request = MeetingRequest.objects.get(sender__id=request.POST.get('meeting_request_sender_id'), recipient__id=request.POST.get('meeting_request_recipient_id'), status='pending')
                meeting = Meeting(sender=meeting_request.sender, recipient=meeting_request.recipient, start_time=meeting_request.start_time, end_time=meeting_request.end_time, date=meeting_request.date, description=meeting_request.message, type=meeting_request.type, meeting_request = meeting_request)
                meeting_request.status = MeetingRequest.Status.ACCEPTED

                # Create review object for Meeting
                meeting.review = MeetingReview(review_status=MeetingReview.Status.PENDING, meeting_date=meeting_request.date)
                meeting.review.save()   
                # Ensure meeting.date and meeting.start_time/end_time are valid
                if meeting.date and meeting.start_time and meeting.end_time:
                    # Combine date and time into a datetime object
                    start_datetime = datetime.combine(meeting.date, meeting.start_time)
                    end_datetime = datetime.combine(meeting.date, meeting.end_time)

                # Convert to naive datetime if timezone-aware
                if is_aware(start_datetime):
                    start_datetime = make_naive(start_datetime)
                if is_aware(end_datetime):
                    end_datetime = make_naive(end_datetime)


                # Convert to Unix timestamps
                meeting.start_time_unix = int(time.mktime(start_datetime.timetuple()))
                meeting.end_time_unix = int(time.mktime(end_datetime.timetuple()))

                meeting_request.save()
                meeting.save()
            elif request.POST.get('decision') == 'decline':
                #meeting_request = MeetingRequest.objects.get(sender__id=request.POST.get('meeting_request_sender_id'), recipient__id=request.POST.get('meeting_request_recipient_id'), status='pending')
                meeting_request.status = MeetingRequest.Status.DECLINED
                meeting_request.save()
                meeting = Meeting(sender=meeting_request.sender, recipient=meeting_request.recipient, start_time=meeting_request.start_time, end_time=meeting_request.end_time, date=meeting_request.date, description=meeting_request.message, type=meeting_request.type, meeting_request = meeting_request, status=Meeting.Status.DECLINED)
                meeting.save()
            elif request.POST.get('decision') == 'reschedule':
                meeting_request.status = MeetingRequest.Status.RESCHEDULED
                meeting_request.save()
                meeting = Meeting(sender=meeting_request.sender, recipient=meeting_request.recipient, start_time=meeting_request.start_time, end_time=meeting_request.end_time, date=meeting_request.date, description=meeting_request.message, type=meeting_request.type, meeting_request = meeting_request, status=Meeting.Status.RESCHEDULED)
                meeting.save()
                return redirect('profile', id=request.POST.get('meeting_request_sender_id'))
        if form_type == "video_upload":
            user = request.user
            user.elevator_pitch = request.FILES['elevator_pitch']
            user.save()
        if form_type == "video_remove":
            user = request.user
            user.elevator_pitch.delete()
        if form_type == "add_project":
            form = ProjectCreationForm(request.POST)
            if form.is_valid:
                project = form.save(commit=False)
                project.pal = request.user
                project.save()
        if form_type == "edit_profile_info":
            form = EditProfileForm(request.POST, instance=request.user)
            if form.is_valid:
                user = form.save(commit=False)
                user.save()
       
        # meeting review form submission
        if form_type == 'meeting-review-form':
            reviewee_id = request.POST.get('reviewee_id')
            reviewee = Engineer.objects.get(id=reviewee_id)
            meeting_type = request.POST.get('meeting_type')
            print('meeting_type:', meeting_type)
            print('reviewee:', reviewee.first_name)
            meeting = Meeting.objects.get(id=request.POST.get('meeting_id'))
            # Determine if the reviewee is the sender or recipient
            reviewee_role = None
            if meeting.sender == reviewee:
                reviewee_role = 'sender'
            elif meeting.recipient == reviewee:
                reviewee_role = 'recipient'
 
            if request.POST.get('pal_attendance') == 'yes':
                print('meeting success')
                # moderation on review and rating (prevent spam, etc.)
                
                # check if review has been created
                if meeting.review:
                    # Update the existing review
                    review = meeting.review
                    if reviewee_role == 'sender':
                        review.sender_review = request.POST.get('meeting_feedback')
                        review.sender_rating = request.POST.get('pal_rating')
                        review.recipient_status = MeetingReview.Status.REVIEWED
                    elif reviewee_role == 'recipient':
                        review.recipient_review = request.POST.get('meeting_feedback')
                        review.recipient_rating = request.POST.get('pal_rating')
                        review.sender_status = MeetingReview.Status.REVIEWED
                    
                    # Check if both users has submitted their reviews
                    if review.sender_status == MeetingReview.Status.REVIEWED and review.recipient_status == MeetingReview.Status.REVIEWED:
                        # Update the review status to reviewed
                        print('both users have reviewed')   
                        meeting.review.review_status = MeetingReview.Status.REVIEWED
                        meeting.status = Meeting.Status.COMPLETED # update meeting to completed, it will not show up in the upcoming meetings
                        meeting.acknowledged = True # mark meeting as acknowledged
                        meeting.save()
                        meeting.refresh_from_db()
                        print(f"Refreshed status: {meeting.status}")  # Debugging
                    review.save()
                
                else:
                    # Create a new review (but should not go to this as we create the meeting review when the meeting is REVIEW status)
                    if reviewee_role == 'sender':
                        review = MeetingReview(recipient_review=request.POST.get('meeting_feedback'), recipient_rating=request.POST.get('rating'), meeting_date=meeting.date, submitted_date=datetime.now(), recipient_status=MeetingReview.Status.REVIEWED, review_status=MeetingReview.Status.PENDING)
                    elif reviewee_role == 'recipient':
                        review = MeetingReview(sender_review=request.POST.get('meeting_feedback'), sender_rating=request.POST.get('rating'), meeting_date=meeting.date, submitted_date=datetime.now(), sender_status=MeetingReview.Status.REVIEWED, review_status=MeetingReview.Status.PENDING)
                    review.save()
                    
                    # Associate the review with the meeting
                    meeting.review = review
                    meeting.save()
             
            elif request.POST.get('pal_attendance') == 'no':
                print('meeting not success')
                # moderation on review and rating (prevent spam, etc.)

            return redirect('/my-profile/')
            # Save the review and rating to the user
            reviewee.rating_count += 1
            reviewee.rating = (reviewee.rating + int(rating)) / reviewee.rating_count # should update system

            # Update reviewee's meeting stats (though I am hesisitant to do this - should we have the count go up after a review is submmited?)
            reviewee.NumMeetings += 1
            # check if online or inperson meeting
            reviewee.NumMeetings += 1; reviewee.NumVideoMeetings += (meeting_type == 'video'); reviewee.NumInPersonMeetings += (meeting_type == 'in-person')

            # Save the review and rating to the user
            reviewee.save()

            # Update meeting status
            meeting = Meeting.objects.get(id=request.POST.get('meeting_id'))
            meeting.status = Meeting.Status.COMPLETED
            meeting.save()

            # Review Object
            review = Reviews(reviewer=request.user, reviewee=reviewee, meeting=meeting, review=review, rating=rating, meeting_date=meeting.date, submitted_date=datetime.now())
            review.save()

            print('Meeting marked as unsuccessful with review and rating saved.')
        elif form_type == 'acknowledge_meeting':
            meeting = Meeting.objects.get(id=request.POST.get('meeting_id'))
            meeting.acknowledged = True
            meeting.save()
            print(f'meeting marked as {meeting.status}')
        
        elif form_type == 'cancel-meeting-form': # Happens when someone cancels the meeting
            cancel_reason = request.POST.get('cancel_reason', None)
            if cancel_reason is not None:
                meeting = Meeting.objects.get(id=request.POST.get('meeting_id'))
                print(meeting)
                
                meeting.cancel_user = Engineer.objects.get(id=request.POST.get('cancel_user'))
                meeting.status = Meeting.Status.CANCELLED
                meeting.meeting_request.status = MeetingRequest.Status.CANCELLED
                meeting.cancel_reason = cancel_reason
                meeting.save()
        elif form_type == 'cancel_sent_request': # Happens only when sender cancels the request
            meeting_request = MeetingRequest.objects.get(id=request.POST.get('sent_meeting_id'))
            meeting_request.status = MeetingRequest.Status.CANCELLED
            meeting_request.save()
            meeting = Meeting(sender=meeting_request.sender, recipient=meeting_request.recipient, start_time=meeting_request.start_time, end_time=meeting_request.end_time, date=meeting_request.date, description=meeting_request.message, type=meeting_request.type, meeting_request = meeting_request, status=Meeting.Status.CANCELLED)
            meeting.acknowledged = True # mark meeting as acknowledged as request was cancelled
            meeting.save()
        else:
            print('did not get meeting_success msg. something went wrong')


    meetings = Meeting.objects.filter( Q(recipient=request.user) | Q(sender=request.user) )
    
    # Create a dictionary to track if the user has reviewed each meeting
    has_reviewed = {}

    # Update meeting status based on current time
    for meeting in meetings:
        if meeting.status == Meeting.Status.COMPLETED or meeting.status == Meeting.Status.DECLINED or meeting.status == Meeting.Status.CANCELLED or meeting.status == Meeting.Status.RESCHEDULED:
            continue
        
        if meeting.start_time_unix <= current_time_unix <= meeting.end_time_unix:
            meeting.status = Meeting.Status.ONGOING
            meeting.save()
        elif meeting.end_time_unix < current_time_unix:
            meeting.status = Meeting.Status.REVIEWING
            # Create review object if it doesn't exist
            if meeting.review is None:
                review = MeetingReview(review_status=MeetingReview.Status.PENDING, meeting_date=meeting.date)
                review.save()
                meeting.review = review
                meeting.save()
        if meeting.review:
            has_reviewed[meeting.id] = meeting.review.has_reviewed(request.user.id, "sender" if meeting.sender.id == request.user.id else "recipient")  # check if the user has reviewed the meeting
        else:
            has_reviewed[meeting.id] = False  # Default to False if no review exists
        meeting.save()  
    print("aftr filter")
    # Sort meetings by status priority
    meetings = meetings.annotate(
        status_order=Case(
            When(status=Meeting.Status.ONGOING, then=1),
            When(status=Meeting.Status.REVIEWING, then=2),
            When(status=Meeting.Status.UPCOMING, then=3),
            When(status=Meeting.Status.CANCELLED, then=4),
            When(status=Meeting.Status.DECLINED, then=5),
            When(status=Meeting.Status.COMPLETED, then=6),
            default=7
        )
    ).order_by('status_order', 'date', 'start_time')

    
    meeting_requests = MeetingRequest.objects.filter( Q(recipient=request.user) | Q(sender=request.user) ) #maybe make meeting_requests and sent_meetings_requests
    meeting_requests = meeting_requests.order_by('date', 'start_time')
    
    sent_meetings = MeetingRequest.objects.filter(sender=request.user)
    sent_meetings = sent_meetings.annotate(
        status_order=Case(
            When(status='pending', then=1),
            When(status='accepted', then=2),
            When(status='rescheduled', then=3),
            When(status='declined', then=4),
            default=5
        )
    ).order_by('status_order')
    projects = Project.objects.filter(pal=request.user)
    project_creation_form = ProjectCreationForm()
    edit_profile_info_form = EditProfileForm(instance=request.user)

    context = {'meetings': meetings,
                'meeting_requests': meeting_requests,
                'sent_meetings': sent_meetings,
                'projects': projects,
                'now': current_time_unix,
                'has_reviewed': has_reviewed,
                'project_creation_form': project_creation_form,
               'edit_profile_info_form': edit_profile_info_form,
               }

    return render(request, 'my_profile.html', context)

@api_view(['GET'])
@permission_classes([IsAdminUser])  # Only admin users can access this view
def profile_list(request):
    profiles = Engineer.objects.all()
    serializer = EngineerSerializer(profiles, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def profile_detail(request, pk):
    profile = get_object_or_404(Engineer, pk=pk)
    serializer = EngineerSerializer(profile)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])  # Only admin users can access this view
def room_list(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_room(request, pk):
    rooms = Room.objects.filter(users__id=pk)
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])  # Only admin users can access this view
def message_list(request):
    message_list = Message.objects.all()
    serializer = MessageSerializer(message_list, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_chat(request, pk):
    messages = Message.objects.filter(room_id=pk)
    print(messages)
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)

#this is apart of testing for the implementation of the video chat
@login_required
def index(request):
    return render(request, 'video_chat/index.html', {})


@login_required
def videoChat(request, room_token):
    meeting = Meeting.objects.get(room_token=room_token)
    context = {'room_token': room_token,
                'meeting': meeting,
               }
    return render(request, 'video_chat/video_chat.html', context)

'''
@login_required
def videoChat(request):
    return render(request, 'video_chat/video_chat.html', {})
'''

