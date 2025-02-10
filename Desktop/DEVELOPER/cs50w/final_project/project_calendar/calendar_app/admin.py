from django.contrib import admin

# Register your models here.

from .models import User, Event, Emailsender

class EventAdmin(admin.ModelAdmin):
    list_display = ('id','creator', 'name', 'email', 'start_time', 'end_time', 'date')
    

class EmailAdmin(admin.ModelAdmin):
  list_display = ('account', 'email', 'password', 'specified_time')
  
  

admin.site.register(User)
admin.site.register(Event, EventAdmin)
admin.site.register(Emailsender, EmailAdmin)