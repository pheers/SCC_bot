from contextlib import nullcontext
from statistics import mode
from django.db import models

class TgUser(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    Status = models.CharField(max_length=30)

class Direction(models.Model):
    Name = models.CharField(max_length=30)

class Team(models.Model):
    Direction = models.ForeignKey(Direction, on_delete=models.CASCADE)
    Name = models.CharField(max_length=30, unique=True)
    Picture = models.ImageField(upload_to ='photos/')
    Decription = models.CharField(max_length=300)
    Place = models.CharField(max_length=300)
    ManagersName = models.CharField(max_length=30)
    ManagersPhone = models.CharField(max_length=20)
    ManagersEmail =models.CharField(max_length=30)

class Application(models.Model):
    TgUser = models.ForeignKey(TgUser, on_delete=models.CASCADE)
    Name = models.CharField(max_length=100, null=True)
    Phone = models.CharField(max_length=20, null=True)
    Direction = models.ForeignKey(Direction, on_delete=models.CASCADE, null=True)
    Team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    IsViewd = models.BooleanField(default=False)
    IsFinished = models.BooleanField(default=False)

class Date(models.Model):
    Team = models.ForeignKey(Team, on_delete=models.CASCADE)
    DateNTime = models.DateTimeField(max_length=100)