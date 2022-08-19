from django.shortcuts import render
from django.views import View
from bot.forms import *
from bot.models import *
from django.http import JsonResponse
from datetime import datetime, tzinfo
from django.utils.timezone import utc
import json
import re
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import redirect
# Create your views here.

class Main(View):
    def get(self, request):
        if request.user.is_authenticated:
            context = {"applications": Application.objects.filter(IsFinished=True), "team_form": TeamForm(), "teams": Team.objects.all(), "direction_form": DirectionForm(), "directions": reversed(Direction.objects.all())}
            return render(template_name='index.html', context = context, request=request)
        else:
            return redirect("/login")            

class Login(View):
    def get(self, request):
        return render(template_name='login.html', request=request)

    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect("/main")
        else:
            return render(template_name='login.html', context = {"error": "Неправильный логин или пароль"}, request=request)
class Applications(View):
    def get(self, request):
        if request.user.is_authenticated:
            return JsonResponse({"applications": list(Application.objects.filter(IsFinished=True).values('id', 'Name', 'Phone', 'Direction__Name', 'Team__Name', 'Date__DateNTime'))})
        else:
            return redirect("/login")

class Directions(View):
    def get(self, request):
        if request.user.is_authenticated:
            return JsonResponse({"directions": list(Direction.objects.all().values('id', 'Name'))})

        else:
            return redirect("/login")

    def post(self, request):
        print(request.body)
        dir = Direction.objects.create(Name = json.loads(request.body)['name'])
        dir.save()
        return JsonResponse({"id": dir.id, "Name": dir.Name})

    def delete(self, request):
        return JsonResponse({'deleted': Direction.objects.get(id=request.GET.get('id')).delete()})

class Teams(View):
    def get(self, request):
        return JsonResponse({"teams": list(Team.objects.all().values('id', "Direction", "Name", "Picture", "Decription", "Place", "ManagersName", "ManagersPhone", "ManagersEmail"))})    
    
    def post(self, request):
        form = TeamForm(request.POST, request.FILES)
        print(form.is_valid())
        if form.is_valid():
            print(request.POST.getlist("DateTime"))
            team = form.save()
            if re.match(r'^((8|\+7)?[\- ]?)\(?(\d{3})\)?[\- ]?(\d{3})[\- ]?(\d{2})[\- ]?(\d{2})$', team.ManagersPhone) is not None:
                groups = re.match(r'^((8|\+7)?[\- ]?)\(?(\d{3})\)?[\- ]?(\d{3})[\- ]?(\d{2})[\- ]?(\d{2})$', team.ManagersPhone).groups()
                print(groups)
                team.ManagersPhone = f'+7({groups[2]}){groups[3]}-{groups[4]}-{groups[5]}'
            team.save()
            
            for dt in request.POST.getlist("DateTime"):
                print(dt)
                new_date = Date.objects.create(Team = team, DateNTime = datetime.fromisoformat(dt))
                new_date.save()
            
            return JsonResponse({"team": {'id': team.id, "Direction": team.Direction.Name, "Name": team.Name, "Picture": team.Picture.url, "Decription": team.Decription, "Place": team.Place, "ManagersName": team.ManagersName, "ManagersPhone": team.ManagersPhone, "ManagersEmail": team.ManagersEmail}})
        context = {"applications": Application.objects.filter(IsFinished=True), "team_form": form, "teams": Team.objects.all(), "direction_form": DirectionForm(), "directions": reversed(Direction.objects.all())}
        return render(template_name='index.html', context = context, request=request)

    def delete(self, request):
        return JsonResponse({'deleted': Team.objects.get(id=request.GET.get('id')).delete()})
        