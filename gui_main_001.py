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

import threading
from queue import Queue

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



## =================== time ===================
# 间隔时间(秒)
INTERVAL_TIME = 30
SHA_TZ = timezone(
    timedelta(hours=8),
    name='Asia/Shanghai',
)
# 协调世界时
utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
# 北京时间
beijing_now = utc_now.astimezone(SHA_TZ)
## =================== time ===================


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

        # telegram 客户端
        self.tgClientList = []
        # # message template
        # self.messageTemplate
        # group/channle
        self.groupList = []

        self.tk_frame_login = Frame_login(self)
        self.tk_listbox_account = None
        Frame_account(self)
        Frame_time(self)
        Frame_messageTemplate(self)
        Frame_Receiver(self)
        Frame_Button(self)
        # self.__tk_input_account()
        # self.tk_btn_testcase_sendmsg()

        # self.msg_queue = Queue.queue()
        self.__tk_label_nowtime()
        self.__tk_btn_http_proxy()

        

        self.auto_login()
        
    def tk_btn_testcase_sendmsg(self):
        btn = tkinter.Button(self, text="...", command=self.testcase_sendmsg)
        btn.configure(text="测试发送消息")
        btn.grid(row=0, column=2)
        return btn

    def __tk_label_nowtime(self):
        self.tk_lbl_nowtime = tkinter.Label(self, text="{0}".format(beijing_now.strftime("%Y-%m-%d %H:%M:%S")))
        self.tk_lbl_nowtime.place(x=900, y=10)
       
        # t = threading.Thread(target=self.print_nowtime, daemon=True)
        # t.start()

        self.after(1000, self.print_nowtime)

    def __tk_btn_http_proxy(self):
        self.tk_btn_setting = tkinter.Button(self, text="setting", command=self.on_btn_setting)
        self.tk_btn_setting.place(x=950, y=40)

    
    def print_nowtime(self):
        # 协调世界时
        utc_now_001 = datetime.utcnow().replace(tzinfo=timezone.utc)
        # 北京时间
        beijing_now_001 = utc_now_001.astimezone(SHA_TZ)
        # print(beijing_now_001.strftime("%Y-%m-%d %H:%M:%S"))

        self.tk_lbl_nowtime.config(text="{0}".format(beijing_now_001.strftime("%Y-%m-%d %H:%M:%S")))

        self.after(1000, self.print_nowtime)

        # t = threading.Timer(1.0, self.print_nowtime)
        # t.start()
 
        # t = threading.Thread(target=self.__show)
        # t.start()

    

    @callback
    def on_btn_setting(self, event=None):
        title = "Setting"
        self.tk_modal_setting = tkinter.Toplevel()
        self.tk_modal_setting.title(title)
        root = self.tk_modal_setting

        # 读取配置文件 config.ini
        config = configparser.ConfigParser()
        config.read("config_ini.ini")
        self.conf = config

        tkinter.Label(root, text="名称").grid(row=0, column=0)
        self.tk_input_setting = tkinter.Entry(root)
        self.tk_input_setting.grid(row=0, column=1)
        self.tk_input_setting.insert(tkinter.END, config.get("baseconfig", "title"))


        # Keep track of the button state on/off
        #global is_on
        self.is_on = True if config.get("proxy", "enable") == "1" else False

        self.my_label = tkinter.Label(root, text="代理开关:{0}".format("开" if self.is_on else "关"))
        self.my_label.grid(row=1, column=0)
        
        # Define Our Images
        self.on = tkinter.PhotoImage(file="on.png")
        self.off = tkinter.PhotoImage(file="off.png")

        # Create A Button
        self.on_button = tkinter.Button(root, image=self.on if self.is_on else self.off, bd=0, command = self.switch)
        self.on_button.grid(row=1, column=1)


        # self.tk_input_setting = tkinter.Entry(root)
        # self.tk_input_setting.grid(row=1, column=1)
        # self.tk_input_setting.insert(tkinter.END, config.get("proxy", "enable"))

        tkinter.Label(root, text="代理模式(socks5/http)").grid(row=2, column=0)
        self.tk_input_proxy_mode = tkinter.Entry(root)
        self.tk_input_proxy_mode.grid(row=2, column=1)
        self.tk_input_proxy_mode.insert(tkinter.END, config.get("proxy", "mode"))

        tkinter.Label(root, text="代理地址").grid(row=3, column=0)
        self.tk_input_proxy_host = tkinter.Entry(root)
        self.tk_input_proxy_host.grid(row=3, column=1)
        self.tk_input_proxy_host.insert(tkinter.END, config.get("proxy", "host"))

        tkinter.Label(root, text="代理端口").grid(row=4, column=0)
        self.tk_input_proxy_port = tkinter.Entry(root)
        self.tk_input_proxy_port.grid(row=4, column=1)
        self.tk_input_proxy_port.insert(tkinter.END, config.get("proxy", "port"))

        tkinter.Button(root, text="Commit", command=self.on_btn_commit).grid(row=5, column=0)
        tkinter.mainloop()

    # Define our switch function
    @callback
    def switch(self, event=None):
        # global is_on
        
        # Determine is on or off
        if self.is_on:
            self.on_button.config(image = self.off)
            self.my_label.config(text = "代理开关:关",
                            fg = "grey")
            self.is_on = False
        else:
            self.on_button.config(image = self.on)
            self.my_label.config(text = "代理开关:开", 
                            fg = "green")
            self.is_on = True



    @callback
    def on_btn_commit(self, event=None):
        # save to config.ini
        self.conf.set("baseconfig", "title", self.tk_input_setting.get().strip())
        self.conf.set("proxy", "enable", "1" if self.is_on else "0")
        self.conf.set("proxy", "mode", self.tk_input_proxy_mode.get().strip())
        self.conf.set("proxy", "host", self.tk_input_proxy_host.get().strip())
        self.conf.set("proxy", "port", self.tk_input_proxy_port.get().strip())
        with open("config_ini.ini", "w") as configFile:
            self.conf.write(configFile)

        app_title_vaue = self.tk_input_setting.get().strip()
        self.title(app_title_vaue)
        self.tk_modal_setting.destroy()



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
        self.tk_listbox_account.place(x=0, y=0, width=250-5, height=450)

        data = readDataByName("account")
        account_data = data.split("\n")
        for i in range(len(account_data)):
            item = ",".join(map(str, account_data[i].split(",")[0: 2]))
            if item == "":
                continue
            self.tk_listbox_account.insert(tkinter.END, item)

        self.p.tk_listbox_account = self.tk_listbox_account


        btn = tkinter.Button(self, text="remove", command=self.on_btn_remove_account)
        # btn.configure(text="")
        btn.place(x=0, y=460)

    def on_btn_remove_account(self):
        pass



