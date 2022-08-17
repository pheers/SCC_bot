from random import randint
from tkinter.messagebox import NO
from tokenize import group, triple_quoted
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
      bot.polling(none_stop=True, interval=0)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
  user, isExist = TgUser.objects.get_or_create(id = message.from_user.id)
  application = Application.objects.get_or_create(TgUser = user, IsFinished = False)[0]
  for mess in MessageForDelete.objects.filter(TgUser = user):
    print(mess.mess_id)
    try:
      bot.delete_message(message.from_user.id, mess.mess_id)
    except:
      pass
    mess.delete()
  print(user.Status)
  if message.text == "/start":
    user.Status = "Выбор направления"
    user.save()
    if isExist:
      bot.send_message(message.from_user.id, "Привет! Здесь вы можете записаться на кастинг :)", reply_markup=telebot.types.ReplyKeyboardRemove(selective=False))
      #MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
    kb = telebot.types.InlineKeyboardMarkup()
    for direction in Direction.objects.all():
      btn = telebot.types.InlineKeyboardButton(direction.Name, callback_data=direction.id)
      kb.add(btn)
    print(len(kb.keyboard)>0)
    kb = kb if len(kb.keyboard)>0 else telebot.types.ReplyKeyboardRemove(selective=False)
    res = bot.send_message(message.from_user.id, "Выберите интересующее Вас направление", reply_markup = kb)
    MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
  elif user.Status == "Ввод ФИО":
      application.Name = message.text
      application.save()
      user.Status = "Ввод телефона"
      user.save()
      res = bot.send_message(message.from_user.id, "Напишите ваш контактный номер телефона", reply_markup=telebot.types.ReplyKeyboardRemove(selective=False))
      MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
  elif user.Status == "Ввод телефона":
    if re.match(r'^((8|\+7)?[\- ]?)\(?(\d{3})\)?[\- ]?(\d{3})[\- ]?(\d{2})[\- ]?(\d{2})$', message.text) is not None:
      groups = re.match(r'^((8|\+7)?[\- ]?)\(?(\d{3})\)?[\- ]?(\d{3})[\- ]?(\d{2})[\- ]?(\d{2})$', message.text).groups()
      application.Phone = f'+7({groups[2]}){groups[3]}-{groups[4]}-{groups[5]}'
      application.save()
      user.Status = "Подтверждение"
      user.save()
      kb = telebot.types.InlineKeyboardMarkup()
      kb.add(telebot.types.InlineKeyboardButton("Отмена", callback_data="cancel"))
      kb.add(telebot.types.InlineKeyboardButton("Отправить", callback_data="send"))
      res = bot.send_message(message.from_user.id, f'*Направление*: {application.Direction.Name}\n*Коллектив*: {application.Team.Name}\n*Дата в время*: {application.Date.DateNTime.strftime("%m.%d - %H:%M")}\n*ФИО*: {application.Name}\n*Номер телефона*: {application.Phone}\nОтправить Вашу заявку?', reply_markup=kb, parse_mode="Markdown")
      MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
    else:
      print(message.text)
      res = bot.send_message(message.from_user.id, "Неверный формат введенных данных. Попробуй еще раз)")
      MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
  else:
    res = bot.send_message(message.from_user.id, "Чтобы начать напишите /start", reply_markup=telebot.types.ReplyKeyboardRemove(selective=False))
    MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
  
  bot.delete_message(message.from_user.id, message.message_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
  try:
      if call.message:
          print(call.message.from_user.id)
          user, isExist = TgUser.objects.get_or_create(id = call.message.chat.id)
          application = Application.objects.get_or_create(TgUser = user, IsFinished = False)[0]
          for mess in MessageForDelete.objects.filter(TgUser = user):
            try:
              bot.delete_message(call.message.chat.id, mess.mess_id)
            except:
              pass
            mess.delete()

          if user.Status == "Выбор направления":
            try:
                direction = Direction.objects.get(id = call.data)
                application.Direction = direction
                application.save()
                user.Status = "Выбор коллектива"
                user.save()
                ikb = telebot.types.InlineKeyboardMarkup()
                ikb.add(telebot.types.InlineKeyboardButton("← Выбрать другое направление", callback_data="back"))
                for team in Team.objects.filter(Direction = application.Direction):
                  ikb.add(telebot.types.InlineKeyboardButton(team.Name, callback_data=team.id))
                res = bot.send_message(call.message.chat.id, "Выберите коллектив", reply_markup = ikb)
                MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
            except Exception as e:
                print(e)
                res = bot.send_message(call.message.chat.id, "Произошла ошибка, попробуте начать сначала(/start)")
                
                MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
          elif user.Status == "Выбор коллектива":
            if call.data == "back":
              user.Status = "Выбор направления"
              user.save()
              kb = telebot.types.InlineKeyboardMarkup()
              for direction in Direction.objects.all():
                btn = telebot.types.InlineKeyboardButton(direction.Name, callback_data=direction.id)
                kb.add(btn)
              kb.keyboard = kb.keyboard if len(kb.keyboard)>0 else telebot.types.ReplyKeyboardRemove(selective=False)
              res = bot.send_message(call.message.chat.id, "Выберите интересующее Вас направление", reply_markup = kb)
              MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
            else:
              try:
                team = Team.objects.get(id = call.data)
                application.Team = team
                application.save()
                user.Status = "Выбор Даты"
                user.save()
                ikb = telebot.types.InlineKeyboardMarkup()
                ikb.add(telebot.types.InlineKeyboardButton("← Выбрать другой коллектив", callback_data='back'))
                for dt in Date.objects.filter(Team = application.Team):
                  ikb.add(telebot.types.InlineKeyboardButton(dt.DateNTime.strftime("%m.%d в %H:%M"), callback_data=dt.id))
                with open(application.Team.Picture.path, 'rb') as photo:
                  res =bot.send_photo(call.message.chat.id, photo, application.Team.Decription)
                  MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
                res = bot.send_message(call.message.chat.id, f"Место проведения кастинга: \n{application.Team.Place}")
                MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
                res = bot.send_message(call.message.chat.id, "Выберите дату и время кастинга", reply_markup=ikb)
                MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
              except Exception as e:
                print(e)
                res = bot.send_message(call.message.chat.id, "Произошла ошибка, попробуте начать сначала(/start)")
                
                MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
          elif user.Status == "Выбор Даты":
            if call.data == "back":
                user.Status = "Выбор коллектива"
                user.save()
                ikb = telebot.types.InlineKeyboardMarkup()
                ikb.add(telebot.types.InlineKeyboardButton("← Выбрать другое направление", callback_data="back"))
                for team in Team.objects.filter(Direction = application.Direction):
                  ikb.add(telebot.types.InlineKeyboardButton(team.Name, callback_data=team.id))
                res = bot.send_message(call.message.chat.id, "Выберите коллектив", reply_markup = ikb)
                MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
            else:
                try:
                  date = Date.objects.get(id = call.data)
                  application.Date = date
                  application.save()
                  user.Status = "Ввод ФИО"
                  user.save()
                  res = bot.send_message(call.message.chat.id, "Введите Ваше ФИО")
                  MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
                except Exception as e:
                  print(e)
                  res = bot.send_message(call.message.chat.id, "Произошла ошибка, попробуте начать сначала(/start)")
          elif user.Status == "Ввод ФИО":
            if call.data == "back":
              ikb = telebot.types.InlineKeyboardMarkup()
              ikb.add(telebot.types.InlineKeyboardButton("← Выбрать другое направление", callback_data='back'))
              for team in Team.objects.filter(Direction = application.Direction):
                btn = telebot.types.InlineKeyboardButton(team.Name, callback_data=team.id)
                ikb.add(btn)
              user.Status = "Выбор коллектива"
              user.save()
              res = bot.send_message(call.message.chat.id, text="Выберите коллектив", reply_markup = ikb)
              MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
          elif user.Status == "Подтверждение":
            if call.data == "cancel":
              application.delete()
              res = bot.send_message(call.message.chat.id, text="Заявка отменена. Чтобы отправить другую нажмите /start")
              MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
            elif call.data == "send":
              application.IsFinished = True
              application.save()
              res = bot.send_message(call.message.chat.id, f'Заявка отправлена✅\n\n*Коллектив*: {application.Team.Name}\n*Место*: {application.Team.Place}\n*Дата и время*: {application.Date.DateNTime.strftime("%m.%d в %H:%M")}\n*ФИО*: {application.Name}\n\nЕсли у вас возникли вопросы:\n {application.Team.ManagersName}\n {application.Team.ManagersPhone}\n {application.Team.ManagersEmail}', parse_mode="Markdown")
              res = bot.send_message(call.message.chat.id, "Чтобы отправить еще одну заявку нажмите /start")
              MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()



          
      bot.answer_callback_query(call.id)

  except Exception as e:
      print(repr(e))