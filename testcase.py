from telethon.sync import TelegramClient
import os
import socks
import time
from pathlib import Path
from utils.file_util import FileUtil


basepath = os.path.abspath(__file__)
folder = os.path.dirname(basepath)

# def Path(path):
#     return folder+"/"+path

api_id="9458299"
api_hash="b0cba0c5ad2b5aa5925ab52afedc3f83"
proxy=(socks.SOCKS5, 'localhost', 51837)

session_path = Path("sessions")
print(session_path)
if not session_path.exists():
    session_path.mkdir()

def get_phone_number():
    return "8613950209512"
    # return "8613859549658"

phone_number = get_phone_number()
client = TelegramClient(f"sessions/{phone_number}", api_id, api_hash, proxy=proxy)


def get_verification_code():
    # return 46116

    fileUtil = FileUtil()
    return fileUtil.read_file_002(folder+"/"+"vcode.txt")


async def main():
    print("connect...")
    await client.connect()


    # print("get_verification_code...", get_verification_code())

    print("is_user_authorized...11")
    if not await client.is_user_authorized():
        print("send_code_request...11")
        await client.send_code_request(f"+{phone_number}")
        print("send_code_request...22")
        time.sleep(180)
        print("get_verification_code...22")
        verification_code = get_verification_code()
        print("verification_code...", verification_code)
        await client.sign_up(verification_code, "a", "bb")

    await client.disconnect()

    # time.sleep(5)
    # print("send_code_request...")
    # await client.send_code_request(f"+{phone_number}", force_sms=True)
    # verification_code = get_verification_code()
    # await client.sign_up(verification_code, names.get_first_name(), names.get_last_name())

    # await client.disconnect()


client.loop.run_until_complete(main())


