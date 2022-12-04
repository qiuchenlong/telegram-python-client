import itertools
import os
import time
from core.tg_client import TgClient
from utils.file_util import FileUtil
from utils.excel_util import ExcelUtil



basepath = os.path.abspath(__file__)
folder = os.path.dirname(basepath)


def get_excel_data(path):
    excelUtil = ExcelUtil()
    result_list = excelUtil.read_file(path)
    return result_list

def SendUsername(client):
    result_list = get_excel_data(folder + "/datas/data_usernames.xlsx")
    for row_data in result_list:
        username = str(row_data[0])
        message = str(row_data[1])
        client.send_message_by_username(username, message)
    

def SendChannelMessageByIdMore(client):
    result_list = get_excel_data(folder + "/datas/data_channel_ids.xlsx")
    for row_data in result_list:
        channel_id = int(row_data[0])
        message = str(row_data[1])
        client.send_message_by_channel_id(channel_id, message)

def SendChannelMessageByNameMore(client):
    result_list = get_excel_data(folder + "/datas/data_channel_names.xlsx")
    for row_data in result_list:
        channel_name = str(row_data[0])
        message = str(row_data[1])
        client.send_message_by_channel_name(channel_name, message)

def FindEnableGroup(client):
    # 881890232 这个是可用的群组id
    # 1815520607 这个是可用的频道id
    for i in range(1244136556, 1244136557):
        client.get_group_info(i)
        # time.sleep(3)


def JoinToGroup(client):
    message = "有小姐姐私我吗?我想要"
    groupLinkList = []
    groupLinkList.append("https://t.me/SexChina2020")
    # FORBIDDEN: You can't write in this chat (caused by SendMessageRequest)
    # 下面这个群,加入了群,但无法发消息
    groupLinkList.append("https://t.me/laosijizhibojiaoliu")
    # BAD_REQUEST: You have successfully requested to join this chat or channel (caused by JoinChannelRequest)
    # 下面这个群,无法加入群
    groupLinkList.append("https://t.me/gtkankan555")
    groupLinkList.append("https://t.me/qwaiwei")

    for link in groupLinkList:
        client.joinToGroupLink(link, message)
        time.sleep(3)


# 总共62个字符
# chars = ["a", "b", "c", "d", "e", "f", "g", "h",
#                 "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
#                 "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5",
#                 "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H",
#                 "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
#                 "U", "V", "W", "X", "Y", "Z"]
chars = ["a", "b", "c", "d", "e", "f", "g", "h",
                "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5",
                "6", "7", "8", "9"]
# chars = ["a", "b", "c", "d", "e", "f", "g", "h",
#                 "0", "1", "2", "3", "4", "5",
#                 "6", "7", "8", "9"]

# 1 digit: 62
# 2 digit: 62x62 + 62 = 62x(62 + 1) = 3906
# 3 digit: 62x62x62 + 3906 = 62x62x62 + 62x62 + 62 = 62x(62x62 + 62 + 1) = 242234
# 4 digit: 62x(62x62x62 + 62x62 + 62 + 1) = 15018570

list = []
def GenerateLink(digits):
    # list = []
    # for i in range(0, len(chars)):
    #     list.append(chars[i])

    # for i in range(0, len(chars)):
    #     for j in range(0, len(chars)):
    #         list.append(chars[i] + chars[j])

    # for i in range(0, len(chars)):
    #     for j in range(0, len(chars)):
    #         for z in range(0, len(chars)):
    #             list.append(chars[i] + chars[j] + chars[z])

    # for i in range(0, len(chars)):
    #     for j in range(0, len(chars)):
    #         for z in range(0, len(chars)):
    #             for x in range(0, len(chars)):
    #                 list.append(chars[i] + chars[j] + chars[z] + chars[x])
    
    # for i in range(0, digits):
        # recursion(n=i)

    # recursion(n=digits)
    recursion2(n=digits)

    # for i in itertools.product(chars):
    #     list.append(i)  

    # print(list)
    print(len(list)) 
    return list

