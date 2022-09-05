from django.forms import ModelForm
from bot.models import *
from django import forms

# Create the form class.
class TeamForm(ModelForm):

    class Meta:
        model = Team
        fields = ['Name', 'Picture', 'Decription', 'Place', 'Direction', 'Vk', 'Contacts', 'Prompt', 'Time']
        widgets = {
            'Decription': forms.Textarea(attrs={'rows': 3}),
            'Prompt': forms.Textarea(attrs={'rows': 1}),
            'Contacts': forms.Textarea(attrs={'rows': 1}),
        }

class DirectionForm(ModelForm):
    class Meta:
        model = Direction
        fields = ['Name']