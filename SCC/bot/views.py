from django.shortcuts import render
from django.views import View
from bot.forms import *
from bot.models import *
# Create your views here.

class Main(View):
    def get(self, request):
        context = {"applications": Application.objects.all(), "team_form": TeamForm()}
        return render(template_name='index.html', context = context, request=request)