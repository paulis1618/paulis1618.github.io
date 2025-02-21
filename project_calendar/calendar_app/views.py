from django.shortcuts import render
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import Event, User, Emailsender, Day_Checker
from django.http import JsonResponse
from datetime import datetime, timedelta, date
import time
import smtplib
from email.message import EmailMessage
import requests
import random
import pytz

# Create your views here.


#returns the calendar page if user is logged in and log in page otherwise
def index(request):
    if request.user.is_authenticated:
        return render (request, "calendar.html")
    else:
        return render(request, "login.html")

#login
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
            yesterd = date.today() + timedelta(days=-1)
            daycheck = Day_Checker(
                creator = user,
                date = yesterd.strftime('%Y-%m-%d')
            )
            daycheck.save()
        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "register.html")
    

#gets an time string and converts it to the appropriate time format
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
    #gets the posted elements of the form
    if request.method == "POST":
        name2 = request.POST['name']
        phone_num = request.POST['phone_number']
        #email2 = request.POST['email']
        start_time2 = request.POST['start_time']
        end_time2 = request.POST['end_time']
        date2 = request.POST['date']
        creator2 = request.user
        
        #creates the new event
        newevent = Event(
            name = name2,
            #email = email2,
            email = 'nikoloupaul@gmail.com',
            phone_number = phone_num,
            start_time = start_time2,
            end_time = end_time2,
            date = date2,
            creator = creator2
        )
        #saves the event
        newevent.save()
        
        return HttpResponseRedirect(reverse('index'))

     
#anything about the settings page
@login_required
def settings(request):
    #if the method is get returns the settings page
    if request.method == "GET":
        cur_user = request.user
        try:
            #trys to get the emailsender(it is the initial value for the form)
            credentials = Emailsender.objects.get(account = cur_user)
            #returns the page with the appropriate initial values
            return render (request, "settings.html", {
            "values" : credentials
        })
        except:
            #if it is the first time the user visits this page the inital values are empty and don't exist so the previous try raises an error, it comes here and we return the settings page, whithout an initial value for the forms' elements
            return render (request, "settings.html")
        
    #if the method is post, meaning the user submits the form and updates his reminder email and reminder password
    if request.method == "POST":
        #gets the posted data from the form 
        newemail = request.POST['newemail']
        newpassword = request.POST['newpassword']
        #newtime = request.POST['specified_time']
        cur_user = request.user
        try:
            #try to get the emailsender by its user and update the password and email according to the values submitted
            currentcredits = Emailsender.objects.get(account = cur_user )
            currentcredits.email = newemail
            currentcredits.password = newpassword
            #currentcredits.specified_time = newtime
            currentcredits.save()
            return HttpResponseRedirect(reverse("settings"))
            
        except:
            #if the user hasn't submitted the form before, the emailsender for him doesn't exist and trying to get it will raise an error 
            #so in that case we create the new emailsender
            newcredits = Emailsender(
                account = cur_user,
                email = newemail,
                password = newpassword,
                #specified_time = newtime,
            )
            newcredits.save()  
            return HttpResponseRedirect(reverse("settings"))

def random_color():
    colors = ['green','BlueViolet', 'DarkCyan', 'DarkMagenta', 'DarkRed', 'Indigo', 'Teal', 'Maroon', 'Thistle', 'SeaGreen', 'Salmon', 'Navy','DarkSlateGray', 'DarkSeaGreen', 'DodgerBlue', 'HotPink',  'DimGray', 'DarkSlateGrey' 'blue', 'black', 'darkblue', 'darkgrey' 'orange', 'purple']
    return random.choice(colors)

@login_required        
#gets all events of a user and returns a list of them that is added to the calendar
def allevents(request):
    current_user = request.user
    events = Event.objects.filter(creator = current_user)
    allevents = []
    
    for event in events:
        allevents.append({'title': event.name, 'phone_number': event.phone_number, 'start': f"{event.date}T{event.start_time}", 'end':f"{event.date}T{event.end_time}", 'color': random_color()})
        
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

@login_required
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
    
    return JsonResponse({'event_name': event.name, 'event_id':event.id, 'event_start': event.start_time, 'event_end': event.end_time, 'event_date': event.date, 'event_email':event.email, 'event_phone_number': event.phone_number})


#sends the email
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

def send_sms(username, time, to, phonenumber):
    # Define the base URL
    url = "https://smsb2b.com/api/sms/send"
    
    # Set the query parameters as a dictionary
    params = {
        "key": "cdc29b5e7dc348c",
        "text": f"Καλησπέρα! Σας υπενθυμιζω το ραντεβου, αύριο στις {time}. {username} Τηλ.{phonenumber}",
        "from": username,
        "to": f"{to}",
        "type": "json"
    }
    
    # Send the GET request with the parameters
    response = requests.get(url, params=params)
    
    # Raise an exception if the request did not succeed
    response.raise_for_status()
    
    # Return the JSON response (or you could print it, depending on your needs)
    return response.json()



