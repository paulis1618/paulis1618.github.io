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
  
  
class Emailsender(models.Model):
  account = models.ForeignKey(User, on_delete=models.CASCADE)
  email = models.EmailField()
  password = models.TextField()
  specified_time = models.TimeField()