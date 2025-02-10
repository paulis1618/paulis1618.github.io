from django.shortcuts import render
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import Event, User, Emailsender
from django.http import JsonResponse
from datetime import datetime, timedelta, date
import time
import smtplib
from email.message import EmailMessage
# Create your views here.

def index(request):
    return render (request, "calendar.html")

def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")


#log the user out
@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


#register new account
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "register.html")
    
def convert_to_24hr(time_str):
    try:
        time_str = str(time_str)
        time, period = time_str.split()
        hours, minutes = map(int, time.split(':'))
        
        if period.lower() == 'p.m.' and hours != 12:
            hours += 12
        elif period.lower() == 'a.m.' and hours == 12:
            hours = 0
            
        return f"{hours:02d}:{minutes:02d}"
    except:
        return time_str
        
      
    
#create new event
@login_required
def create_event(request):
    if request.method == "POST":
        name2 = request.POST['name']
        email2 = request.POST['email']
        start_time2 = request.POST['start_time']
        end_time2 = request.POST['end_time']
        date2 = request.POST['date']
        creator2 = request.user
        
        
        newevent = Event(
            name = name2,
            email = email2,
            start_time = start_time2,
            end_time = end_time2,
            date = date2,
            creator = creator2
        )
        
        newevent.save()
        
        return HttpResponseRedirect(reverse('index'))

     
    
@login_required
def settings(request):
    if request.method == "GET":
        cur_user = request.user
        credentials = Emailsender.objects.get(account = cur_user)
        #credentials.specified_time = credentials.specified_time.strftime("%I:%M:%S")
        credentials.specified_time = convert_to_24hr(credentials.specified_time)
        return render (request, "settings.html", {
            "values" : credentials
        })
        
    if request.method == "POST":
        newemail = request.POST['newemail']
        newpassword = request.POST['newpassword']
        newtime = request.POST['specified_time']
        cur_user = request.user
        try:
            currentcredits = Emailsender.objects.get(account = cur_user )
            currentcredits.email = newemail
            currentcredits.password = newpassword
            currentcredits.specified_time = newtime
            currentcredits.save()
            return HttpResponseRedirect(reverse("settings"))
            
        except:
            newcredits = Emailsender(
                account = cur_user,
                email = newemail,
                password = newpassword,
                specified_time = newtime,
            )
            newcredits.save()  
            return HttpResponseRedirect(reverse("settings"))
        
        
      
def allevents(request):
    current_user = request.user
    events = Event.objects.filter(creator = current_user)
    allevents = []
    
    for event in events:
        allevents.append({'title': event.name, 'start': f"{event.date}T{event.start_time}", 'end':f"{event.date}T{event.end_time}", 'color': 'blue'})
        
    return JsonResponse(allevents, safe=False)
    return render (request, "experiment.html",{
        "events": allevents
    })
    
def extract_time_using_datetime(datetime_str):
    # Remove the timezone part in parentheses as it's not needed
    cleaned_str = datetime_str.split('(')[0].strip()
    # Parse the datetime string
    dt = datetime.strptime(cleaned_str, '%a %b %d %Y %H:%M:%S GMT%z')
    # Format to get only the time
    return dt.strftime('%H:%M:%S')

def get_event(request, name, start, end ):
    print(start)
    print(end)
    #start = start.strftime("%H:%M")
    cur_user = request.user
    #return JsonResponse({"success"}, safe=False)
    start = extract_time_using_datetime(start)
    end = extract_time_using_datetime(end)
    starttime_object = datetime.strptime(start, '%H:%M:%S')
    endtime_object = datetime.strptime(end, '%H:%M:%S')
    event = Event.objects.get(name = name, creator = cur_user, start_time = starttime_object, end_time = endtime_object)
    
    return JsonResponse({'event_name': event.name, 'event_id':event.id, 'event_start': event.start_time, 'event_end': event.end_time})

def constant_looping(request):
    current_useraki = request.user
    reminder = Emailsender.objects.get(account = current_useraki)
    return reminder.specified_time

def email_alert(current_useraklas, passwrordaki, date, time, to, name):
  email = EmailMessage()
  body = f"Dear {name}, we would like to remind you your appointment for tomorrow, ({date}) at {time}."
  subject = "Appointment Reminder"
  email.set_content(body)

  email['subject'] = subject
  email['to'] = to

  user = current_useraklas
  password = passwrordaki

  server  = smtplib.SMTP('smtp.gmail.com', 587)
  server.starttls()
  server.login(user, password)
  server.send_message(email)
  server.quit()

def get_tomorrows_events(request):
    cur_user = request.user
    #tom_events = Event.objects.filter(st)
    tod = datetime.now().strftime('%d-%m-%Y')
    tomor = date.today() + timedelta(days=1)
    tomor = tomor.strftime('%Y-%m-%d')
    tomor_events = []
    data = Emailsender.objects.get(account = cur_user)
    eventss = Event.objects.filter(creator = cur_user, date = tomor )
    for event in eventss:
        email_alert(data.email, data.password, event.date, event.start_time, event.email, event.name)
    return render(request, "experiment.html",{
        "current": datetime.now().strftime('%d-%m-%Y'),
        "next": tomor,
        "events" : eventss
        
    })
    
#while True:
 #   if datetime.now().strftime('%H:%M:%S') == "14:00:00":
  #      get_tomorrows_events()
#print(datetime.now().strftime('%H:%M:%S'))