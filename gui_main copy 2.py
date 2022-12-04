from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import tkinter as tk
import socks


class TelegramApp:
    def __init__(self, master):
        width = master.winfo_screenwidth() - round(master.winfo_screenwidth() * 0.5)
        height = master.winfo_screenheight() - round(master.winfo_screenheight() * 0.1)
        x = master.winfo_screenwidth() // 2 - width // 2
        y = master.winfo_screenheight() // 2 - height // 2
        master.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        self.createWidgets()

    
    def createWidgets(self):
        v = tk.IntVar()
        tk.Radiobutton(master=self.master, text="手机号", variable=v, value=1).pack(anchor=tk.W)
        tk.Radiobutton(master=self.master, text="Bot", variable=v, value=2).pack(anchor=tk.W)
        

        self.l1 = tk.Label(master=self.master, text="手机号")
        self.l1.pack(side=tk.LEFT)
        self.e1 = tk.Entry(master=self.master, bd=5)
        self.e1.pack(side=tk.LEFT)


        self.btn = tk.Button(master, text="登录", command=self.connect)
        self.btn.pack(side=tk.LEFT)

    def connect(self):
        phone = "8613950209512"
        client_name = "" + phone
        api_id = "9458299"   # api id
        api_hash = "b0cba0c5ad2b5aa5925ab52afedc3f83" # api hase
        client = TelegramClient(
                client_name,
                # "session/{phone_number}",
                api_id,
                api_hash,
                proxy=(socks.SOCKS5, 'localhost', 51837),
            )
        client.connect()
        if not client.is_user_authorized():
            # client.send_code_request(phone)
            # client.sign_in(phone, input('Enter the code: '))
            client.sign_in(bot_token="5797820537:AAFSi75rB-mci13W7IaIoJdwujaVSkRIdnU")
        else:
            # main()
            print("main()")
            pass

root = tk.Tk()
app = TelegramApp(root)
root.mainloop()