@login_required
#gets all events of the current user, scheduled for tomorrow, and for each sends an email to the person we are meeting with to remind him the time of our appointment
def get_the_events(request):
    
    cur_user = request.user
    onomataki = cur_user.username
    #tom_events = Event.objects.filter(st)
    tod = datetime.now(pytz.timezone('Europe/Athens')).strftime('%d-%m-%Y')
    paulis_kaulis = datetime.now(pytz.timezone('Europe/Athens')).strftime('%Y-%m-%d')
    #tomor = date.today() + timedelta(days=1)
    tomor =  datetime.now(pytz.timezone('Europe/Athens')).date() + timedelta(days=1)
    tomor = tomor.strftime('%Y-%m-%d')
    
    

    day_checker = Day_Checker.objects.get(creator = cur_user)
    last_time = day_checker.date.strftime('%d-%m-%Y')
    #trys to get the emailsender of the current user, if it exists of course
    try:
        data = Emailsender.objects.get(account = cur_user)
        #if this condition is true we have allready sent the reminder for tomorrow
        if last_time == tod:
            print(last_time)
            print(tod)
            return JsonResponse({'status':'Error, allready sent reminders for tomorrow'})
        #if this condition is true, our email credentials are mepty and we cant send emails
        elif data.email=="" or data.password=="":
            return JsonResponse({'status':'Error, you did not fill out your email credentials'})
        #if none of the previous conditions are true we come here and send email for each person we are meeting with tomorrow
        else:
            print(last_time)
            print(tod)
            #tod = tod.strftime('%Y-%m-%d')
            day_checker.date = paulis_kaulis
            print(f"Today is {tod}")
            print(f"Time is {paulis_kaulis}")
            print(f"Tomorrow is {tomor}")
            day_checker.save()
            #data = Emailsender.objects.get(account = cur_user)
            eventss = Event.objects.filter(creator = cur_user, date = tomor )
            for event in eventss:
                #if event.sent_reminder == False:
                #send_sms(onomataki, event.start_time, event.phone_number, "6948947751" )
                    email_alert(data.email, data.password, event.date, event.start_time, event.email, event.name)
                    event.sent_reminder = True
                    event.save()
                    print(datetime.now(pytz.timezone('Europe/Athens')))
                #else: 
                    print(event.sent_reminder)
                    print(datetime.now(pytz.timezone('Europe/Athens')))
                #return render(request, "experiment.html",{
                ##    "current": datetime.now().strftime('%d-%m-%Y'),
                #    "next": tomor,
                #    "events" : eventss
                #   
                #})
                #def send_sms(username, time, to, phonenumber):
            return JsonResponse({'status':'All reminders have been sent out successfully!!!'})
    #if we haven't created the emailsender credentials(which means we haven't submitted the form in settings) trying to get them will raise an error.
    #then we come here and we give an alert
    except:
            return JsonResponse({'status':'Error, there is something wrong with your email credentials'})


@login_required 
#gets called when we want to edit an existing post
def editevent(request):
    if request.method == "POST":
        event_id = request.POST['eventId']
        event_name = request.POST['edit_name']
        #event_email = request.POST['edit_email']
        event_phone_number = request.POST['edit_phone_number']
        event_start = request.POST['edit_start_time']
        event_end = request.POST['edit_end_time']
        event_date = request.POST['edit_date']
        
        eventaki = Event.objects.get(pk = event_id)
        
        eventaki.name = event_name
        #eventaki.email = event_email
        eventaki.start_time = event_start
        eventaki.end_time = event_end
        eventaki.date = event_date
        eventaki.phone_number = event_phone_number
        
        eventaki.save()
        return HttpResponseRedirect(reverse('index'))
        return render(request, "experiment.html",{
            "event": eventaki
        })
    
@login_required    
#deletes an event from our database
def deleteevent(request, event_id):
    event = Event.objects.get(pk = event_id)
    event.delete()
    return JsonResponse({'status': 'success'})




#while True:
 #   if datetime.now().strftime('%H:%M:%S') == "14:00:00":
  #      get_tomorrows_events()
#print(datetime.now().strftime('%H:%M:%S'))


#scheduled_time = "00:20"
#schedule.every().day.at(scheduled_time).do(get_tomorrows_events())


# Keep the script running indefinitely so that scheduled tasks can be executed.
#while True:
 #   schedule.run_pending()  # Check if any scheduled tasks are pending to run
 #   time.sleep(60)      