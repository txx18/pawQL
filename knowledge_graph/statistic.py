import os

from util.FileUtils import read_json_file


def get_data_one_topic_repo(topic_path):
    res = set()
    for page_index, page_file in enumerate(os.listdir(topic_path)):
        json = read_json_file(os.path.join(topic_path, page_file))
        # 预处理，忽略fork的仓库 private仓库
        for item in json["items"]:
            exclude = item["size"] == 0 or item["fork"] or item["private"]
            if exclude is True:
                continue
            res.add(item["full_name"])
    return res


def get_data_topic_repo_set(topic_repo_path):
    res = set()
    for topic_index, topic_dir in enumerate(os.listdir(topic_repo_path)):
        for page_index, page_file in enumerate(os.listdir(os.path.join(topic_repo_path, topic_dir))):
            json = read_json_file(os.path.join(topic_repo_path, topic_dir, page_file))
            # 预处理，忽略fork的仓库 private仓库
            for item in json["items"]:
                exclude = item["size"] == 0 or item["fork"] or item["private"]
                if exclude is True:
                    continue
                res.add(item["full_name"])
    return res


def get_data_repo_set(repo_path):
    res = set()
    for repo_index, repo_file in enumerate(os.listdir(repo_path)):
        owner, repoName = os.path.splitext(repo_file)[0].split("-$-")
        res.add(owner + "/" + repoName)
    return res


if __name__ == "__main__":
    # topic_repo_set = get_data_topic_repo_set(os.path.join(os.getcwd(), "..", "tx_data", "topic_repo"))
    data_repo_set = get_data_repo_set(os.path.join(os.getcwd(), "..", "tx_data", "repo"))
    print("finish")
