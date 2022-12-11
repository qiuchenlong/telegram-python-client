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

from core.PlaceholderEntry import PlaceholderEntry


from telethon import TelegramClient, events, utils
import telethon


from datetime import datetime
from datetime import timedelta
from datetime import timezone
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from telethon.tl.types import PeerUser, PeerChat, PeerChannel,UpdateNewChannelMessage
from telethon.tl.types import User, Channel
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


loop = asyncio.get_event_loop()

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
    def setExit(self, value):
        self.exitValue = value
    def exit(self):
        return self.exitValue
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
        # time
        self.CheckVarLoop = None
        # self.CheckVarTime = None
        # message template
        self.CheckVarText = None
        self.CheckVarImage = None
        # group/channle
        self.groupList = []
        self.phoneList = []

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
        self.tk_btn_setting = tkinter.Button(self, text="系统设置", command=self.on_btn_setting)
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
        title = "系统设置"
        self.tk_modal_setting = tkinter.Toplevel()
        self.tk_modal_setting.title(title)
        root = self.tk_modal_setting

        # 读取配置文件 config.ini
        config = configparser.ConfigParser()
        config.read("config_ini.ini", encoding="utf-8")
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

        tkinter.Label(root, text="注:设置代理,需重启软件", fg="#f00").grid(row=5, column=0)

        tkinter.Button(root, text="提交", command=self.on_btn_commit).grid(row=5, column=1)
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
        with open("config_ini.ini", "w", encoding="utf-8") as configFile:
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


    async def login(self, tgClient, id, phone):
        print("login...")
        try:
            await tgClient.connect()
            auth = await tgClient.is_user_authorized()
            if auth:
                print(id, phone, "ok")
                self.tgClientList.append(tgClient)
                globalTgClientList.append(tgClient)

                me = await tgClient.get_me()
                isbot = me.bot

                size = self.tk_listbox_account.size()
                for i in range(0, size):
                    item = self.tk_listbox_account.get(i)
                    if id in item:
                        self.tk_listbox_account.delete(i)
                        self.tk_listbox_account.insert(i, "{0},{1},ok".format(item, "机器号" if isbot else "实体号"))
                        self.tk_listbox_account.itemconfig(i, bg="#f00" if isbot else "#0f0")
        
        except ConnectionError as e:
            tkinter.messagebox.showerror(title="错误", message="无法连接到telegram服务,请检查网络", )
        except Exception as e:
            print("login happen error,", e)

            size = self.tk_listbox_account.size()
            for i in range(0, size):
                item = self.tk_listbox_account.get(i)
                if id in item:
                    self.tk_listbox_account.delete(i)
                    self.tk_listbox_account.insert(i, item + ",fail")
    
    ## 获取本地数据,自动登录
    @callback
    async def auto_login(self, event=None):
        print("auto_login")
        accountCSV = readDataByName("account")
        accounts = accountCSV.split("\n")
        for account in accounts:
            if account:
                id = account.split(",")[0]
                phone = account.split(",")[len(account.split(",")) - 1]

                tgClient = TgClient(phone).getClient()
                try:


                    # await self.login(tgClient, id, phone)
                    asyncio.create_task(self.login(tgClient, id, phone))


                    # tgClient.loop.run_until_complete(payload(tgClient))
                    # for task in asyncio.Task.all_tasks(tgClient.loop):
                    #     task.cancel()

                    # task = tgClient.loop.create_task(self.login())
                    # tgClient.loop.run_until_complete(task)

                    # await tgClient.connect()
                    # time.sleep(5)
                    # print(222)
                    # auth = await tgClient.is_user_authorized()
                    # print(333)
                    # if auth:
                    #     print(id, phone, "ok")
                    #     self.tgClientList.append(tgClient)
                    #     globalTgClientList.append(tgClient)

                    #     size = self.tk_listbox_account.size()
                    #     for i in range(0, size):
                    #         item = self.tk_listbox_account.get(i)
                    #         if id in item:
                    #             self.tk_listbox_account.delete(i)
                    #             self.tk_listbox_account.insert(i, item + ",ok")
                except Exception as e:
                    print("e...", e)
                    
        
    def __app(self):
        config = configparser.ConfigParser()
        # 这里不能读中文,macOS会报错
        config.read("config_ini.ini", encoding="utf-8")
        self.title(config.get("baseconfig", "title"))
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
        self.parent = parent
        self.first_input_value = None
        self.me = None
        self.__frame()
        self.tk_label_account = self.__tk_label_account()
        self.tk_input_account = self.__tk_input_account()
        self.tk_button_account = self.__tk_button_account()
        self.code = None
        self.twoSteps = False
        self.tgClient = None
        self.tk_input_remark_account = self.__tk_input_remark_account()
        self.tk_btn_add_account = self.__tk_btn_add_account()
        

    def __tk_input_remark_account(self):
        # input = tkinter.Entry(self, )
        # input.insert(tkinter.END, "请输入账号备注")
        # input.configure(state=tkinter.DISABLED)
        # def focus_in(self):
        #     input.configure(state=tkinter.NORMAL)
        #     input.delete(0, tkinter.END)
        # def focus_out(self):
        #     if input.get().strip() != "":
        #         input.insert(tkinter.END, "请输入账号备注")
        #         input.configure(state=tkinter.DISABLED)
        # input.bind("<FocusIn>", focus_in)
        # input.bind("<FocusOut>", focus_out)

        input = PlaceholderEntry(self, "请输入账号备注")
        input.bind('<Return>', self.add_account)
        input.configure(state=tkinter.DISABLED)
        input.grid(row=0, column=4)
        return input

    def __tk_btn_add_account(self):
        btn = tkinter.Button(self, text="...", command=self.add_account)
        btn.configure(text="添加账号")
        btn.configure(state=tkinter.DISABLED)
        btn.grid(row=0, column=5)
        return btn

    @callback
    def add_account(self, event=None):
        # print("添加账号", self.me)

        if self.me is None:
            tkinter.messagebox.showerror(title="错误", message="账号未登录", )
            return

        account = self.me
        username = utils.get_display_name(self.me)
        phone = self.me.phone
        # print(phone, self.first_input_value, account)

        # 备注
        remark_account = self.tk_input_remark_account.get().strip()


        # bot
        data = ""
        isbot = phone is None
        if isbot:
            data = "{0},{1},{2},{3},{4}\n".format(
                account.id, 
                remark_account, 
                "{0}{1}".format("" if account.first_name is None else account.first_name, "" if account.last_name is None else account.last_name), 
                "" if account.username is None else account.username, 
                self.first_input_value
            )
        else:
            data = "{0},{1},{2},{3},{4}\n".format(
                account.id, 
                remark_account, 
                "{0}{1}".format("" if account.first_name is None else account.first_name, "" if account.last_name is None else account.last_name), 
                "" if account.username is None else account.username, 
                account.phone
            )
        # self.accountListbox.insert(tkinter.END, "{0},{1}".format(str(account.id), username))
        appendDataByName("account", data)
        item = ",".join(map(str, data.split(",")[0: 3]))
        self.parent.tk_listbox_account.insert(tkinter.END, "{0},{1},ok".format(item, "机器号" if isbot else "实体号"))
        self.parent.tk_listbox_account.itemconfig(tkinter.END, bg="#f00" if isbot else "#0f0")
        # self.parent.tk_listbox_account.insert(tkinter.END, item+",ok")

        # todo: 将连接句柄,放入全局连接句柄管理
        globalTgClientList.append(self.tgClient)
        self.tgClient = None
        self.tk_label_account.config(text="登录 (手机号/token):")
        self.tk_input_account.configure(state=tkinter.NORMAL)
        self.tk_input_account.delete(0, tkinter.END)
        self.tk_button_account.configure(text='登录')

        self.tk_input_remark_account.delete(0, tkinter.END)
        self.tk_input_remark_account.insert(tkinter.END, "请输入账号备注")
        self.tk_input_remark_account.configure(state=tkinter.DISABLED)
        self.tk_btn_add_account.configure(state=tkinter.DISABLED)



    
    def __frame(self):
        self.place(x=200, y=20, width=680, height=60)

    def __tk_label_account(self):
        lbl = tkinter.Label(self, text="加载中...")
        lbl.configure(text="登录 (手机号/token):")
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
        btn.configure(text="登录")
        btn.grid(row=0, column=2)
        return btn

    @callback
    async def sign_in(self, event=None):
        self.tk_label_account.configure(text="进行中...")
        self.tk_input_account.configure(state=tkinter.DISABLED)
        self.tk_button_account.configure(state=tkinter.DISABLED)
        
        # 8613950209512
        account = self.tk_input_account.get().strip()
        if account == "":
            self.tk_label_account.configure(text="登录 (手机号/token):")
            self.tk_input_account.configure(state=tkinter.NORMAL)
            self.tk_button_account.configure(state=tkinter.NORMAL)
            tkinter.messagebox.showerror(title="错误", message="手机号/token不能为空", )
            return

        if self.first_input_value is None:
            self.first_input_value = account
        # account = "8613950209512"
        # account = "5797820537:AAFSi75rB-mci13W7IaIoJdwujaVSkRIdnU"
        # is_success = True
        if self.tgClient == None:
            self.tgClient = TgClient(account).getClient()
            await self.tgClient.connect()
            # try:
            #     self.tgClient = TgClient(account).getClient()
            #     await self.tgClient.connect()
            # except Exception as e:
            #     print(e)
            #     is_success = False
            #     tkinter.messagebox.showerror(title="错误", message="无法连接到telegram服务,请检查网络", )

        # if not is_success:
        #     return

        auth = await self.tgClient.is_user_authorized()
        print("auth...", auth)
        if auth:
            self.me = await self.tgClient.get_me()
            self.set_signed_in(me=self.me)
            return

        if self.code:
            signLabel = self.tk_label_account.cget("text")
            if signLabel == "两步验证:" or self.twoSteps:
                self.set_signed_in(await self.tgClient.sign_in(password=account))
                return

            try:
                self.set_signed_in(await self.tgClient.sign_in(code=account))
            except telethon.errors.SessionPasswordNeededError:
                self.twoSteps = True
                self.tk_label_account.configure(text='两步验证:')
                self.tk_input_account.configure(state=tkinter.NORMAL)
                self.tk_input_account.delete(0, tkinter.END)
                self.tk_input_account.focus()
                self.tk_button_account.configure(state=tkinter.NORMAL)
            except Exception as e:
                print("e", e)
        elif ":" in account:
            self.set_signed_in(await self.tgClient.sign_in(bot_token=account))
        else:
            self.code = await self.tgClient.send_code_request(account)
            self.tk_label_account.configure(text="验证码:")
            self.tk_input_account.configure(state=tkinter.NORMAL)
            self.tk_input_account.delete(0, tkinter.END)
            self.tk_input_account.focus()
            self.tk_button_account.configure(state=tkinter.NORMAL)
            return

    def set_signed_in(self, me):
        """
        Configures the application as "signed in" (displays user's
        name and disables the entry to input phone/bot token/code).
        """
        self.me = me
        self.tk_label_account.configure(text='已登录')
        self.tk_input_account.configure(state=tkinter.NORMAL)
        self.tk_input_account.delete(0, tkinter.END)
        self.tk_button_account.configure(state=tkinter.NORMAL)

        self.tk_input_remark_account.configure(state=tkinter.NORMAL)
        self.tk_input_remark_account.focus()
        self.tk_btn_add_account.configure(state=tkinter.NORMAL)

        try:
            self.tk_input_account.insert(tkinter.INSERT, utils.get_display_name(me))
            # self.account_data.append(utils.get_display_name(me))
        except Exception as e:
            pass
        self.tk_input_account.configure(state=tkinter.DISABLED)
        self.tk_button_account.configure(text='登出')
        # self.chat.focus()
            

