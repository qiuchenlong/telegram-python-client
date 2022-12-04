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

def saveAccountData(id, username):
    data = id + ","
    data += username + ","
    data += "\n"
    print("data...", data)
    fileUtil.write_file("{0}{1}".format(dataPath, "/account.csv"), data)

def saveData001(data):
    fileUtil.write_file_001("{0}{1}".format(dataPath, "/account.csv"), data)


def saveDataByName(name, data):
    fileUtil.write_file_001("{0}{1}".format(dataPath, "/"+name+".csv"), data)

def readDataByName(name):
    return fileUtil.read_file_002("{0}{1}".format(dataPath, "/"+name+".csv"))


def readData():
    return fileUtil.read_file_002("{0}{1}".format(dataPath, "/account.csv"))


# Some configuration for the app
TITLE = 'Telegram GUI'
SIZE = '1080x640'
REPLY = re.compile(r'\.r\s*(\d+)\s*(.+)', re.IGNORECASE)
DELETE = re.compile(r'\.d\s*(\d+)', re.IGNORECASE)
EDIT = re.compile(r'\.s(.+?[^\\])/(.*)', re.IGNORECASE)


def get_env(name, message, cast=str):
    if name in os.environ:
        return os.environ[name]
    while True:
        value = input(message)
        try:
            return cast(value)
        except ValueError as e:
            print(e, file=sys.stderr)
            time.sleep(1)


# Session name, API ID and hash to use; loaded from environmental variables
# SESSION = os.environ.get('TG_SESSION', 'gui')
# API_ID = get_env('TG_API_ID', 'Enter your API ID: ', int)
# API_HASH = get_env('TG_API_HASH', 'Enter your API hash: ')
SESSION = "gui"
API_ID = "9458299"
API_HASH = "b0cba0c5ad2b5aa5925ab52afedc3f83"

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


def sanitize_str(string):
    return ''.join(x if ord(x) <= 0xffff else
                   '{{{:x}ū}}'.format(ord(x)) for x in string)


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


def allow_copy(widget):
    """
    This helper makes `widget` readonly but allows copying with ``Ctrl+C``.
    """
    widget.bind('<Control-c>', lambda e: None)
    widget.bind('<Key>', lambda e: "break")


