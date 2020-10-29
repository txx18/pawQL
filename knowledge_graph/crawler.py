import os
import random
import time

import requests

from knowledge_graph import queries
from knowledge_graph.statistic import get_data_repo_set, get_data_topic_repo_set
from util.FileUtils import write_json_file


def read_token():
    token_file = open("../config/token_list.txt", 'r')
    tokens = token_file.readlines()
    return tokens


def get_topic_repos():
    """
    从topic_repo文件夹的
    :return:
    """
    pass


class GithubAPIv3(object):

    def __init__(self):
        self.api = "https://api.github.com/"

    def search_repos(self, q, sort, order, per_page):
        """
        根据系统关键字和用户自定义关键字搜索特定数据
        :param q: eg. tetris+language:assembly q=topic:ruby+topic:rails+language:assembly
        :param sort: eg. stars
        :param order: eg. desc
        :return:
        """
        one_topic = q.split(":")[1]
        print("begin to search: " + q)
        pageNo = 1
        while True:
            print("crawling page " + str(pageNo) + "...")
            tokens = read_token()
            token = tokens[random.randint(0, len(tokens) - 1)].strip()
            headers = {"Authorization": "token %s" % token,
                       "Accept": "application/vnd.github.mercy-preview+json"}
            url = self.api + "search/repositories?q=%s&sort=%s&order=%s&page=%s&per_page=%s" % (q, sort, order, pageNo, per_page)
            try:
                # 获取第pageNo页
                response = requests.get(url=url, headers=headers)
                response_json = response.json()
                # 有时候被拒绝请求会返回message，抛出异常，请求重试
                print("response.status_code: " + str(response.status_code))
                if response.status_code != 200:
                    raise Exception("request error with search " + q)
                # 测试API限制
                print(headers)
                print("X-RateLimit-Limit: " + str(response.headers.get("X-RateLimit-Limit")))
                print("X-RateLimit-Remaining: " + str(response.headers.get("X-RateLimit-Remaining")))
                print('X-RateLimit-Reset: ' + str(response.headers.get("X-RateLimit-Reset")))
                # 写入文件
                out_dir = os.path.join(os.getcwd(), "..", "tx_data", "topic_repo", one_topic)
                write_json_file(out_dir, os.path.join(out_dir, "page" + str(pageNo) + ".json"), response_json)
                print("write to file: " + str(os.path.join(out_dir, "page" + str(pageNo) + ".json")))
                # 如果有下一页，循环
                if response.links.__contains__("next"):
                    pageNo += 1
                else:
                    break
            except Exception as e:
                print(e)
                print("error at page" + str(pageNo) + "...retrying...")
                continue
        print("search finished")


class GithubAPIv4(object):

    def __init__(self):
        self.api = "https://api.github.com/graphql"

    def get_repo_batch(self):
        # 扫描topic需要爬取的仓库
        data_topic_repo_set = get_data_topic_repo_set(os.path.join(os.getcwd(), "..", "tx_data", "topic_repo"))
        # 扫描已有的仓库数据
        data_repo_set = get_data_repo_set(os.path.join(os.getcwd(), "..", "tx_data", "repo"))
        payload_repo_set = data_topic_repo_set - data_repo_set
        for repo in payload_repo_set:
            self.get_repo(repo)
        print("get repo batch finished")

    def get_repo(self, repo_full_name):
        """
        query one ropo info
        :param owner:
        :param repoName:
        :return:
        """
        owner, repoName = repo_full_name.split("/")
        print("begin to get repo: " + owner + "/" + repoName)
        query = queries.repos_query % (owner, repoName)
        # manifest_pageNo = 1
        # dependency_pageNo = 1
        # language_pageNo = 1
        # topic_pageNo = 1
        while True:
            tokens = read_token()
            token = tokens[random.randint(0, len(tokens) - 1)].strip()
            headers = {"Authorization": "Bearer %s" % token,
                       "Accept": "application/vnd.github.hawkgirl-preview+json"}
            try:
                response = requests.post(url=self.api, headers=headers, json={"query": query})
                response_json = response.json()
                # 过滤仓库
                exclude = self.filter_repo(response_json)
                if exclude is True:
                    continue
                print("response.status_code: " + str(response.status_code))
                if response.status_code != 200:
                    raise Exception("request error at: " + owner + "/" + repoName)
                # TODO 内部有4个字段可能有多页dependencyGraphManifests（嵌套dependencies），languages, repositoryTopics，但是一般都不会超过100个，所以这里统统不考虑了

                # 写入文件
                out_dir = os.path.join(os.getcwd(), "..", "tx_data", "repo")
                write_json_file(out_dir, os.path.join(out_dir, owner + "-$-" + repoName + ".json"), response_json)
                print("write to file: " + str(os.path.join(out_dir, owner + "-$-" + repoName + ".json")))
                break
            except Exception as e:
                print(e)
                print("exception at: " + owner + "/" + repoName)
                continue

    def list_relate_topics(self, topic):
        while True:
            tokens = read_token()
            token = tokens[random.randint(0, len(tokens) - 1)].strip()
            headers = {"Authorization": "Bearer %s" % token}
            query = queries.topic_query % topic
            try:
                response = requests.post(url=self.api, headers=headers, json={"query": query})
                response_json = response.json()
                print("response.status_code: " + str(response.status_code))
                if response.status_code != 200:
                    raise Exception("request error: " + topic)
                # 写入文件
                out_dir = os.path.join(os.getcwd(), "..", "tx_data", "topic")
                write_json_file(out_dir, os.path.join(out_dir, topic + ".json"), response_json)
                break
            except Exception as e:
                print(e)
                print("exception at: " + topic)
                continue
        print("get finished")

    def filter_repo(self, response_json):
        repo = response_json["data"]["repository"]
        exclude = repo["isEmpty"] or repo["isFork"] or repo["isLocked"] or repo["isPrivate"]
        return exclude


if __name__ == "__main__":
    v3 = GithubAPIv3()
    # for topic in ["rnn", "lstm", "recurrent-neural-networks", "recurrent-neural-network", "gru",
    #               "cnn", "convolutional-neural-network", "convolutional-neural-networks",
    #               "gradient-descent", "auto-encoder", "convolutional-autoencoders", "convolutional-networks",
    #               "gan", "logistic-regression", "meta-learning", "shot-learning", "maml",
    #               "nlp", "natural-language-processing", "sentiment-analysis", "nltk", "spacy",
    #               "transfer-learning", "classifier", "unsupervised-learning", "supervised-learning",
    #               "semi-supervised-learning", "clustering-algorithms", "kmeans-clustering", "clustering",
    #               "word-embedding"]:
    #     v3.search_repos("topic:" + topic, "stars", "desc", 100)

    v4 = GithubAPIv4()
    # v4.get_repo("pytorch/pytorch")
    # v4.list_relate_topics("semi-supervised-learning")

    v4.get_repo_batch()
    print("finished")
