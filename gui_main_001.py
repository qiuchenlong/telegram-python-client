import asyncio
import collections
import functools
import inspect
import os
import re
import sys
import time
import tkinter
import tkinter.constants
import tkinter.scrolledtext
import tkinter.ttk
import tkinter.filedialog
import socks


from telethon import TelegramClient, events, utils
import telethon


from datetime import datetime
from datetime import timedelta
from datetime import timezone
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon.tl.functions.messages import SendMessageRequest

from apscheduler.schedulers import base


import configparser

import json

from utils.file_util import FileUtil
fileUtil = FileUtil()

basepath = os.path.abspath(__file__)
folder = os.path.dirname(basepath)
sessionPath = "{0}/sessions".format(folder)
dataPath = "{0}/datas".format(folder)

def saveDataByName(name, data):
    fileUtil.write_file_001("{0}{1}".format(dataPath, "/"+name+".csv"), data)

def readDataByName(name):
    return fileUtil.read_file_002("{0}{1}".format(dataPath, "/"+name+".csv"))



def callback(func):
    """
    This decorator turns `func` into a callback for Tkinter
    to be able to use, even if `func` is an awaitable coroutine.
    """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        if inspect.iscoroutine(result):
            asyncio.create_task(result)

    return wrapped



class App(tkinter.Tk):
    """
    Our main GUI application; we subclass `tkinter.Tk`
    so the `self` instance can be the root widget.

    One must be careful when assigning members or
    defining methods since those may interfer with
    the root widget.

    You may prefer to have ``App.root = tkinter.Tk()``
    and create widgets with ``self.root`` as parent.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__app()
        self.tgClientList = []
        self.tk_frame_login = Frame_login(self)
        # self.__tk_input_account()
        self.tk_btn_login()

        

        # self.login()
        
    def tk_btn_login(self):
        btn = tkinter.Button(self, text="...", command=self.checkLogin)
        btn.configure(text="Login")
        btn.grid(row=0, column=2)
        return btn

    

    @callback
    async def checkLogin(self, event=None):
        print(len(self.tgClientList))
        for tg in self.tgClientList:
            chat_id = (await tg.get_entity("https://t.me/+WTEnWAazodlhZGQ1")).id
            messageValue = "你好,测试"
            await tg.send_message(chat_id, messageValue)


    
    @callback
    async def login(self, event=None):
        accountCSV = readDataByName("account")
        accounts = accountCSV.split("\n")
        for account in accounts:
            if account:
                phone = account.split(",")[2]

                tgClient = TgClient(phone).getClient()
                await tgClient.connect()
                auth = await tgClient.is_user_authorized()
                if auth:
                    print(phone, "ok")
                    self.tgClientList.append(tgClient)

        
    def __app(self):
        self.title("Telegram Client")
        # 设置窗口大小、居中
        width = 1080
        height = 720
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        self.resizable(width=False, height=False)


class Frame_login(tkinter.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.first_input_value = None
        self.me = None
        self.__frame()
        self.tk_label_account = self.__tk_label_account()
        self.tk_input_account = self.__tk_input_account()
        self.tk_button_account = self.__tk_button_account()
        self.code = None
        self.twoSteps = False
        self.tgClient = None
        self.tk_btn_add_account()


    def tk_btn_add_account(self):
        btn = tkinter.Button(self, text="...", command=self.add_account)
        btn.configure(text="Add account")
        btn.grid(row=0, column=3)
        return btn

    @callback
    def add_account(self, event=None):
        print("添加账号", self.me)
        account = self.me
        username = utils.get_display_name(self.me)
        phone = self.me.phone
        print(phone, self.first_input_value)
        # self.accountListbox.insert(tkinter.END, "{0},{1}".format(str(account.id), username))
        # saveAccountData(str(account.id), username)

    
    def __frame(self):
        self.place(x=200, y=20, width=680, height=60)

    def __tk_label_account(self):
        lbl = tkinter.Label(self, text="Loading...")
        lbl.configure(text="Sign in (phont/token):")
        # lbl.place(x=10, y=10, width="auto", height=32)
        lbl.grid(row=0, column=0)
        return lbl

    def __tk_input_account(self):
        ipt = tkinter.Entry(self)
        # ipt.place(x=50, y=10, width=150, height=32)
        ipt.grid(row=0, column=1, sticky=tkinter.EW)
        ipt.bind('<Return>', self.sign_in)
        return ipt

    def __tk_button_account(self):
        btn = tkinter.Button(self, text="...", command=self.sign_in)
        btn.configure(text="Sign in")
        btn.grid(row=0, column=2)
        return btn

    @callback
    async def sign_in(self, event=None):
        self.tk_label_account.configure(text="Working...")
        self.tk_input_account.configure(state=tkinter.DISABLED)
        
        # 8613950209512
        account = self.tk_input_account.get().strip()
        if self.first_input_value is None:
            self.first_input_value = account
        # account = "8613950209512"
        if self.tgClient == None:
            self.tgClient = TgClient(account).getClient()
            await self.tgClient.connect()

        auth = await self.tgClient.is_user_authorized()
        print("auth...", auth)
        if auth:
            self.me = await self.tgClient.get_me()
            self.set_signed_in(me=self.me)
            return

        if self.code:
            signLabel = self.tk_label_account.cget("text")
            if signLabel == "Two-steps verification:" or self.twoSteps:
                self.set_signed_in(await self.tgClient.sign_in(password=account))
                return

            try:
                self.set_signed_in(await self.tgClient.sign_in(code=account))
            except telethon.errors.SessionPasswordNeededError:
                self.twoSteps = True
                self.tk_label_account.configure(text='Two-steps verification:')
                self.tk_input_account.configure(state=tkinter.NORMAL)
                self.tk_input_account.delete(0, tkinter.END)
                self.tk_input_account.focus()
            except Exception as e:
                print("e", e)
        elif ":" in account:
            self.set_signed_in(await self.tgClient.sign_in(bot_token=account))
        else:
            self.code = await self.tgClient.send_code_request(account)
            self.tk_label_account.configure(text="Code:")
            self.tk_input_account.configure(state=tkinter.NORMAL)
            self.tk_input_account.delete(0, tkinter.END)
            self.tk_input_account.focus()
            return

    def set_signed_in(self, me):
        """
        Configures the application as "signed in" (displays user's
        name and disables the entry to input phone/bot token/code).
        """
        self.me = me
        self.tk_label_account.configure(text='Signed in')
        self.tk_input_account.configure(state=tkinter.NORMAL)
        self.tk_input_account.delete(0, tkinter.END)
        try:
            self.tk_input_account.insert(tkinter.INSERT, utils.get_display_name(me))
            # self.account_data.append(utils.get_display_name(me))
        except Exception as e:
            pass
        self.tk_input_account.configure(state=tkinter.DISABLED)
        self.tk_button_account.configure(text='Log out')
        # self.chat.focus()
            


# SESSION = "gui"
API_ID = "9458299"
API_HASH = "b0cba0c5ad2b5aa5925ab52afedc3f83"
class TgClient():
    
    def __init__(self, session):
        session = "{0}/{1}".format(sessionPath, session)
        self.client = TelegramClient(session=session,
            api_id=API_ID,
            api_hash=API_HASH)
    
    def getClient(self):
        return self.client
    
    async def connect(self):
        try:
            await self.client.connect()
        except Exception as e:
            print('Failed to connect', e, file=sys.stderr)
            return False
        return True

        

        
async def main(interval=0.05):
    app = App()
    try:
        while True:
            app.update()
            # if app.exit():
            #     sys.exit(0)
            await asyncio.sleep(interval)
    except KeyboardInterrupt:
        pass
    except tkinter.TclError as e:
        if 'application has been destroyed' not in e.args[0]:
            sys.exit(0)
            raise
    finally:
        pass



# https://www.pytk.net/tkinter-helper/
if __name__ == "__main__":
    asyncio.run(main())

    