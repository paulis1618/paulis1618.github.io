from django.contrib import admin

# Register your models here.

from .models import User, Event, Emailsender, Day_Checker

class EventAdmin(admin.ModelAdmin):
    list_display = ('id','creator', 'name', 'email', 'start_time', 'end_time', 'date', 'phone_number', 'sent_reminder')
    

class EmailAdmin(admin.ModelAdmin):
  list_display = ('account', 'email', 'password')
  
class Day_checkerAdmin(admin.ModelAdmin): 
  list_display = ('creator', 'date') 

admin.site.register(User)
admin.site.register(Event, EventAdmin)
admin.site.register(Emailsender, EmailAdmin)
admin.site.register(Day_Checker, Day_checkerAdmin)
