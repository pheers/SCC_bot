from contextlib import nullcontext
from multiprocessing.dummy import Manager
from statistics import mode
from django.db import models
from django.contrib.auth.models import User

class TgUser(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    Status = models.CharField(max_length=30)
    EditMessId = models.BigIntegerField(null=True)

class Direction(models.Model):
    Name = models.CharField(max_length=30)

    def __str__(self):
        return self.Name

class Team(models.Model):
    Direction = models.ForeignKey(Direction, on_delete=models.CASCADE)
    Name = models.CharField(max_length=300, unique=True)
    Picture = models.ImageField(upload_to ='static/photos/')
    Decription = models.CharField(max_length=2000)
    Place = models.CharField(max_length=300)
    Vk = models.CharField(max_length=300)
    Contacts = models.CharField(max_length=1000)
    Prompt = models.CharField(max_length=2000)
    Time = models.CharField(max_length=300)

class Date(models.Model):
    Date = models.CharField(max_length=300)

class DateTeam(models.Model):
    Team = models.ForeignKey(Team, on_delete=models.CASCADE)
    Date = models.ForeignKey(Date, on_delete=models.CASCADE)


class Application(models.Model):
    TgUser = models.ForeignKey(TgUser, on_delete=models.CASCADE)
    Name = models.CharField(max_length=100, null=True)
    Phone = models.CharField(max_length=20, null=True)
    Direction = models.ForeignKey(Direction, on_delete=models.CASCADE, null=True)
    Team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    Date = models.ForeignKey(Date, on_delete=models.CASCADE, null=True)
    IsViewd = models.BooleanField(default=False)
    IsFinished = models.BooleanField(default=False)


class MessageForDelete(models.Model):
    TgUser = models.ForeignKey(TgUser, on_delete=models.CASCADE)
    mess_id = models.BigIntegerField(null=True)