class Frame_account(tkinter.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
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
            item = ",".join(map(str, account_data[i].split(",")[0: 3]))
            if item == "":
                continue
            self.tk_listbox_account.insert(tkinter.END, item)

        self.parent.tk_listbox_account = self.tk_listbox_account


        btn = tkinter.Button(self, text="移除账号", command=self.on_btn_remove_account)
        # btn.configure(text="")
        btn.place(x=0, y=460)

    @callback
    async def on_btn_remove_account(self):
        result = tkinter.messagebox.askquestion(title="提示", message="确定移除账号?", icon="warning")
        if result != "yes":
            return
        # 获取选中的账号
        select = self.parent.tk_listbox_account.curselection()
        print(select)
        if len(select) == 0:
            return
        data = readDataByName("account")
        accountData = data.split("\n")

        start = select[0]
        end = select[len(select) - 1]
        print(start, end)
        print("accountData...", accountData)
        account_item = accountData[start: end + 1]
        # print("account_item...", account_item)
        del accountData[start: end + 1]
        self.tk_listbox_account.delete(start, end) # 删除listbox组件的数据
        
        print("accountData", accountData)

        d = ""
        for account in accountData:
            if account != "":
                d += ''.join(account + "\n")
        print("d...", d)
        
        # 设置csv数据
        saveDataByName("account", d)
        
        print(account_item)
        for a in account_item:
            print(a.split(",")[len(a.split(",")) - 1])
            file_path = "{0}/sessions/{1}.session".format(folder, a.split(",")[len(a.split(",")) - 1])
            print("file_path...", file_path)
            # 删除session文件
            fileUtil.delete_file(file_path)

        # todo: 从全家账号句柄中,移除选中的账号句柄
        client_index_list = []
        for a in account_item:
            for i in range(len(globalTgClientList)):
                if globalTgClientList[i] == "":
                    continue
                me = await globalTgClientList[i].get_me()
                # print(a.split(",")[0], me)
                if a.split(",")[0] == str(me.id):
                    client_index_list.append(i)
                    globalTgClientList[i] = ""

        print(client_index_list)
        while "" in globalTgClientList:
            globalTgClientList.remove("")
        print(len(globalTgClientList))
        







class Frame_time(tkinter.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.__frame()
        self.__tk_label_starttime()

    def __frame(self):
        self.place(x=(250+10)*1+25, y=120, width=250, height=520)

    def __tk_label_starttime(self):
        self.CheckVarLoop = tkinter.IntVar(value=0)
        # self.CheckVarTime = tkinter.IntVar(value=0)

        self.parent.CheckVarLoop = self.CheckVarLoop
        # self.parent.CheckVarTime = self.CheckVarTime

        tkinter.Label(self, text="1、按 时间单位:\n循环时刻(eg: 1秒)", justify="left").place(x=0, y=0,)
       

        self.tk_checkbtn_text = tkinter.Radiobutton(self, value=0, variable=self.CheckVarLoop)
        self.tk_checkbtn_text.place(x=0, y=20*2, width=20, height=20)
       
        tk_label_starttime = tkinter.Label(self, text="开始时间\n(默认: 2022-11-11 12:00:00)", justify="left")
        tk_label_starttime.place(x=0, y=20*3,)
        self.parent.tk_input_starttime = tkinter.Entry(self, )
        self.parent.tk_input_starttime.place(x=0, y=20*5, width=250-5)
        self.parent.tk_input_starttime.insert(0, "" + beijing_now.strftime("%Y-%m-%d %H:%M:%S"))

        # 秒
        tkinter.Label(self, text="秒", justify="right").place(x=200, y=20*6 + 28 -18)
        self.parent.tk_input_intervals_seconds = tkinter.Entry(self, )
        self.parent.tk_input_intervals_seconds.place(x=0, y=20*6 + 28 -18, width=250-5 - 50)
        self.parent.tk_input_intervals_seconds.insert(0, "")

        # 分
        tkinter.Label(self, text="分", justify="right").place(x=200, y=20*6 + 28*2 -18)
        self.parent.tk_input_intervals_minutes = tkinter.Entry(self, )
        self.parent.tk_input_intervals_minutes.place(x=0, y=20*6 + 28*2 -18, width=250-5 - 50)
        self.parent.tk_input_intervals_minutes.insert(0, "")

        # 小时
        tkinter.Label(self, text="小时", justify="right").place(x=200, y=20*6 + 28*3 -18)
        self.parent.tk_input_intervals_hours = tkinter.Entry(self, )
        self.parent.tk_input_intervals_hours.place(x=0, y=20*6 + 28*3 -18, width=250-5 - 50)
        self.parent.tk_input_intervals_hours.insert(0, "")

        # 天
        tkinter.Label(self, text="天", justify="right").place(x=200, y=20*6 + 28*4 -18)
        self.parent.tk_input_intervals_days = tkinter.Entry(self, )
        self.parent.tk_input_intervals_days.place(x=0, y=20*6 + 28*4 -18, width=250-5 - 50)
        self.parent.tk_input_intervals_days.insert(0, "")


        tk_label_endtime = tkinter.Label(self, text="结束时间\n(默认: 30天)", justify="left")
        tk_label_endtime.place(x=0, y=20*6 + 28*5 -18,)
        self.parent.tk_input_endstime = tkinter.Entry(self, )
        self.parent.tk_input_endstime.place(x=0, y=20*8 + 28*5 -18, width=250-5)
        # delta = timedelta(hours=6)
        delta = timedelta(days=30)
        self.parent.tk_input_endstime.insert(0, "" + (beijing_now + delta).strftime("%Y-%m-%d %H:%M:%S"))



        self.tk_checkbtn_time = tkinter.Radiobutton(self, value=1, variable=self.CheckVarLoop)
        self.tk_checkbtn_time.place(x=0, y=20*9 + 160, width=20, height=20)

        # 时刻
        tkinter.Label(self, text="2、按 固定时间:", justify="right").place(x=0, y=20*9 + 180)
        self.parent.tk_input_intervals_time = tkinter.Entry(self, )
        self.parent.tk_input_intervals_time.place(x=0, y=20*10 + 180, width=250-5 - 50)
        self.parent.tk_input_intervals_time.insert(0, "")
        # self.parent.tk_input_intervals_time.insert(0, "" + beijing_now.strftime("%Y-%m-%d %H:%M:%S"))




    
class Frame_messageTemplate(tkinter.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # 读取配置文件 config.ini
        config = configparser.ConfigParser()
        config.read("config_ini.ini", encoding="utf-8")
        self.conf = config
        
        self.__frame()
        self.__tk_template_text()
        self.__tk_button()

    def __frame(self):
        self.place(x=(250+10)*2+25, y=120, width=250, height=520)

    def __tk_template_text(self):
        check_content = self.conf.get("message", "check_content")
        check_file = self.conf.get("message", "check_file")
        content = self.conf.get("message", "content")
        file_path = self.conf.get("message", "file_path")

        self.CheckVarText = tkinter.IntVar(value=1 if check_content == "1" else 0)
        self.CheckVarImage = tkinter.IntVar(value=1 if check_file == "1" else 0)

        self.parent.CheckVarText = self.CheckVarText
        self.parent.CheckVarImage = self.CheckVarImage

        tk_label_template_text = tkinter.Label(self, text="消息模板", justify="left")
        tk_label_template_text.place(x=0, y=0,)
        
        self.tk_checkbtn_text = tkinter.Checkbutton(self, variable=self.CheckVarText)
        self.tk_checkbtn_text.place(x=0, y=24, width=20, height=20)

        self.parent.tk_text_template_text = tkinter.Text(self)
        self.parent.tk_text_template_text.place(x=25, y=24, width=250- 30-5, height=200*1.5)
        self.parent.tk_text_template_text.insert(tkinter.END, "" + content)


        self.tk_checkbtn_image = tkinter.Checkbutton(self, variable=self.CheckVarImage)
        self.tk_checkbtn_image.place(x=0, y=24+200*1.5 + 5, width=20, height=20)

        btn = tkinter.Button(self, text='选择文件(图片、视频或者其他文件)',
            command=self.select_photo)
        btn.place(x=25, y=24+200*1.5, width=250- 30-5, )
        tkinter.Label(self, text='路径:', anchor="w", justify="left").place(x=0, y=30+24+200*1.5)
        self.parent.tk_label_file_path = tkinter.Label(self, text='', wraplength=250-5, anchor="w", justify="left")
        self.parent.tk_label_file_path.place(x=0, y=30+24+200*1.5 + 28, width=250-5, height=100)
        self.parent.tk_label_file_path.config(text="" + file_path)



    def __tk_button(self):
        btn = tkinter.Button(self, text="保存", command=self.on_btn_save)
        btn.place(x=0, y=200*2+10+24*3, )

    
    @callback
    def select_photo(self):
        filename = tkinter.filedialog.askopenfilename()
        if filename != "":
            self.parent.tk_label_file_path.config(text="{0}".format(filename))
        else:
            self.parent.tk_label_file_path.config(text="没有选择图片文件")

    @callback
    def on_btn_save(self):
        check_content = str(self.parent.CheckVarText.get())
        check_file = str(self.parent.CheckVarImage.get())
        messageValue = self.parent.tk_text_template_text.get("1.0", tkinter.END).strip()
        image_path = self.parent.tk_label_file_path.cget("text")
        
        self.conf.set("message", "check_content", check_content)
        self.conf.set("message", "check_file", check_file)
        self.conf.set("message", "content", messageValue)
        self.conf.set("message", "file_path", image_path)
        with open("config_ini.ini", "w", encoding="utf-8") as configFile:
            self.conf.write(configFile)





class Frame_Receiver(tkinter.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.groupList = parent.groupList
        self.phoneList = parent.phoneList
        self.__frame()
        self.__tk_group()
        self.__tk_phone()
        self.__tk_button()

    def __frame(self):
        self.place(x=(250+10)*3+25, y=120, width=250, height=520)

    def __tk_group(self):
        tkinter.Label(self, text="群组/频道 分享链接:").place(x=0, y=0)
        self.textGroup = tkinter.Text(self)
        self.textGroup.place(x=0, y=24, width=250-5, height=200)

        self.__load_tk_group_data()        

    def __tk_phone(self):
        tkinter.Label(self, text="手机号(+区号)/用户名:").place(x=0, y=200+10+24)
        self.textPhone = tkinter.Text(self)
        self.textPhone.place(x=0, y=200+10+24*2, width=250-5, height=200)

        self.__load_tk_phone_data()

    # 加载群组/频道数据
    def __load_tk_group_data(self):
        groupLinkData = readDataByName("groupLink")
        groupLinkDatas = groupLinkData.split("\n")
        for i in range(len(groupLinkDatas)):
            suffix = "\n"
            if i == len(groupLinkDatas) - 1:
                suffix = ""
            self.textGroup.insert(tkinter.END, groupLinkDatas[i] + suffix)
            self.groupList.append(groupLinkDatas[i])
    
    # 加载手机号/用户名数据
    def __load_tk_phone_data(self):
        phoneNumberData = readDataByName("phoneNumber")
        phoneNumberDatas = phoneNumberData.split("\n")
        for i in range(len(phoneNumberDatas)):
            suffix = "\n"
            if i == len(phoneNumberDatas) - 1:
                suffix = ""
            self.textPhone.insert(tkinter.END, phoneNumberDatas[i] + suffix)
            self.phoneList.append(phoneNumberDatas[i])


    def __tk_button(self):
        btn = tkinter.Button(self, text="保存", command=self.on_btn_save)
        btn.place(x=0, y=200*2+10+24*3, )

    @callback
    def on_btn_save(self):
        groupLinkData = self.textGroup.get("1.0", tkinter.END).strip()
        saveDataByName("groupLink", groupLinkData)

        phoneNumberData = self.textPhone.get("1.0", tkinter.END).strip()
        saveDataByName("phoneNumber", phoneNumberData)

        self.textGroup.delete("0", "end")
        self.groupList = []
        self.__load_tk_group_data()
        self.textPhone.delete("0", "end")
        self.phoneList = []
        self.__load_tk_phone_data()



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

        self.tk_label_send_status = tkinter.Label(self, text="立即发送状态")
        self.tk_label_send_status.place(x=10, y=30)



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


    def check_send_msg(self):
        messageValue = self.parent.tk_text_template_text.get("1.0", tkinter.END).strip()
        image_path = self.parent.tk_label_file_path.cget("text")

        if self.parent.CheckVarText.get() == 0 and self.parent.CheckVarImage.get() == 0:
            tkinter.messagebox.showerror(title="错误", message="消息模板不能为空", )
            return (False, messageValue, image_path)
        
        # 如果消息是空的,不允许发送
        if self.parent.CheckVarText.get() == 1 and messageValue == "":
            tkinter.messagebox.showerror(title="错误", message="文本内容不能为空", )
            return (False, messageValue, image_path)

        if self.parent.CheckVarImage.get() == 1 and image_path == "":
            tkinter.messagebox.showerror(title="错误", message="文件地址不能为空", )
            return (False, messageValue, image_path)
        
        return (True, messageValue, image_path)

    
    async def on_send_msg(self):
        # print(len(globalTgClientList))
        # size = self.parent.tk_listbox_account.size()
        # print(size)
        # print(self.parent.groupList)

        print("准备发送消息...")

        result, messageValue, image_path = self.check_send_msg()
        if not result:
            return

        print("发送消息...")
        # self.parent.tk_listbox_account.delete(0, size - 1)


        # 获取一个实体号,拿到chat_id
        # 实体号也可能拿不到群/频道信息,没有进行群/频道的情况
        is_get_entity_flag = False # 是否有实体号,获取过群/频道信息
        entity_list = []
        for tg in globalTgClientList:
            me = await tg.get_me()
            if not me.bot:
                is_get_entity_flag = True
                for rec in self.parent.groupList:
                    if rec == "":
                        continue
                    print("groupList rec", rec)
                    try:
                        entity = await tg.get_entity(rec)
                        entity_list.append(entity)
                    except Exception as e:
                        print(e)
                for rec in self.parent.phoneList:
                    if rec == "":
                        continue
                    print("phoneList rec", rec)
                    try:
                        entity = await tg.get_entity(rec)
                        entity_list.append(entity)
                    except Exception as e:
                        print(e)
                break
        


        if len(entity_list) == 0 and not is_get_entity_flag:
            tkinter.messagebox.showerror(title="错误", message="必须添加一个非机器人账号", )
            return

        if len(entity_list) == 0 and is_get_entity_flag:
            tkinter.messagebox.showerror(title="错误", message="请检查待发送的账号和目标关系,是否无法发送?", )
            return

        for tg in globalTgClientList:
            for entity in entity_list:
                try:
                    # print(entity)
                    # 881890232
                    # 1815520607
                    # chat_id = (await tg.get_entity(rec)).id
                    # chat_id = 881890232
                    # chat_id = 1815520607
                    chat_id = entity.id
                    print(chat_id, )

                    if self.parent.CheckVarText.get() == 1:
                        me = await tg.get_me()
                        if not me.bot:
                            print("真人,发送人/群/频道", messageValue)
                            # 真人,发送人/群/频道
                            await tg.send_message(chat_id, messageValue)
                        else:
                            if type(entity) == User:
                                print("bot,发送人", messageValue)
                                # bot,发送人
                                # await tg(SendMessageRequest(PeerUser(chat_id), messageValue))
                                raise RuntimeError("bot无法发送人", messageValue)
                            else:
                                if entity.participants_count != None:
                                    print("bot,发送群", messageValue)
                                    # bot,发送群
                                    await tg(SendMessageRequest(PeerChat(chat_id), messageValue))
                                else:
                                    print("bot,发送频道", messageValue)
                                    # bot,发送频道
                                    await tg(SendMessageRequest(PeerChannel(chat_id), messageValue))
                        
                        


                    if self.parent.CheckVarImage.get() == 1:
                        await tg.send_file(chat_id, image_path)

                    self.schedulerTaskSuccessCount += 1
                    if not self.scheduler.running:
                        pass
                        # self.tk_label_send_status.config(text="发送成功", bg="#0f0")
                    else:
                        self.tk_label_send_status.config(text="")
                except Exception as e:
                    print("err", e)
                    self.schedulerTaskFailedCount += 1
                    if not self.scheduler.running:
                        pass
                        # self.tk_label_send_status.config(text="发送失败", bg="#f00") 
                    else:
                        self.tk_label_send_status.config(text="")

        if not self.scheduler.running:
            self.tk_label_send_status.config(text="执行完成,成功{0}次,失败{1}次".format(self.schedulerTaskSuccessCount, self.schedulerTaskFailedCount))

    async def send_msg(self):
        # 创建异步任务
        asyncio.create_task(self.on_send_msg())
        
        


    def schedulerListener(self, event):
        print("schedulerListener...", event)
        # get_jobs = self.scheduler.get_jobs()
        # print(get_jobs)
        # print_jobs = self.scheduler.print_jobs()
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
        result = tkinter.messagebox.askquestion(title="提示", message="确定立即发送?", icon="warning")
        if result != "yes":
            return
        await self.send_msg()


    @callback
    def on_schedule_send(self):
        result = tkinter.messagebox.askquestion(title="提示", message="确定定时发送?", icon="warning")
        if result != "yes":
            return
        result, _, _ = self.check_send_msg()
        if not result:
            return

        if self.scheduler.running:
            return

        self.tk_label_send_status.config(text="")

        isLoop = self.parent.CheckVarLoop.get() == 0

        startTimeValue = self.parent.tk_input_starttime.get().strip()
        secondsValue = self.parent.tk_input_intervals_seconds.get().strip()
        minuteValue=self.parent.tk_input_intervals_minutes.get().strip()
        hoursValue = self.parent.tk_input_intervals_hours.get().strip()
        daysValue = self.parent.tk_input_intervals_days.get().strip()
        timeValue = self.parent.tk_input_intervals_time.get().strip()
        endTimeValue = self.parent.tk_input_endstime.get().strip()
        self.scheduler.remove_all_jobs()
        self.scheduler.remove_listener(self.schedulerListener)
        if isLoop:
            if secondsValue != "":
                self.scheduler.add_job(
                    self.send_msg, 
                    trigger='interval', 
                    seconds=int(secondsValue),
                    start_date=startTimeValue,
                    end_date=endTimeValue,
                )
            elif minuteValue != "":
                self.scheduler.add_job(
                    self.send_msg, 
                    trigger='interval', 
                    minutes=int(minuteValue),
                    start_date=startTimeValue,
                    end_date=endTimeValue,
                )
            elif hoursValue != "":
                self.scheduler.add_job(
                    self.send_msg, 
                    trigger='interval', 
                    hours=int(hoursValue),
                    start_date=startTimeValue,
                    end_date=endTimeValue,
                )
            elif daysValue != "":
                self.scheduler.add_job(
                    self.send_msg, 
                    trigger='interval', 
                    days=int(daysValue),
                    start_date=startTimeValue,
                    end_date=endTimeValue,
                )
            else:
                tkinter.messagebox.showerror(title="错误", message="循环时刻不能都为空", )
                return
        else: 
            if timeValue != "":
                print("+", timeValue, "=")
                trigger = DateTrigger(
                    # run_date=datetime.now() + timedelta(seconds=100),
                    run_date=timeValue,
                    # timezone=timezone('Asia/Shanghai')
                )
                self.scheduler.add_job(
                    self.send_msg, 
                    # "date",
                    trigger=trigger, 
                    # run_date=datetime.strptime(timeValue, "%Y-%m-%d %H:%M:%S"),
                    # run_date=datetime.now() + timedelta(seconds=100),
                    # timezone=timezone('Asia/Shanghai')
                    # start_date=startTimeValue,
                    # end_date=endTimeValue,
                )
            else:
                tkinter.messagebox.showerror(title="错误", message="固定时间不能为空", )
                return
        
        self.scheduler.start()
        self.scheduler.add_listener(self.schedulerListener, )
            # mask=base.EVENT_JOB_REMOVED | base.EVENT_SCHEDULER_SHUTDOWN) # 任务监听

        print_jobs = self.scheduler.print_jobs()
        print(print_jobs)

        self.isScheduleTask = True
        self.schedulerTaskCount = 0
        self.schedulerTaskSuccessCount = 0
        self.schedulerTaskFailedCount = 0
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
        config.read("config_ini.ini", encoding="utf-8")
        enable = config.get("proxy", "enable")
        mode = config.get("proxy", "mode")
        host = config.get("proxy", "host")
        port = config.get("proxy", "port")

        if enable != None and mode != None and host != None and port != None and (enable == "1"):
            if str(mode).lower() == "socks5":
                self.client = TelegramClient(session, 
                        API_ID, 
                        API_HASH, 
                        proxy=(socks.SOCKS5, host, int(port)), 
                        loop=loop)
            elif str(mode).lower() == "http":
                self.client = TelegramClient(session, 
                        API_ID, 
                        API_HASH, 
                        proxy=(socks.HTTP, host, int(port)), 
                        loop=loop)
            else:
                self.client = TelegramClient(session=session,
                    api_id=API_ID,
                    api_hash=API_HASH, 
                    loop=loop)
        else:
            self.client = TelegramClient(session=session,
                api_id=API_ID,
                api_hash=API_HASH, 
                loop=loop)        
    
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
    app.setExit(False)


    def dd():
        result = tkinter.messagebox.askquestion(title="提示", message="确定退出?", icon="warning")
        if result != "yes":
            return

        print("dd")
        app.destroy()
        app.setExit(True)
        pass

    app.protocol('WM_DELETE_WINDOW', dd)


    try:
        while True:
            app.update()
            if app.exit():
                sys.exit(0)
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
    # asyncio.run(main())
    loop.run_until_complete(main())

    