class App(tkinter.Tk):
    def setExit(self, value):
        self.exitValue = value
    def exit(self):
        return self.exitValue
    
    def setTitle(self, title):
        self.title(title)
    """
    Our main GUI application; we subclass `tkinter.Tk`
    so the `self` instance can be the root widget.

    One must be careful when assigning members or
    defining methods since those may interfer with
    the root widget.

    You may prefer to have ``App.root = tkinter.Tk()``
    and create widgets with ``self.root`` as parent.
    """
    def __init__(self, client, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cl = client
        self.me = None
        self.isScheduleTask = False
        self.schedulerTaskCount = 0

        self.twoSteps = False

        
        self.title(TITLE)
        self.geometry(SIZE)


        # header
        self.initHeader()
        



        self.initCenter()




        # footer
        self.initFooter()



        # The chat where to send and show messages from
        # tkinter.Label(self, text='Target chat(share link):').grid(row=1, column=0)
        # self.chat = tkinter.Entry(self)
        # self.chat.grid(row=1, column=1, columnspan=2, sticky=tkinter.EW)
        # self.columnconfigure(1, weight=1)
        # self.chat.bind('<Return>', self.check_chat)
        # self.chat.bind('<FocusOut>', self.check_chat)
        # self.chat.focus()
        # self.chat_id = None


        # # Message log (incoming and outgoing); we configure it as readonly
        # self.log = tkinter.scrolledtext.ScrolledText(self)
        # allow_copy(self.log)
        # self.log.grid(row=2, column=0, columnspan=3, sticky=tkinter.NSEW)
        # self.rowconfigure(2, weight=1)
        # self.cl.add_event_handler(self.on_message, events.NewMessage)

        # # Save shown message IDs to support replying with ".rN reply"
        # # For instance to reply to the last message ".r1 this is a reply"
        # # Deletion also works with ".dN".
        # self.message_ids = []

        # # Save the sent texts to allow editing with ".s text/replacement"
        # # For instance to edit the last "hello" with "bye" ".s hello/bye"
        # self.sent_text = collections.deque(maxlen=10)

        # tkinter.Button(self.frameCenter, text='Send',
        #         command=self.send_message).grid(row=3, column=2)



        # tkinter.Label(self, text='Target chat(phonenumber):').grid(row=4, column=0)
        # self.phonenumber = tkinter.Entry(self)
        # self.phonenumber.grid(row=4, column=1, columnspan=2, sticky=tkinter.EW)
        # self.columnconfigure(1, weight=1)
        # self.phonenumber.bind('<Return>', self.check_phonenumber)
        # self.phonenumber.bind('<FocusOut>', self.check_phonenumber)
        # self.phonenumber.bind('')
        # self.phonenumber.focus()
        # self.phonenumber_value = None

        # tkinter.Label(self, text='Message:').grid(row=5, column=0)
        # self.pMessage = tkinter.Entry(self)
        # self.pMessage.grid(row=5, column=1, columnspan=2, sticky=tkinter.EW)
        # self.columnconfigure(1, weight=1)
        

        



        # tkinter.Button(self, text='Start Task',
        #                command=self.start_task).grid(row=7, column=2)

        # # tkinter.Button(self, text='Start Task',
        # #                command=self.remove_task).grid(row=8, column=2)

        # tkinter.Button(self, text='Stop Task',
        #                command=self.stop_task).grid(row=9, column=2)


        # Post-init (async, connect client)
        asyncio.create_task(self.post_init())

        self.scheduler = AsyncIOScheduler()


    def initHeader(self):
        self.frameHeader = tkinter.LabelFrame(text="")
        self.frameHeader.grid(row=0, column=0, columnspan=5)

        # Signing in row; the entry supports phone and bot token
        self.sign_in_label = tkinter.Label(self.frameHeader, text='Loading...')
        self.sign_in_label.grid(row=1, column=0)
        self.sign_in_entry = tkinter.Entry(self.frameHeader)
        self.sign_in_entry.grid(row=1, column=1, sticky=tkinter.EW)
        self.sign_in_entry.bind('<Return>', self.sign_in)
        self.sign_in_button = tkinter.Button(self.frameHeader, text='...',
                                             command=self.sign_in)
        self.sign_in_button.grid(row=1, column=2)
        self.code = None

        # Add Account
        self.add_account_button = tkinter.Button(self.frameHeader, text="添加账号", command=self.add_account)
        self.add_account_button.grid(row=1, column=3)

        self.add_account_button = tkinter.Button(self.frameHeader, text="读取账号", command=self.read_account)
        self.add_account_button.grid(row=1, column=4)




    def initCenter(self):
        # ========================== Account =========================
        self.frameAccount = tkinter.LabelFrame(text="")
        self.frameAccount.grid(row=1, column=0)

        tkinter.Label(self.frameAccount, text='账号列表').grid(row=0, column=0)
     

        data = readData()
        accountData = data.split("\n");


        self.account_data = accountData
        self.accountListbox = tkinter.Listbox(self.frameAccount, selectmode=tkinter.EXTENDED, height=12)
        self.accountListbox.grid(row=1, column=0)
        for i in range(len(self.account_data)):
            self.accountListbox.insert(tkinter.END, self.account_data[i])


        tkinter.Button(self.frameAccount, text='删除账号',
                command=self.delete_account).grid(row=2, column=0)

        tkinter.Button(self.frameAccount, text="批量登录",
                command=self.batch_login).grid(row=2, column=0)

        # for i in range(len(self.account_data)):
        #     CheckVar1 = tkinter.IntVar()
        #     C1 = tkinter.Checkbutton(self.frameAccount, text = self.account_data[i], variable = CheckVar1, \
        #                 onvalue = 1, offvalue = 0, width=20)
        #     C1.grid(row=i+1, column=0)


        # CheckVar1 = tkinter.IntVar()
        # CheckVar2 = tkinter.IntVar()
        # C1 = tkinter.Checkbutton(self.frameAccount, text = "Music", variable = CheckVar1, \
        #                 onvalue = 1, offvalue = 0, width=20)
        # C2 = tkinter.Checkbutton(self.frameAccount, text = "Video", variable = CheckVar2, \
        #                 onvalue = 1, offvalue = 0, width=20)
        # C1.grid(row=1, column=0)
        # C2.grid(row=2, column=0)


        


        # ========================== Time =========================
        self.frameTime = tkinter.LabelFrame(text="")
        self.frameTime.grid(row=1, column=1)

        frameStartTime = tkinter.Frame(self.frameTime)
        tkinter.Label(frameStartTime, text='开始时间\n(校准,eg: 2022-11-11 12:00:00)').grid(row=0, column=0)
        self.startTime = tkinter.Entry(frameStartTime, width=20)
        self.startTime.grid(row=1, column=0, sticky=tkinter.EW)
        self.startTime.insert(0, "" + beijing_now.strftime("%Y-%m-%d %H:%M:%S"))
        # self.startTime.bind('<Return>', self.send_message)
        frameStartTime.grid(row=0, column=0)


        frameLoopTime = tkinter.Frame(self.frameTime)
        tkinter.Label(frameLoopTime, text='间隔时间(eg: 1s)').grid(row=0, column=0)
        self.loopTime = tkinter.Entry(frameLoopTime, width=20)
        self.loopTime.grid(row=1, column=0, sticky=tkinter.EW)
        self.loopTime.insert(0, "" + str(INTERVAL_TIME))
        # self.loopTime.bind('<Return>', self.send_message)
        frameLoopTime.grid(row=1, column=0)


        frameEndTime = tkinter.Frame(self.frameTime)
        tkinter.Label(frameEndTime, text='结束时间\n(默认加6小时)').grid(row=0, column=0)
        self.endTime = tkinter.Entry(frameEndTime, width=20)
        self.endTime.grid(row=1, column=0, sticky=tkinter.EW)
        delta = timedelta(hours=6)
        self.endTime.insert(0, "" + (beijing_now + delta).strftime("%Y-%m-%d %H:%M:%S"))
        # self.startTime.bind('<Return>', self.send_message)
        frameEndTime.grid(row=2, column=0)


        # ========================== Content =========================
        self.frameContent = tkinter.LabelFrame(text="")
        self.frameContent.grid(row=1, column=2)



        # self.frameTemplateCheckout = tkinter.Frame(self.frameContent)
        # self.frameTemplateCheckout.grid(row=0, column=0)
        self.CheckVarText = tkinter.IntVar(value=1)
        self.CheckVarImage = tkinter.IntVar(value=0)





        self.frameTemplateContainer = tkinter.Frame(self.frameContent)
        self.frameTemplateContainer.grid(row=0, column=0)



          # Sending messages
        tkinter.Label(self.frameTemplateContainer, text='消息模板').grid(row=0, column=0)

        self.checkText = tkinter.Checkbutton(self.frameTemplateContainer, variable=self.CheckVarText)
        self.checkText.grid(row=1, column=0)

        self.message = tkinter.Text(self.frameTemplateContainer, width=30, height=20,)
        self.message.grid(row=1, column=1, rowspan=1, sticky=tkinter.EW)
        # self.message.bind('<Return>', self.send_message)
        self.message.insert(tkinter.END, "测试时间:" + beijing_now.strftime("%Y-%m-%d %H:%M:%S"))




        self.checkImage = tkinter.Checkbutton(self.frameTemplateContainer, variable=self.CheckVarImage)
        self.checkImage.grid(row=2, column=0)

        tkinter.Button(self.frameTemplateContainer, text='选择本地图片',
        command=self.select_photo).grid(row=2, column=1)
        self.messageTemplateImage = tkinter.Label(self.frameTemplateContainer, text='路径:')
        self.messageTemplateImage.grid(row=3, column=1)



        
        



        # ========================== Group =========================
        self.frameGroup = tkinter.LabelFrame(text="")
        self.frameGroup.grid(row=1, column=3)

        tkinter.Label(self.frameGroup, text='Group/Channel').grid(row=0, column=0)
        self.group = tkinter.Text(self.frameGroup, width=30, height=10)
        self.group.grid(row=1, column=0, sticky=tkinter.EW)
        # self.group.bind('<Return>', self.onGroupOrChannel)

        groupLinkData = readDataByName("groupLink")
        groupLinkDatas = groupLinkData.split("\n")
        for groupLink in groupLinkDatas:
            self.group.insert(tkinter.END, groupLink + "\n")

        # self.group.insert(tkinter.END, "https://t.me/+WTEnWAazodlhZGQ1\n")
        # self.group.insert(tkinter.END, "https://t.me/+oG2Tyey6OBQxNThl\n")

        tkinter.Button(self.frameGroup, text='保存群组链接',
                command=self.saveGroupLink).grid(row=2, column=0)
        # tkinter.Button(self.frameGroup, text='删除群组链接',
        #         command=self.addGroupLink).grid(row=2, column=1)


        tkinter.Label(self.frameGroup, text='Or').grid(row=3, column=0)

        tkinter.Label(self.frameGroup, text='PhoneNumber').grid(row=4, column=0)
        self.phonenumber = tkinter.Text(self.frameGroup, width=30, height=10)
        self.phonenumber.grid(row=5, column=0, sticky=tkinter.EW)
        # self.phonenumber.bind('<Return>', self.send_message)


        phoneNumberData = readDataByName("phoneNumber")
        phoneNumberDatas = phoneNumberData.split("\n")
        for phoneNumber in phoneNumberDatas:
            self.phonenumber.insert(tkinter.END, phoneNumber + "\n")
        # self.phonenumber.insert(tkinter.END, "+85266125259")


        tkinter.Button(self.frameGroup, text='保存手机号码',
                command=self.savePhoneNumber).grid(row=6, column=0)
        # tkinter.Button(self.frameGroup, text='删除手机号码',
        #         command=self.addGroupLink).grid(row=6, column=1)








    def initFooter(self):
        self.frameFooter = tkinter.LabelFrame(text="")
        self.frameFooter.grid(row=2, column=0, columnspan=4)

        tkinter.Button(self.frameFooter, text='立即发送',
                       command=self.send_message_by_now).grid(row=0, column=3)

        tkinter.Button(self.frameFooter, text='定时发送',
                       command=self.send_message_by_schedule).grid(row=0, column=4)

        tkinter.Button(self.frameFooter, text='停止发送',
                       command=self.send_message_by_schedule_stop).grid(row=0, column=5)

        self.scheduleTask = tkinter.Label(
            self.frameFooter, 
            text='定时任务:'+ ("运行中" if self.isScheduleTask else "未运行"),
            bg='yellow'
        )
        self.scheduleTask.grid(row=1, column=4)


    async def post_init(self):
        """
        Completes the initialization of our application.
        Since `__init__` cannot be `async` we use this.
        """
        if await self.cl.is_user_authorized():
            try:
                self.set_signed_in(await self.cl.get_me())
            except Exception as e:
                pass
        else:
            # User is not logged in, configure the button to ask them to login
            self.sign_in_button.configure(text='Sign in')
            self.sign_in_label.configure(
                text='Sign in (phone/token):')

    async def on_message(self, event):
        """
        Event handler that will add new messages to the message log.
        """
        # We want to show only messages sent to this chat
        if event.chat_id != self.chat_id:
            return

        # Save the message ID so we know which to reply to
        self.message_ids.append(event.id)

        # Decide a prefix (">> " for our messages, "<user>" otherwise)
        if event.out:
            text = '>> '
        else:
            sender = await event.get_sender()
            text = '<{}> '.format(sanitize_str(
                utils.get_display_name(sender)))

        # If the message has media show "(MediaType) "
        if event.media:
            text += '({}) '.format(event.media.__class__.__name__)

        text += sanitize_str(event.text)
        text += '\n'

        # Append the text to the end with a newline, and scroll to the end
        self.log.insert(tkinter.END, text)
        self.log.yview(tkinter.END)

    # noinspection PyUnusedLocal
    @callback
    async def sign_in(self, event=None):
        """
        Note the `event` argument. This is required since this callback
        may be called from a ``widget.bind`` (such as ``'<Return>'``),
        which sends information about the event we don't care about.

        This callback logs out if authorized, signs in if a code was
        sent or a bot token is input, or sends the code otherwise.
        """
        self.sign_in_label.configure(text='Working...')
        self.sign_in_entry.configure(state=tkinter.DISABLED)
        if await self.cl.is_user_authorized():
            await self.cl.log_out()
            self.destroy()
            sys.exit(0)
            return

        value = self.sign_in_entry.get().strip()
        if self.code:
            signLabel = self.sign_in_label.cget("text")
            print("signLabel...", signLabel)
            if signLabel == "Two-steps verification:" or self.twoSteps:
                self.set_signed_in(await self.cl.sign_in(password=value))
                return

            try:
                self.set_signed_in(await self.cl.sign_in(code=value))
            except telethon.errors.SessionPasswordNeededError:
                self.twoSteps = True
                self.sign_in_label.configure(text='Two-steps verification:')
                self.sign_in_entry.configure(state=tkinter.NORMAL)
                self.sign_in_entry.delete(0, tkinter.END)
                self.sign_in_entry.focus()
                # self.set_signed_in(await self.cl.sign_in(password="Cindy1024"))
            except Exception as e:
                print("e", e)

        elif ':' in value:
            self.set_signed_in(await self.cl.sign_in(bot_token=value))
        else:
            self.code = await self.cl.send_code_request(value)
            self.sign_in_label.configure(text='Code:')
            self.sign_in_entry.configure(state=tkinter.NORMAL)
            self.sign_in_entry.delete(0, tkinter.END)
            self.sign_in_entry.focus()
            return

    @callback
    def add_account(self, event=None):
        print("添加账号")
        account = self.me
        username = utils.get_display_name(self.me)
        self.accountListbox.insert(tkinter.END, "{0},{1}".format(str(account.id), username))
        saveAccountData(str(account.id), username)

    
    def read_account(self):
        data = readData()
        print("data...", data)
        accountData = data.split("\n")
        size = self.accountListbox.size()
        print("size...", size)
        self.accountListbox.delete(0, size-1)

        for i in range(0, len(accountData)):
            self.accountListbox.insert(tkinter.END, accountData[i])




   
    @callback
    def delete_account(self, event=None):
        print("删除账号")
        select = self.accountListbox.curselection()
        print(select)
        data = readData()
        accountData = data.split("\n")

        print(len(accountData), accountData)

        if len(select) == 0:
            return

        start = select[0]
        end = select[len(select) - 1]
        print(start, end)
        del accountData[start: end]
        self.accountListbox.delete(start, end) # 删除listbox组件的数据
        
        print("accountData", accountData)

        d = ""
        for account in accountData:
            if account != "":
                d += ''.join(account + "\n")
        print("d...", d)
        
        saveData001(d)
        

    @callable
    def batch_login(self, event=None):
        print("批量登录")



    
    @callback
    def select_photo(self, event=None):
        filename = tkinter.filedialog.askopenfilename()
        if filename != "":
            self.messageTemplateImage.config(text="{0}".format(filename))
        else:
            self.messageTemplateImage.config("没有选择图片文件")






    def set_signed_in(self, me):
        """
        Configures the application as "signed in" (displays user's
        name and disables the entry to input phone/bot token/code).
        """
        self.me = me
        self.sign_in_label.configure(text='Signed in')
        self.sign_in_entry.configure(state=tkinter.NORMAL)
        self.sign_in_entry.delete(0, tkinter.END)
        try:
            self.sign_in_entry.insert(tkinter.INSERT, utils.get_display_name(me))
            self.account_data.append(utils.get_display_name(me))
        except Exception as e:
            pass
        self.sign_in_entry.configure(state=tkinter.DISABLED)
        self.sign_in_button.configure(text='Log out')
        self.chat.focus()






    @callback
    async def onGroupOrChannel(self):
        pass


    @callback
    async def send_message_by_now(self):
        await self.send_msg()


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
            text='定时任务:'+ ("运行中, 已执行{0}次".format(self.schedulerTaskCount) if self.isScheduleTask else "未运行"),
            bg="red" if self.isScheduleTask else "yellow"
        )
        


    @callback
    async def send_message_by_schedule(self):
        if self.scheduler.running:
            return

        startTimeValue = self.startTime.get().strip()
        loopTimeValue = self.loopTime.get().strip()
        endTimeValue = self.endTime.get().strip()
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
            text='定时任务:'+ ("运行中, 已执行{0}次".format(self.schedulerTaskCount) if self.isScheduleTask else "未运行"),
            bg='red'
        )

    


    @callback
    async def send_message_by_schedule_stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)





    @callback
    async def addGroupLink(self):
        print("添加群组链接")
        self.showaddGroupLinkDialog("1", "2")


    @callback
    async def saveGroupLink(self, event=None):
        print("保存群组链接")
        groupLinkData = self.group.get("1.0", tkinter.END).strip()
        print(groupLinkData)
        saveDataByName("groupLink", groupLinkData)

    @callback
    async def savePhoneNumber(self, event=None):
        phoneNumberData = self.phonenumber.get("1.0", tkinter.END).strip()
        print(phoneNumberData)
        saveDataByName("phoneNumber", phoneNumberData)


    ## ========================================= add group link begin ===============================================
    def showaddGroupLinkDialog(self, title, content):
        self.addGroupLinkDialog = tkinter.Toplevel(self)
        self.myLabel = tkinter.Label(self.addGroupLinkDialog, text='Enter your group link')
        self.myLabel.pack()

        self.myGroupLink = tkinter.Entry(self.addGroupLinkDialog)
        self.myGroupLink.pack()

        self.mySubmitButton = tkinter.Button(self.addGroupLinkDialog, text='Submit', command=self.addGroupLinkHandle)
        self.mySubmitButton.pack()

    def addGroupLinkHandle(self):
        groupLink = self.myGroupLink.get().strip()
        print("群组链接: ", groupLink)
        self.group.insert(tkinter.END, "{0}\n".format(groupLink))
        self.addGroupLinkDialog.destroy()
    ## ========================================= add group link end ===============================================



    async def send_msg(self):
        messageValue = self.message.get("1.0", tkinter.END).strip()
        print(messageValue)

        groupValue = self.group.get("1.0", tkinter.END).strip()
        phonenumberValue = self.phonenumber.get("1.0", tkinter.END).strip()


        print("CheckVarText...", self.CheckVarText.get())
        print("CheckVarImage...", self.CheckVarImage.get())


        for g in groupValue.split("\n"):
            if g == "":
                continue
            print(g)
            try:
                chat_id = (await self.cl.get_entity(g)).id

                if self.CheckVarText.get() == 1:
                    await self.cl.send_message(chat_id, messageValue)

                if self.CheckVarImage.get() == 1:
                    image_path = self.messageTemplateImage.cget("text")
                    print("image_path...", image_path)
                    if image_path != "":
                        await self.cl.send_file(chat_id, image_path)

                # await self.cl(SendMessageRequest(g, messageValue))
            except Exception as e:
                print("err...", e)
                pass

        for p in phonenumberValue.split("\n"):
            if p == "":
                continue
            print(p)
            try:
                await self.cl.send_message(p, messageValue)
                # await self.cl(SendMessageRequest(p, messageValue))
            except Exception as e:
                print("err...", e)
                pass




    @callback
    async def start_task(self):
        # self.scheduler.add_job(task_001, 'interval', seconds=2, id="task_001")
        # self.scheduler.add_job(task_001, 'interval', seconds=1, id="task_002")
        self.scheduler.add_job(self.send_sp_message, 'interval', seconds=3)
        self.scheduler.start()

    @callback
    async def remove_task(self):
        self.scheduler.remove_job(job_id="task_002")


    @callback
    async def stop_task(self):
        self.scheduler.shutdown()



    @callback
    async def send_simple_message(self, event=None):
        # phonenumber_value = self.phonenumber.get().strip()
        # pMessage_value = self.pMessage.get().strip()
        # await self.cl.send_message(phonenumber_value, pMessage_value)
        await self.send_sp_message()


    async def send_sp_message(self):
        phonenumber_value = self.phonenumber.get().strip()
        pMessage_value = self.pMessage.get().strip()
        await self.cl.send_message(phonenumber_value, pMessage_value)

        

    # noinspection PyUnusedLocal
    @callback
    async def send_message(self, event=None):
        """
        Sends a message. Does nothing if the client is not connected.
        """
        if not self.cl.is_connected:
            return

        # The user needs to configure a chat where the message should be sent.
        #
        # If the chat ID does not exist, it was not valid and the user must
        # configure one; hint them by changing the background to red.
        if not self.chat_id:
            self.chat.configure(bg='red')
            self.chat.focus()
            return

        # Get the message, clear the text field and focus it again
        text = self.message.get().strip()
        self.message.delete(0, tkinter.END)
        self.message.focus()
        if not text:
            return

        # NOTE: This part is optional but supports editing messages
        #       You can remove it if you find it too complicated.
        #
        # Check if the edit matches any text
        m = EDIT.match(text)
        if m:
            find = re.compile(m.group(1).lstrip())
            # Cannot reversed(enumerate(...)), use index
            for i in reversed(range(len(self.sent_text))):
                msg_id, msg_text = self.sent_text[i]
                if find.search(msg_text):
                    # Found text to replace, so replace it and edit
                    new = find.sub(m.group(2), msg_text)
                    self.sent_text[i] = (msg_id, new)
                    await self.cl.edit_message(self.chat_id, msg_id, new)

                    # Notify that a replacement was made
                    self.log.insert(tkinter.END, '(message edited: {} -> {})\n'
                                    .format(msg_text, new))
                    self.log.yview(tkinter.END)
                    return

        # Check if we want to delete the message
        m = DELETE.match(text)
        if m:
            try:
                delete = self.message_ids.pop(-int(m.group(1)))
            except IndexError:
                pass
            else:
                await self.cl.delete_messages(self.chat_id, delete)
                # Notify that a message was deleted
                self.log.insert(tkinter.END, '(message deleted)\n')
                self.log.yview(tkinter.END)
                return

        # Check if we want to reply to some message
        reply_to = None
        m = REPLY.match(text)
        if m:
            text = m.group(2)
            try:
                reply_to = self.message_ids[-int(m.group(1))]
            except IndexError:
                pass

        # NOTE: This part is no longer optional. It sends the message.
        # Send the message text and get back the sent message object
        message = await self.cl.send_message(self.chat_id, text,
                                             reply_to=reply_to)

        # Save the sent message ID and text to allow edits
        self.sent_text.append((message.id, text))

        # Process the sent message as if it were an event
        await self.on_message(message)

    @callable
    async def check_phonenumber(self, event=None):
        print("check_phonenumber")
        phonenumber_value = self.phonenumber.get().strip()

        print("check_phonenumber", phonenumber_value)
        # if self.phonenumber_value is None:
        #     return
        self.phonenumber_value = phonenumber_value
        print("")

    # noinspection PyUnusedLocal
    @callback
    async def check_chat(self, event=None):
        """
        Checks the input chat where to send and listen messages from.
        """
        if self.me is None:
            return  # Not logged in yet

        chat = self.chat.get().strip()
        try:
            chat = int(chat)
        except ValueError:
            pass

        try:
            old = self.chat_id
            # Valid chat ID, set it and configure the colour back to white
            print("===>>>", old)
            print("===>>>", chat)
            # print("===>>>", self.cl.)
            self.chat_id = (await self.cl.get_entity(chat)).id
            self.chat.configure(bg='white')

            # If the chat ID changed, clear the
            # messages that we could edit or reply
            if self.chat_id != old:
                self.message_ids.clear()
                self.sent_text.clear()
                self.log.delete('1.0', tkinter.END)
                if not self.me.bot:
                    for msg in reversed(
                            await self.cl.get_messages(self.chat_id, 100)):
                        await self.on_message(msg)
        except ValueError:
            # Invalid chat ID, let the user know with a yellow background
            self.chat_id = None
            self.chat.configure(bg='yellow')




