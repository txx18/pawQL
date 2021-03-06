import os
import json

def save_json_to_file(file_path,json_data):
    folderpath = file_path.replace("/"+file_path.split("/")[-1],'')
    folder = os.path.exists(folderpath)
    if not folder:
        os.makedirs(folderpath)
    f = open(file_path, 'w')
    content = json.dumps(json_data)
    f.write(content)
    f.close()

def read_json_from_file(file_path):
    f = open(file_path, 'r')
    content = json.loads(f.readline())
    f.close()
    return content