#!/usr/bin/python
# -*- coding: UTF-8 -*-

from telethon import TelegramClient, sync, events
import telethon
from telethon.tl.types import PeerUser, PeerChat, PeerChannel,UpdateNewChannelMessage
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl import types, functions
from telethon import utils
import socks
import time
import os
from utils.file_util import FileUtil


# telegram client
# 14759752148


basepath = os.path.abspath(__file__)
folder = os.path.dirname(basepath)
# data_path = os.path.join(folder, 'data.txt')

class TgClient:

    # 到https://my.telegram.org/用手机号登录这个网址申请api
    api_id = "9458299"   # api id
    api_hash = "b0cba0c5ad2b5aa5925ab52afedc3f83" # api hase
    client_name = "test123"
    use_proxy = True
    client = None

    phone_number = "+8613950209512"

    # 启动成功，输入 手机号码+验证码
    def __init__(self):
        print("send_code_request init...")
        if self.use_proxy:
            # 代理设置
            self.client = TelegramClient(
                self.client_name,
                # "session/{phone_number}",
                self.api_id,
                self.api_hash,
                proxy=(socks.SOCKS5, 'localhost', 51837),
            ).start()
        else:
            self.client = TelegramClient(self.client_name, self.api_id, self.api_hash).start()

        # sent = await self.client.send_code_request(phone="+86 13950209512", force_sms=True);
        # print("send_code_request...")


    def println(self, text):
        print("", text)

    def get_me(self):
        myself = self.client.get_me()
        self.println(myself)

    def xxx(self):
        peer = self.client.get_input_entity(phone_number, text)
        peer = utils.get_input_peer(peer)
        self.println(peer)

    # 发送消息，通过 手机号码，例如（+852 66125259）
    def send_message_by_phone(self, phone_number, text):
        result = self.client(SendMessageRequest(phone_number, text))

    # 发送消息，通过 用户名
    def send_message_by_username(self, username, text):
        result = self.client(SendMessageRequest(username, text))

    # 发送消息，通过 频道id
    def send_message_by_channel_id(self, channel_id, text):
        result = self.client(SendMessageRequest(PeerChannel(channel_id), text))

    # 发送消息，通过 频道name
    def send_message_by_channel_name(self, channel_name, text):
        entry = self.client.get_entity(channel_name)
        print(entry)
        result = self.client(SendMessageRequest(channel_name, text))

    # 获取消息列表信息
    def get_chat_list_info(self):
        try:
            for dialog in self.client.iter_dialogs():
                friend_info = self.client.get_entity(dialog.title)
                # 判断消息类型是 用户 还是 群/频道
                if type(friend_info) is not telethon.tl.types.User:
                    channel_id = friend_info.id
                    channel_title = friend_info.title
                    channel_username = ""
                    dict_channel_info = {"channel_id": channel_id, "channel_title": channel_title,
                                         "channel_username": channel_username}
                    print(dialog.title, "这是一个频道", dict_channel_info)
                else:
                    if friend_info.bot is False:
                        user_id = friend_info.id
                        user_name = friend_info.username
                        is_bot = friend_info.bot
                        user_phone = friend_info.phone
                        dict_user_info = {'user_id':user_id,'user_name':user_name,'user_phone':user_phone,'is_bot':is_bot}
                        print(dialog.title,"这是一个用户",dict_user_info)
                    else:
                        bot_id = friend_info.id
                        bot_name = friend_info.username
                        is_bot = friend_info.bot
                        dict_bot_info = {'bot_id':bot_id,'bot_name':bot_name,'is_bot':is_bot}
                        print(dialog.title,'这是一个机器人',dict_bot_info)

        except Exception as e:
            print("error", e)
            pass

    # 获取群信息
    def get_group_info(self, group_id):
        self.my_group = self.client.get_entity(PeerChat(group_id))
        print("my_group", self.my_group)

    # 获取频道信息
    def get_channel_info(self, channel_id):
        try:
            my_channel = self.client.get_entity(PeerChannel(channel_id))
            print("my_channel", my_channel, "\n")
        except Exception as e:
            print("get_channel_info err", e)
            pass
        


    # 获取群成员
    def get_group_participants(self, group_entity):
        for user in self.client.iter_participants(group_entity):
            print(user.id, user.username, user.first_name)
            time.sleep(5)

            data_path = os.path.join(folder, 'data_'+ str(group_entity.id) +'.txt')

            fileUtil = FileUtil()
            fileUtil.write_file(data_path, str(user.id) + "," + str(user.username) + "," + str(user.first_name) + '\n')


    def get_group_participants_read(self, group_entity):
        data_path = os.path.join(folder, 'data_' + str(group_entity.id) + '.txt')

        fileUtil = FileUtil()
        # fileUtil.read_file(data_path)

        return fileUtil.read_file_002(data_path)


    def is_group_participant(self, group_entity, entity):
        participant = self.get_group_participants_read(group_entity=group_entity)
        participant_array = participant.split("\n")
        participant_id_array = []
        for p in participant_array:
            participant_id = p.split(",")[0]
            # print("成员id", participant_id)
            participant_id_array.append(participant_id)

        # print(entity.id)
        # print(participant_id_array)

        # return "1499841284" in ["1499841284"]
        return str(entity.id) in participant_id_array



    def invite_join_my_channel(self):
        # 获取频道成员信息并将成员加入自己的群组或频道,并加入欢迎语
        for dialog in self.client.iter_dialogs():
            print("\n\n\n\n")
            try:
                friend_info = self.client.get_entity(dialog.title) #dialog.title为first_name
                # print(friend_info)
                if type(friend_info) is not telethon.tl.types.User:
                    channel_id = friend_info.id
                    channel_title = friend_info.title
                    # channel_username = friend_info.username
                    # dict_channel_info = {"channel_id":channel_id,"channel_title":channel_title,"channel_username":channel_username}
                    dict_channel_info = {"channel_id":channel_id,"channel_title":channel_title,"channel_username":None}
                    print(dialog.title,"这是一个频道",dict_channel_info)
                    channel = self.client.get_entity(PeerChat(channel_id))  # 根据群组id获取群组对  PeerChannel
                    responses = self.client.iter_participants(channel, aggressive=True) # 获取群组所有用户信息
                    for response in responses:
                        if response.username is not None:
                            d = {'id':response.id,'username':response.username}
                            print(d)
                            # time.sleep(2)
                            # self.client(InviteToChannelRequest(
                            # channel=1815520607,
                            # users = [d.get('username')],
                            # ))
                            # self.client.send_message(1815520607,'''✨Welcome to <a href="https://t.me/haimei_group">BiBi's group</a> chat {} !'''.format(d.get('username')) ,parse_mode="html")
                            # time.sleep(2) #防止出现UserPrivacyRestrictedError
            except Exception as e:
                print("error", e)
                pass


    # 解析群连接 eg: https://t.me/BinanceChinese
    def parseGroupLink(self, link):
        if "https://" in link:
            link = link[len("https://"):]
        # print("群分享连接", link)
        
        try:
            entry = self.client.get_entity(link)
            print("entry...", entry)
            return entry
        except Exception as e:
            print("e", e)
            pass


        

        # self.client.get_entity(PeerChat(1757008707))
       
       
        # id = self.client.get_peer_id("+8613950209512")
        # print("id...", id)


        # groupId = entry.id
        # groudUserName = entry.username
        #
        # return groupId, groudUserName
        return None


    # 根据群组链接,进群,并且发送一条消息,
    def joinToGroupLink(self, link, message):
        if "https://" in link:
            link = link[len("https://"):]
        entry = self.client.get_entity(link)
        from telethon.tl.functions.channels import JoinChannelRequest
        try: 
            self.client(JoinChannelRequest(entry))
            self.send_message_by_channel_id(entry.id, message)
        except Exception as e:
            print("joinToGroupLink happen err: " + e.message + ": " + str(e)) 




    # 邀请进群
    # 1 id，发送进群消息   2 username，直接进群
    def invite_join_channel(self, joinGroupLink, groupLink):

        join_group_entry = self.parseGroupLink(joinGroupLink)
        group_entry = self.parseGroupLink(groupLink)

        for user in self.client.iter_participants(group_entry):
            # print("频道", user.id, user.username, user.first_name)

            if self.is_group_participant(group_entity=group_entry, entity=user):
                print("跳过，已经在群内")
                continue

            id = user.id
            username = user.username
            print("user.id=", id, ",  user.username=", username)

            if username is None:

                # 1、 *** 没有设置username，通过id，发送一条邀请进群的消息 ***
                print("1.发消息给", id, username)
                # self.client.send_message(id,'''✨ 这个是一个能赚钱的群，群链接👉{} !'''.format(joinGroupLink) ,parse_mode="html")

            else:

                # 2、 *** 邀请有username，且未设置不可邀请的人，进入频道 ***
                from telethon.tl.functions.channels import InviteToChannelRequest
                chat_id = join_group_entry.id #频道
                users = [username]
                target_group_entity = self.client.get_entity(PeerChannel(chat_id))
                try:
                    print("2.直接邀请进群", id, username)
                    # res = self.client(InviteToChannelRequest(channel=target_group_entity, users=users ))
                except Exception as e:
                    print("spam protection: " + e.message + ": " + str(e))


            time.sleep(5)