async def main(interval=0.05):
    pass
    
    print("sessionPath...", sessionPath)
    if not os.path.exists(sessionPath):
        os.makedirs(sessionPath)

    appName = "app"
    if readApp() != "":
        appName = readApp()
    session = "{0}/{1}".format(sessionPath, SESSION+"_"+appName)

    # client = TelegramClient(session, API_ID, API_HASH)

    enable, mode, host, port = readConfig()
    print(enable, mode, host, port)
    if enable != None and mode != None and host != None and port != None and (enable == "True" or enable == "true"):
        print(1)
        if str(mode).lower() == "socks5":
            client = TelegramClient(session, API_ID, API_HASH, proxy=(socks.SOCKS5, host, int(port)))
        elif str(mode).lower() == "http":
            client = TelegramClient(session, API_ID, API_HASH, proxy=(socks.HTTP, host, int(port)))
        else:
            client = TelegramClient(session, API_ID, API_HASH)
    else:    
        print(2)
        client = TelegramClient(session, API_ID, API_HASH)
    

    try:
        await client.connect()
    except Exception as e:
        print('Failed to connect', e, file=sys.stderr)
        return

    app = App(client)
    app.setTitle("Telegram GUI, {}".format(appName))
    app.setExit(False)

    def dd():
        print("dd")
        app.destroy()
        app.setExit(True)
        pass

    app.protocol('WM_DELETE_WINDOW', dd)


    try:
        while True:
            # We want to update the application but get back
            # to asyncio's event loop. For this we sleep a
            # short time so the event loop can run.
            #
            # https://www.reddit.com/r/Python/comments/33ecpl
            app.update()
            # sys.exit(0)

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
        await app.cl.disconnect()

    # app.protocol('WM_DELETE_WINDOW', destroy(app))
    