class Frame_time(tkinter.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.__frame()
        self.__tk_label_starttime()

    def __frame(self):
        self.place(x=(250+10)*1+25, y=120, width=250, height=520)

    def __tk_label_starttime(self):
        tk_label_starttime = tkinter.Label(self, text="Start Time\n(eg: 2022-11-11 12:00:00)", justify="left")
        tk_label_starttime.place(x=0, y=0,)
        self.parent.tk_input_starttime = tkinter.Entry(self, )
        self.parent.tk_input_starttime.place(x=0, y=20*2, width=250-5)
        self.parent.tk_input_starttime.insert(0, "" + beijing_now.strftime("%Y-%m-%d %H:%M:%S"))

        tk_label_intervalstime = tkinter.Label(self, text="Intervals Time\n(eg: 1s)", justify="left")
        tk_label_intervalstime.place(x=0, y=20*4,)
        self.parent.tk_input_intervalstime = tkinter.Entry(self, )
        self.parent.tk_input_intervalstime.place(x=0, y=20*6, width=250-5)
        self.parent.tk_input_intervalstime.insert(0, "" + str(INTERVAL_TIME))

        tk_label_endtime = tkinter.Label(self, text="End Time\n(default: 6h)", justify="left")
        tk_label_endtime.place(x=0, y=20*8,)
        self.parent.tk_input_endstime = tkinter.Entry(self, )
        self.parent.tk_input_endstime.place(x=0, y=20*10, width=250-5)
        delta = timedelta(hours=6)
        self.parent.tk_input_endstime.insert(0, "" + (beijing_now + delta).strftime("%Y-%m-%d %H:%M:%S"))



    
class Frame_messageTemplate(tkinter.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.__frame()
        self.__tk_template_text()

    def __frame(self):
        self.place(x=(250+10)*2+25, y=120, width=250, height=520)

    def __tk_template_text(self):
        self.CheckVarText = tkinter.IntVar(value=1)
        self.CheckVarImage = tkinter.IntVar(value=0)


        tk_label_template_text = tkinter.Label(self, text="Message Template", justify="left")
        tk_label_template_text.place(x=0, y=0,)
        
        self.tk_checkbtn_text = tkinter.Checkbutton(self, variable=self.CheckVarText)
        self.tk_checkbtn_text.place(x=0, y=24, width=20, height=20)

        self.parent.tk_text_template_text = tkinter.Text(self)
        self.parent.tk_text_template_text.place(x=25, y=24, width=250- 30-5, height=200*1.5)


        self.tk_checkbtn_image = tkinter.Checkbutton(self, variable=self.CheckVarImage)
        self.tk_checkbtn_image.place(x=0, y=24+200*1.5 + 5, width=20, height=20)

        btn = tkinter.Button(self, text='select file(image, video)',
            command=self.select_photo)
        btn.place(x=25, y=24+200*1.5, width=250- 30-5, )
        self.tk_file_path = tkinter.Label(self, text='path:', wraplength=250-5, anchor="w", justify="left")
        self.tk_file_path.place(x=0, y=30+24+200*1.5, width=250-5, height=100)

    
    @callback
    def select_photo(self):
        filename = tkinter.filedialog.askopenfilename()
        if filename != "":
            self.tk_file_path.config(text="path:{0}".format(filename))
        else:
            self.tk_file_path.config("没有选择图片文件")

    @callback
    def CheckVarImage(self):
        pass




class Frame_Receiver(tkinter.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.groupList = parent.groupList
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

        groupLinkData = readDataByName("groupLink")
        groupLinkDatas = groupLinkData.split("\n")
        for i in range(len(groupLinkDatas)):
            suffix = "\n"
            if i == len(groupLinkDatas) - 1:
                suffix = ""
            self.textGroup.insert(tkinter.END, groupLinkDatas[i] + suffix)
            self.groupList.append(groupLinkDatas[i])

    def __tk_phone(self):
        tkinter.Label(self, text="Phone:").place(x=0, y=200+10+24)
        self.textPhone = tkinter.Text(self)
        self.textPhone.place(x=0, y=200+10+24*2, width=250-5, height=200)

        phoneNumberData = readDataByName("phoneNumber")
        phoneNumberDatas = phoneNumberData.split("\n")
        for i in range(len(phoneNumberDatas)):
            suffix = "\n"
            if i == len(phoneNumberDatas) - 1:
                suffix = ""
            self.textPhone.insert(tkinter.END, phoneNumberDatas[i] + suffix)

    def __tk_button(self):
        btn = tkinter.Button(self, text="Save", command=self.on_btn_save)
        btn.place(x=0, y=200*2+10+24*3, )

    @callback
    def on_btn_save(self):
        groupLinkData = self.textGroup.get("1.0", tkinter.END).strip()
        saveDataByName("groupLink", groupLinkData)

        phoneNumberData = self.textPhone.get("1.0", tkinter.END).strip()
        saveDataByName("phoneNumber", phoneNumberData)



class Frame_Button(tkinter.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.__frame()
        self.__tk_btn_once_send()
        self.__tk_btn_schedule_send()
        self.__tk_btn_stop_send()



        self.isScheduleTask = False
        self.schedulerTaskCount = 0
        self.schedulerTaskSuccessCount = 0
        self.schedulerTaskFailedCount = 0
        self.scheduler = AsyncIOScheduler()


        self.scheduleTask = tkinter.Label(
            self, 
            text='定时任务:'+ ("运行中" if self.isScheduleTask else "未运行"),
            bg='yellow'
        )
        self.scheduleTask.grid(row=1, column=4)

        self.tk_label_send_status = tkinter.Label(self, text="")
        self.tk_label_send_status.grid(row=1, column=3)



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


    async def send_msg(self):
        # print(len(globalTgClientList))
        # size = self.parent.tk_listbox_account.size()
        # print(size)
        # print(self.parent.groupList)

        print("准备发送消息...")

        messageValue = self.parent.tk_text_template_text.get("1.0", tkinter.END).strip()
        
        # 如果消息是空的,不允许发送
        if messageValue == "":
            return

        print("发送消息...")
        # self.parent.tk_listbox_account.delete(0, size - 1)
        for tg in globalTgClientList:
            for rec in self.parent.groupList:
                try:
                    chat_id = (await tg.get_entity(rec)).id
                    await tg.send_message(chat_id, messageValue)
                    self.schedulerTaskSuccessCount += 1
                    if not self.isScheduleTask:
                        self.tk_label_send_status.config(text="发送成功", bg="#0f0")
                    else:
                        self.tk_label_send_status.config(text="")
                except Exception as e:
                    print("err", e)
                    self.schedulerTaskFailedCount += 1
                    if not self.isScheduleTask:
                        self.tk_label_send_status.config(text="发送失败", bg="#f00") 
                    else:
                        self.tk_label_send_status.config(text="")


    def schedulerListener(self, event):
        print("schedulerListener...", event)
        # get_jobs = self.scheduler.get_jobs()
        # print_jobs = self.scheduler.print_jobs()
        # print(get_jobs)
        # print(print_jobs)

        # EVENT_JOB_REMOVED: 定时任务自动停止时             1024
        # EVENT_SCHEDULER_SHUTDOWN: 定时任务主动移除时      2
        if event.code == base.EVENT_JOB_REMOVED or event.code == base.EVENT_SCHEDULER_SHUTDOWN:
            self.isScheduleTask = False
        if event.code == base.EVENT_JOB_SUBMITTED:
            print("执行定时任务")
            self.schedulerTaskCount += 1

        self.scheduleTask.config(
            text='定时任务:'+ ("运行中, 已执行{0}次,成功{1}次,失败{2}次".format(self.schedulerTaskCount, self.schedulerTaskSuccessCount, self.schedulerTaskFailedCount) if self.isScheduleTask else "未运行"),
            bg="red" if self.isScheduleTask else "yellow"
        )


    @callback
    async def on_once_send(self):
        await self.send_msg()


    @callback
    def on_schedule_send(self):
        if self.scheduler.running:
            return

        startTimeValue = self.parent.tk_input_starttime.get().strip()
        loopTimeValue = self.parent.tk_input_intervalstime.get().strip()
        endTimeValue = self.parent.tk_input_endstime.get().strip()
        self.scheduler.remove_all_jobs()
        self.scheduler.remove_listener(self.schedulerListener)
        self.scheduler.add_job(
            self.send_msg, 
            trigger='interval', 
            seconds=int(loopTimeValue), 
            start_date=startTimeValue,
            end_date=endTimeValue,
        )
        self.scheduler.start()
        self.scheduler.add_listener(self.schedulerListener, )
            # mask=base.EVENT_JOB_REMOVED | base.EVENT_SCHEDULER_SHUTDOWN) # 任务监听

        self.isScheduleTask = True
        self.schedulerTaskCount = 0
        self.scheduleTask.config(
            text='定时任务:'+ ("运行中, 已执行{0}次,成功{1}次,失败{2}次".format(self.schedulerTaskCount, self.schedulerTaskSuccessCount, self.schedulerTaskFailedCount) if self.isScheduleTask else "未运行"),
            bg='red'
        )

    @callback
    def on_stop_send(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
    


# SESSION = "gui"
API_ID = "9458299"
API_HASH = "b0cba0c5ad2b5aa5925ab52afedc3f83"
class TgClient():
    
    def __init__(self, session):
        session = "{0}/{1}".format(sessionPath, session)

        config = configparser.ConfigParser()
        config.read("config_ini.ini")
        enable = config.get("proxy", "enable")
        mode = config.get("proxy", "mode")
        host = config.get("proxy", "host")
        port = config.get("proxy", "port")

        if enable != None and mode != None and host != None and port != None and (enable == "1"):
            if str(mode).lower() == "socks5":
                self.client = TelegramClient(session, 
                        API_ID, 
                        API_HASH, 
                        proxy=(socks.SOCKS5, host, int(port)))
            elif str(mode).lower() == "http":
                self.client = TelegramClient(session, 
                        API_ID, 
                        API_HASH, 
                        proxy=(socks.HTTP, host, int(port)))
            else:
                self.client = TelegramClient(session=session,
                    api_id=API_ID,
                    api_hash=API_HASH)
        else:
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

    