import os




class FileUtil:

    def __init__(self):
        pass

    def read_file(self, file_path):
        with open(file_path, "r+", encoding="utf-8") as f:
            text = f.read()
            print(text)


    def read_file_002(self, file_path):
        result = ""
        try:
            file = open(file_path, "r+")
            for line in file:  # 遍历file文件
                result = result + line
            file.close()  # 关闭文件
        except Exception as e:
            print(e)
        return result


    def write_file(self, file_path, text):
        try:
            with open(file_path, "a+", encoding="utf-8") as fw:
                fw.write(text)
        except Exception as e:
            print(e)

    def write_file_001(self, file_path, text):
        try:
            with open(file_path, "w+", encoding="utf-8") as fw:
                fw.write(text)
        except Exception as e:
            print(e)