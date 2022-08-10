from django.core.management.base import BaseCommand
from django.conf import settings
import telebot
import re
from bot.models import *
bot = telebot.TeleBot(settings.TELEGRAM_BOT_API_KEY)


# Название класса обязательно - "Command"
class Command(BaseCommand):
  	# Используется как описание команды обычно
    help = 'Implemented to Django application telegram bot setup command'
    
    def handle(self, *args, **options):
      @bot.message_handler(content_types=['text'])
      def get_text_messages(message):
        user, isExist = TgUser.objects.get_or_create(id = message.from_user.id)
        application= Application.objects.get_or_create(TgUser = user, IsFinished = False)[0]
        
        print(user.Status)
        # Team.objects.create(Name="Иванушки Интэрнэшнл", Direction = Direction.objects.all()[0], Place="Органный зал", ManagersName="Аставьева Зинаида Олеговна", ManagersPhone="+7(923)172-49-14", ManagersEmail = "email@email.com")
        if message.text == "/start":
          user.Status = "Выбор направления"
          user.save()
          if isExist:
            bot.send_message(message.from_user.id, "Привет! Здесь ты можешь записаться на кастинг :)")
          kb = telebot.types.ReplyKeyboardMarkup(row_width=2)
          for direction in Direction.objects.all():
            btn = telebot.types.KeyboardButton(direction.Name)
            kb.add(btn)
          bot.send_message(message.from_user.id, "Выбери интересующее тебя направление", reply_markup = kb)
        elif user.Status == "Выбор направления":
          try:
            direction = Direction.objects.get(Name = message.text)
            application.TgUser = user
            application.Direction = direction
            application.save()
            kb = telebot.types.ReplyKeyboardMarkup(row_width=2)
            for team in Team.objects.filter(Direction = direction):
              btn = telebot.types.KeyboardButton(team.Name)
              kb.add(btn)
            user.Status = "Выбор коллектива"
            user.save()
            bot.send_message(message.from_user.id, "Отлично! Теперь выбери коллектив", reply_markup = kb)
          except Exception as e:
            print(e)
            bot.send_message(message.from_user.id, "Неверный формат введенных данных. Попробуй еще раз)")
        elif user.Status == "Выбор коллектива":
          try:
            team = Team.objects.get(Name = message.text)
            application.Team = team
            application.save()
            user.Status = "Ввод ФИО"
            user.save()
            bot.send_message(message.from_user.id, "Напишите ваше ФИО", reply_markup = telebot.types.ReplyKeyboardMarkup())
          except:
            bot.send_message(message.from_user.id, "Неверный формат введенных данных. Попробуй еще раз)")
        elif user.Status == "Выбор Даты":
          pass
        elif user.Status == "Ввод ФИО":
          if re.match(r'[А-Я][а-я]*\s[А-Я][а-я]*\s[А-Я][а-я]*$', message.text) is not None:
            application.Name = message.text
            application.save()
            user.Status = "Ввод телефона"
            user.save()
            bot.send_message(message.from_user.id, "Напишите ваш контактный номер телефона")
          else:
            print(message.text)
            bot.send_message(message.from_user.id, "Неверный формат введенных данных. Попробуй еще раз)")
        elif user.Status == "Ввод телефона":
          if re.match(r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$', message.text) is not None:
            application.Phone = message.text
            application.IsFinished = True
            application.save()
            user.Status = ""
            user.save()
            bot.send_message(message.from_user.id, "Ваша заявка принята!")
          else:
            print(message.text)
            bot.send_message(message.from_user.id, "Неверный формат введенных данных. Попробуй еще раз)")
        else:
          bot.send_message(message.from_user.id, "Чтобы начать напишите /start")


      bot.polling(none_stop=True, interval=0)