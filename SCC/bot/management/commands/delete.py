from bot.models import *
from django.core.management.base import BaseCommand

class Command(BaseCommand):
  	# Используется как описание команды обычно
    help = 'Implemented to Django application telegram bot setup command'
    
    def handle(self, *args, **options):
        for user in TgUser.objects.all():
            user.delete()
        for application in Application.objects.all():
            application.delete()