# def task_001():
#     print(beijing_now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])

# from PIL import Image
# from PIL import ImageTk


# class MY_GUI():
#     def __init__(self,init_window_name):
#         self.init_window_name = init_window_name


#     #设置窗口
#     def set_init_window(self):
#         self.init_window_name.title("Telegram 群发工具_v1.0.0")           #窗口名
#         #self.init_window_name.geometry('320x160+10+10')                         #290 160为窗口大小，+10 +10 定义窗口弹出时的默认展示位置
#         self.init_window_name.geometry('1068x681+10+10')
#         #self.init_window_name["bg"] = "pink"                                    #窗口背景色，其他背景色见：blog.csdn.net/chl0000/article/details/7657887
#         #self.init_window_name.attributes("-alpha",0.9)                          #虚化，值越小虚化程度越高
        

# def main_001():
#     init_window = tkinter.Tk()
#     ZMJ_PORTAL = MY_GUI(init_window)
#     # 设置根窗口默认属性
#     ZMJ_PORTAL.set_init_window()

#     init_window.mainloop()          #父窗口进入事件循环，可以理解为保持窗口运行，否则界面不展示


def readTitle():
    try:
        config = configparser.ConfigParser()
        config.read("config_ini.ini")
        title = config.get("baseconfig", "title")
        return title
    except Exception as e:
        pass
    return "Telegram GUI"