def recursion(n):
    if n == 0 :
        return 1
    for i in itertools.product(chars, repeat=n):
        # print("".join(i))
        list.append("".join(i)) 
    return n + recursion(n - 1)

def recursion2(n):
    for i in itertools.product(chars, repeat=n):
        string = "".join(i)
        isPass = False
        for j in range(0, n - 2):
            if string[j].isdigit():
                isPass = True
        if isPass:
            continue
        # if string[0].isdigit() or \
        #     (string[0].isdigit() and string[1].isdigit()) or \
        #     (string[0].isdigit() and string[1].isdigit() and string[2].isdigit()) or \
        #     (string[0].isdigit() and string[1].isdigit() and string[2].isdigit() and string[3].isdigit()) or \
        #     (string[0].isdigit() and string[1].isdigit() and string[2].isdigit() and string[3].isdigit() and string[4].isdigit()) or \
        #     (string[0].isdigit() and string[1].isdigit() and string[2].isdigit() and string[3].isdigit() and string[4].isdigit() and string[5].isdigit()):
        #     continue
        list.append(string) 




if __name__ == '__main__':



    tgClient = TgClient()
    tgClient.println("Telegram client, Ready...")
    tgClient.get_me()

    # 0、通过username,群发消息(私聊,1v1)
    # SendUsername(tgClient)

    # 1、通过channel_id,群发消息(频道)
    # SendChannelMessageByIdMore(tgClient)

    # 2、通过channel_name,群发消息(频道)
    # SendChannelMessageByNameMore(tgClient)

    # 查找可用的群id
    # FindEnableGroup(tgClient)

    # 未加入该群[sm2000],获取群信息
    entryTemp = tgClient.parseGroupLink("https://t.me/sm2000")
    # tgClient.parseGroupLink(1757008707)

    # 3、通过群链接,加入群组 (批量)
    # JoinToGroup(tgClient)


    # tgClient.send_message_by_channel_name("SexChina2020", "Hello...")



    # tgClient.get_chat_list_info()

    # ## 频道
    # tgClient.get_channel_info(1815520607)

    # # # tgClient.get_me()
    # # # tgClient.invite_join_my_channel()
    # #
    # # # 1、解析群连接
    # GroupLink = "https://t.me/BinanceChinese"
    # notGroupLink = "https://t.me/T3mn_mot"
    # # group_entry = tgClient.parseGroupLink(notGroupLink)
    # # tgClient.get_group_participants(group_entity=group_entry)


    # ChannelLink = "https://t.me/+oG2Tyey6OBQxNThl"

    # # tgClient.invite_join_channel(GroupLink, notGroupLink)
    # tgClient.invite_join_channel(GroupLink, GroupLink)


    # 1 没有
    # 2 没有
    # 3 有, 24个
    # 4 有, 112个
    # 5
    # 6

    time.sleep(15)
    # linkArray = GenerateLink(5)
    # data_path = os.path.join(folder, 'grouplink_'+ str(len(linkArray)) +'.txt')
    # data_path_exist = os.path.join(folder, 'grouplink_exist_'+ str(len(linkArray)) +'.txt')
    # fileUtil = FileUtil()
    # # fileUtil.write_file(data_path, "{}\n".format(entryTemp.__dict__))
    # count = 0
    # for e in linkArray:
    #     link = "https://t.me/{}".format(e)
    #     fileUtil.write_file(data_path, "{}\n".format(link))
    #     print(link)
    #     entry = tgClient.parseGroupLink(link)
    #     if entry:
    #         print("==>>", entry)
    #         fileUtil.write_file(data_path_exist, "{},{}\n".format(link, entry.__dict__))
    #     # else:
    #     #     fileUtil.write_file(data_path, "\n")

    #     count += 1
    #     if count % 500 == 0:
    #         time.sleep(3)
        

    # fileUtil.write_file(data_path, "{} =======================\n\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))





    # group_entry = tgClient.parseGroupLink(GroupLink)
    # tgClient.get_group_participants(group_entity=group_entry)

    # result = tgClient.is_group_participant(group_entity=group_entry, entity=None)
    # print("result...", result)



