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

def appendDataByName(name, data):
    res = readDataByName(name)
    exist = False
    for r in res.split("\n"):
        if r.find(str(data).strip()) != -1:
            exist = True
    if exist:
        return
    fileUtil.write_file("{0}{1}".format(dataPath, "/"+name+".csv"), data)

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


globalTgClientList = []

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
        self.tk_listbox_account = None
        Frame_account(self)
        Frame_time(self)
        Frame_messageTemplate(self)
        Frame_Receiver(self)
        Frame_Button(self)
        # self.__tk_input_account()
        self.tk_btn_testcase_sendmsg()

        

        self.auto_login()
        
    def tk_btn_testcase_sendmsg(self):
        btn = tkinter.Button(self, text="...", command=self.testcase_sendmsg)
        btn.configure(text="测试发送消息")
        btn.grid(row=0, column=2)
        return btn

    

    @callback
    async def testcase_sendmsg(self, event=None):
        print(len(self.tgClientList))
        for tg in self.tgClientList:
            chat_id = (await tg.get_entity("https://t.me/+WTEnWAazodlhZGQ1")).id
            messageValue = "你好,测试"
            await tg.send_message(chat_id, messageValue)


    
    ## 获取本地数据,自动登录
    @callback
    async def auto_login(self, event=None):
        accountCSV = readDataByName("account")
        accounts = accountCSV.split("\n")
        for account in accounts:
            if account:
                id = account.split(",")[0]
                phone = account.split(",")[len(account.split(",")) - 1]

                tgClient = TgClient(phone).getClient()
                await tgClient.connect()
                auth = await tgClient.is_user_authorized()
                if auth:
                    print(id, phone, "ok")
                    self.tgClientList.append(tgClient)
                    globalTgClientList.append(tgClient)

                    size = self.tk_listbox_account.size()
                    for i in range(0, size):
                        item = self.tk_listbox_account.get(i)
                        if id in item:
                            self.tk_listbox_account.delete(i)
                            self.tk_listbox_account.insert(i, item + ",ok")
        
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
        print(phone, self.first_input_value, account)

        # bot
        if phone is None:
            data = "{0},{1},{2},{3}\n".format(account.id, "{0}{1}".format(account.first_name, account.last_name), account.username, self.first_input_value)
            appendDataByName("account", data)
        else:
            data = "{0},{1},{2},{3}\n".format(account.id, "{0}{1}".format(account.first_name, account.last_name), account.username, account.phone)
            appendDataByName("account", data)
        # self.accountListbox.insert(tkinter.END, "{0},{1}".format(str(account.id), username))

    
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
        # account = "5797820537:AAFSi75rB-mci13W7IaIoJdwujaVSkRIdnU"
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
            

class Frame_account(tkinter.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.p = parent
        self.__frame()
        self.__tk_listbox_account()

    def __frame(self):
        self.place(x=25, y=120, width=250, height=520)

    def __tk_listbox_account(self):
        self.tk_listbox_account = tkinter.Listbox(self, selectmode=tkinter.EXTENDED, height=12)
        self.tk_listbox_account.place(x=0, y=0, width=250, height=520)

        data = readDataByName("account")
        account_data = data.split("\n")
        for i in range(len(account_data)):
            item = ",".join(map(str, account_data[i].split(",")[0: 2]))
            self.tk_listbox_account.insert(tkinter.END, item)

        self.p.tk_listbox_account = self.tk_listbox_account




class Frame_time(tkinter.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.__frame()

    def __frame(self):
        self.place(x=(250+10)*1+25, y=120, width=250, height=520)

    
class Frame_messageTemplate(tkinter.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.__frame()

    def __frame(self):
        self.place(x=(250+10)*2+25, y=120, width=250, height=520)


class Frame_Receiver(tkinter.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.__frame()
        self.__tk_group()
        self.__tk_phone()
        self.__tk_button()

    def __frame(self):
        self.place(x=(250+10)*3+25, y=120, width=250, height=520)

    def __tk_group(self):
        tkinter.Label(self, text="Group/Channel:").place(x=0, y=0)
        self.textGroup = tkinter.Text(self)
        self.textGroup.place(x=0, y=24, width=250-5, height=200)
    
    def __tk_phone(self):
        tkinter.Label(self, text="Phone:").place(x=0, y=200+10+24)
        self.textGroup = tkinter.Text(self)
        self.textGroup.place(x=0, y=200+10+24*2, width=250-5, height=200)

    def __tk_button(self):
        btn = tkinter.Button(self, text="Save", command=self.on_btn_save)
        btn.place(x=0, y=200*2+10+24*3, )

    @callback
    def on_btn_save(self):
        pass


class Frame_Button(tkinter.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.p = parent
        self.__frame()
        self.__tk_btn_once_send()
        self.__tk_btn_schedule_send()
        self.__tk_btn_stop_send()

    def __frame(self):
        self.place(x=200, y=650, width=680, height=60)
    
    def __tk_btn_once_send(self):
        btn_once_send = tkinter.Button(self, text="立即发送", command=self.on_once_send)
        btn_once_send.grid(row=0, column=0)

    def __tk_btn_schedule_send(self):
        btn_schedule_send = tkinter.Button(self, text="定时发送", command=self.on_schedule_send)
        btn_schedule_send.grid(row=0, column=1)

    def __tk_btn_stop_send(self):
        btn_stop_send = tkinter.Button(self, text="停止发送", command=self.on_stop_send)
        btn_stop_send.grid(row=0, column=2)

    @callback
    def on_once_send(self):
        print(len(globalTgClientList))
        size = self.p.tk_listbox_account.size()
        print(size)
        # self.p.tk_listbox_account.delete(0, size - 1)

    @callback
    def on_schedule_send(self):
        pass

    @callback
    def on_stop_send(self):
        pass
    


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

    