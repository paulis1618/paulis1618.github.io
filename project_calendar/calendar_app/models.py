from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
  pass


class Event(models.Model):
  name = models.TextField()
  date = models.DateField()
  start_time = models.TimeField()
  end_time = models.TimeField()
  creator = models.ForeignKey(User, on_delete=models.CASCADE)
  email = models.EmailField(default='nikoloupaul@gmail.com')
  phone_number = models.IntegerField(default="6948947751")
  sent_reminder = models.BooleanField(default=False)
  
  
class Emailsender(models.Model):
  account = models.ForeignKey(User, on_delete=models.CASCADE)
  email = models.EmailField()
  password = models.TextField()
  
  
class Day_Checker(models.Model):
  creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
  date = models.DateField()