def readApp():
    try:
        config = configparser.ConfigParser()
        config.read("config_ini.ini")
        title = config.get("baseconfig", "app")
        return title
    except Exception as e:
        pass
    return ""
TITLE = readTitle()


def readConfig():
    try:
        config = configparser.ConfigParser()
        basepath = os.path.abspath(__file__)
        folder = os.path.dirname(basepath)
        print("folder...", folder)
        config.read("config_ini.ini")
        proxy = config.options("proxy")
        enable = config.get("proxy", "enable")
        mode = config.get("proxy", "mode")
        host = config.get("proxy", "host")
        port = config.get("proxy", "port")


        return (enable, mode, host, port)
    except Exception as e:
        pass
    return (None, None, None, None)


# root = tkinter.Tk()
# def create():
#     # top = tkinter.Toplevel()
#     # top.title("Python")

#     app = entry.get().strip()
#     print(app)
#     config = configparser.ConfigParser()
#     config.read("config_ini.ini")
#     config.set("baseconfig", "app", app)
#     with open("config_ini.ini", "w") as configFile:
#         config.write(configFile)


    
#     root.destroy()

#     asyncio.run(main())



    
entry = None

if __name__ == "__main__":
    # title = readApp()
    # if title == "":
    #     title = "请输入名称"
    # tkinter.Label(root, text="名称").grid(row=0, column=0)
    # entry = tkinter.Entry(root)
    # entry.grid(row=0, column=1)
    # entry.insert(tkinter.END, title)
    # tkinter.Button(root, text="Connect", command=create).grid(row=1, column=0)
    # tkinter.mainloop()

    asyncio.run(main())

    