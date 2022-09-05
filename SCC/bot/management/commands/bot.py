from random import randint
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
    try:
      bot.delete_message(message.from_user.id, mess.mess_id)
    except:
      pass
    mess.delete()
  if message.text == "/start":
    user.Status = "Выбор направления"
    user.save()
    if isExist:
      res = bot.send_message(message.from_user.id, "Привет! Здесь вы можете записаться на кастинг :)", reply_markup=telebot.types.ReplyKeyboardRemove(selective=False))
    kb = telebot.types.InlineKeyboardMarkup()
    for direction in Direction.objects.all():
      btn = telebot.types.InlineKeyboardButton(direction.Name, callback_data=direction.id)
      kb.add(btn)
    kb = kb if len(kb.keyboard)>0 else telebot.types.ReplyKeyboardRemove(selective=False)
    res = bot.send_message(message.from_user.id, "Выберите интересующее Вас направление", reply_markup = kb)
    try:
      bot.delete_message(message.from_user.id, user.EditMessId)
    except:
      pass
    user.EditMessId = res.id
    user.save()
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
      res=bot.send_message(chat_id=message.chat.id, text=f'*Направление*: {application.Direction.Name}\n*Коллектив*: {application.Team.Name}\n*Дата*: {application.Date.Date}\n*ФИО*: {application.Name}\n*Номер телефона*: {application.Phone}\nОтправить Вашу заявку?', reply_markup=kb, parse_mode="Markdown")
      try:
        bot.delete_message(message.from_user.id, user.EditMessId)
      except:
        pass
      user.EditMessId = res.id
      user.save()
    else:
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
          user = TgUser.objects.get_or_create(id = call.message.chat.id)[0]
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
                for team in Team.objects.filter(Direction = application.Direction):
                  ikb.add(telebot.types.InlineKeyboardButton(team.Name, callback_data=team.id))
                ikb.add(telebot.types.InlineKeyboardButton("← Выбрать другое направление", callback_data="back"))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=user.EditMessId, text="Выберите коллектив", reply_markup=ikb )
                #res = bot.send_message(call.message.chat.id, "Выберите коллектив", reply_markup = ikb)
                #MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
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
              bot.edit_message_text(chat_id=call.message.chat.id, message_id=user.EditMessId, text="Выберите интересующее вас направление", reply_markup=kb )
            else:
              try:

                team = Team.objects.get(id = call.data)
                application.Team = team
                application.save()
                user.Status = "Выбор Даты"
                user.save()

                bot.delete_message(call.message.chat.id, user.EditMessId)
                with open(application.Team.Picture.path, 'rb') as photo:
                  ikb = telebot.types.InlineKeyboardMarkup()
                  ikb.add(telebot.types.InlineKeyboardButton("Группа ВКонтакте", url=application.Team.Vk))
                  res = bot.send_photo(call.message.chat.id, photo, application.Team.Decription, reply_markup=ikb)
                  MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()

                
                ikb = telebot.types.InlineKeyboardMarkup()
                btns = Date.objects.filter(dateteam__Team = application.Team).values('id','Date')
                for i in range(len(btns)//3):
                  ikb.row(telebot.types.InlineKeyboardButton(btns[i*3]["Date"], callback_data=btns[i*3]["id"]),
                  telebot.types.InlineKeyboardButton(btns[i*3+1]["Date"], callback_data=btns[i*3+1]["id"]),
                  telebot.types.InlineKeyboardButton(btns[i*3+2]["Date"], callback_data=btns[i*3+2]["id"]))
                if len(btns)%3>1:
                  ikb.row(telebot.types.InlineKeyboardButton(btns[len(btns)-(len(btns)%3)]["Date"], callback_data=btns[len(btns)-(len(btns)%3)]["id"]),
                  telebot.types.InlineKeyboardButton(btns[len(btns)-(len(btns)%3)+1]["Date"], callback_data=btns[len(btns)-(len(btns)%3)+1]["id"]))
                elif len(btns)%3>0:
                  ikb.row(telebot.types.InlineKeyboardButton(btns[len(btns)-(len(btns)%3)]["Date"], callback_data=btns[len(btns)-(len(btns)%3)]["id"]))
                ikb.add(telebot.types.InlineKeyboardButton("← Выбрать другой коллектив", callback_data='back'))
                res = bot.send_message(call.message.chat.id, f"Кастинг проводится по адресу *{application.Team.Place} {application.Team.Time}* \nВыберите дату кастинга", reply_markup=ikb, parse_mode="Markdown")
                user.EditMessId = res.id
                user.save()
              except Exception as e:
                print(e)
                res = bot.send_message(call.message.chat.id, "Произошла ошибка, попробуте начать сначала(/start)")
                MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
                
          elif user.Status == "Выбор Даты":
            if call.data == "back":
                user.Status = "Выбор коллектива"
                user.save()
                ikb = telebot.types.InlineKeyboardMarkup()
                for team in Team.objects.filter(Direction = application.Direction):
                  ikb.add(telebot.types.InlineKeyboardButton(team.Name, callback_data=team.id))
                ikb.add(telebot.types.InlineKeyboardButton("← Выбрать другое направление", callback_data="back"))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=user.EditMessId, text="Выберите коллектив", reply_markup=ikb )
            else:
                try:
                  bot.delete_message(call.message.chat.id, user.EditMessId)
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
                  MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
          elif user.Status == "Подтверждение":
            if call.data == "cancel":
              application.delete()
              user.Status = ""
              user.save()
              bot.delete_message(call.message.chat.id, user.EditMessId)
              res = bot.send_message(call.message.chat.id, text="Заявка отменена. Чтобы отправить другую нажмите /start")
              MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()
            elif call.data == "send":
              application.IsFinished = True
              application.save()
              user.Status = ""
              user.save()
              bot.delete_message(call.message.chat.id, user.EditMessId)
              bot.send_message(chat_id=call.message.chat.id, text=f'Заявка отправлена✅\n\n*Коллектив*: {application.Team.Name}\n*Место*: {application.Team.Place}\n*Дата и время*: {application.Date.Date} {application.Team.Time}\n*ФИО*: {application.Name}\n\n_{application.Team.Prompt}_\n\nЕсли у вас возникли вопросы:\n{application.Team.Contacts}', parse_mode="Markdown", reply_markup='')
              res = bot.send_message(call.message.chat.id, "Чтобы отправить еще одну заявку нажмите /start")
              MessageForDelete.objects.create(TgUser = user, mess_id = res.message_id).save()





          
      bot.answer_callback_query(call.id)

  except Exception as e:
      print(repr(e))