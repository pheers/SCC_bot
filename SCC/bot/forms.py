from django.forms import ModelForm
from bot.models import *

# Create the form class.
class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ['Name', 'Picture', 'Decription', 'Place', 'Direction', 'ManagersName', 'ManagersPhone', 'ManagersEmail']