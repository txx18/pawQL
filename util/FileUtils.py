import os
import json


# 将结果写入文件
def writeFile(fileDir, file, data):
    if not os.path.exists(fileDir):
        os.makedirs(fileDir)
    with open(file, 'w', encoding="utf-8") as outfile:
        # json.dump(data, outfile)
        outfile.write(data)


def writeFileAppend(fileDir, file, data):
    if not os.path.exists(fileDir):
        os.makedirs(fileDir)
    with open(file, 'a', encoding="utf-8") as outfile:
        # json.dump(data, outfile)
        outfile.write(data)


def writeJsonFile(fileDir, file, data):
    if not os.path.exists(fileDir):
        os.makedirs(fileDir)
    with open(file, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False)
        # outfile.write(data)


# 读取json
def readJsonFile(filepath):
    with open(filepath, 'r', encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    writeJsonFile("..", "test.json", {"name": "唐轩"})