import os
import json


def writeFile(fileDir, file, data):
    """
    python to file
    :param fileDir:
    :param file:
    :param data:
    :return:
    """
    if not os.path.exists(fileDir):
        os.makedirs(fileDir)
    with open(file, 'w', encoding="utf-8") as outfile:
        # json.dump(data, outfile)
        outfile.write(data)


def writeFileAppend(fileDir, file, data):
    """
    python to file append
    :param fileDir:
    :param file:
    :param data:
    :return:
    """
    if not os.path.exists(fileDir):
        os.makedirs(fileDir)
    with open(file, 'a', encoding="utf-8") as outfile:
        # json.dump(data, outfile)
        outfile.write(data)


def write_json_file(fileDir, file, data):
    """
    python to json file
    :param fileDir:
    :param file:
    :param data:
    :return:
    """
    if not os.path.exists(fileDir):
        os.makedirs(fileDir)
    with open(file, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False)
        # outfile.write(data)


def read_json_file(filepath):
    """
    json file to python
    :param filepath:
    :return:
    """
    with open(filepath, 'r', encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    write_json_file("..", "test.json", {"name": "唐轩"})
