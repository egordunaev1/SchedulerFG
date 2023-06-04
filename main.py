import telebot
from telebot import types
import schedule
import time
from datetime import datetime
import threading

token = "6262873019:AAEBRwRcS2W5JUxqb4M7-w4Lk3AD-uFN_rg"
admin_id = 456961755
foma_id = 5483630327
gleb_id = 1053088289

bot = telebot.TeleBot(token)

class action:
    def __init__(self, text: str, bot, chat_id):
        self.name, self.when = text.split(';')[1:]
        self.bot = bot
        self.chat = chat_id
        self.gleb = 0
        self.foma = 0
        self.create_schedule()
        
        self.bot.send_message(self.chat, f"Создано: {self.name}")
    
    def create_schedule(self):
        if not self.when:
            return
        if self.when[0] == 'ч':
            schedule.every(int(self.when[1:])).days.at("8:00").do(self.alarm, 60, "23:59")
        else:
            for t in self.when[1:-1].split(','):
                b, e = t.split('-')
                schedule.every().day.at(b).do(self.alarm, 15, e)
    
    def alarm(self, interval: int, end: str):
        self.__alarm()
        self.job = schedule.every(interval).minutes.do(self.__alarm)
        if end:
            self.job.until(end)

    def __alarm(self):
        if self.gleb > self.foma:
            who = f"Фома ({self.gleb - self.foma})"
        else:
            who = f"Глеб ({self.foma - self.gleb})"

        msg = f"Действие: {self.name}\nДелает: {who}"
        self.bot.send_message(self.chat, msg)
    
    def done(self, user: int):
        try:
            schedule.cancel_job(self.job)
        except:
            self.bot.send_message(self.chat, "Exception")

        if user == foma_id:
            self.foma += 1
        else:
            self.gleb += 1
    
    def __del__(self):
        schedule.cancel_job(self.job)
        self.bot.send_message(self.chat, f"Удалено: {self.name}")

actions = dict()

def create_action(text: str, chat: int):
    actions[text.split(';')[1]] = action(text, bot, chat)

def action_done(name: str, chat: int, user: int):
    if name not in actions:
        bot.send_message(chat, f"Неизвестное действие: {name}")
    else:
        actions[name].done(user)

def delete_action(name: str, chat: int):
    if name not in actions:
        bot.send_message(chat, f"Неизвестное действие: {name}")
    else:
        actions.pop(name)

def run_pending():
    while True:
        schedule.run_pending()
        time.sleep(1)

@bot.message_handler(content_types=["text"])
def handle_text(message: telebot.types.Message):
    text = str(message.text)
    if text.startswith("Удалить;") and message.from_user.id == admin_id:
        delete_action(text, message.chat.id)
    elif text.startswith("Создать;") and message.from_user.id == admin_id:
        create_action(text, message.chat.id)
    else:
        action_done(text, message.from_user.id)

threading.Thread(target=run_pending).start()
bot.polling(none_stop=True, interval=0)