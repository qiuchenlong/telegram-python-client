
tkinter 打包成exe可执行文件
pyinstaller -F -w gui_main_001.py



```shell
pip3 install py2app

py2applet --make-setup gui_main.py

python3 setup.py py2app
python3 setup.py py2app --packages=telethon,PIL
python3 setup.py py2app --packages=PIL


pip3 install setuptools==44.0.0



开发环境
python3 -m venv tutorial-env

启用开发环境
source tutorial-env/bin/activate

安装telethon
pip3 install --upgrade telethon

pip3 install PySocks


生成requirements.txt文件
pip3 freeze > requirements.txt

安装依赖包
pip install -r requirements.txt











```

https://www.youtube.com/watch?v=84UHgvfCcec

telegram 需求

https://www.youtube.com/watch?v=5fm4UYBFnQs

1、
简体汉化
tg://setlanguage?lang=jiantizi

繁体汉化
tg://setlanguage?lang=hongkong
tg://setlanguage?lang=zh-hant-beta

2、
搜索群组机器人
简体中文
https://t.me/SuperIndexCNBot
https://t.me/zh_secretary_bot
https://t.me/So1234Bot
https://t.me/zh_groups_bot xxx

繁体中文
https://t.me/TG_index_bot

导航网站
简体中文
https://github.com/itgoyo/TelegramGroup

繁体中文
https://telegramgroup.com.hk/
https://tgtw.cc/index.php
https://www.telegram.url.tw/
