import os
import random
import time

import requests

from knowledge_graph import queries
from util.FileUtils import writeJsonFile


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
        pageNo = 2
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
                # 测试API限制
                print(headers)
                print("X-RateLimit-Limit: " + str(response.headers.get("X-RateLimit-Limit")))
                print("X-RateLimit-Remaining: " + str(response.headers.get("X-RateLimit-Remaining")))
                print('X-RateLimit-Reset: ' + str(response.headers.get("X-RateLimit-Reset")))
                # 有时候被拒绝请求会返回message，抛出异常，请求重试
                print("response.status_code: " + str(response.status_code))
                if response.status_code != 200:
                    raise Exception("request error with search " + q)
                # 写入文件
                out_dir = os.path.join(os.getcwd(), "..", "tx_data", "topic_repo", one_topic)
                writeJsonFile(out_dir, os.path.join(out_dir, "page" + str(pageNo) + ".json"), response_json)
                # 如果有下一页，循环
                while response.links.__contains__("next"):
                    pageNo += 1
                    continue
            except Exception as e:
                print(e)
                print("error at page" + str(pageNo) + "...retrying...")
                continue
        print("search finished")


class GithubAPIv4(object):

    def __init__(self):
        self.api = "https://api.github.com/graphql"

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
                # TODO 内部有4个字段可能有多页dependencyGraphManifests（嵌套dependencies），languages, repositoryTopics，但是一般都不会超过100个，所以这里统统不考虑了
                print("response.status_code: " + str(response.status_code))
                if response.status_code != 200:
                    raise Exception("request error at: " + owner + "/" + repoName)
                # 写入文件
                out_dir = os.path.join(os.getcwd(), "..", "tx_data", "repo")
                writeJsonFile(out_dir, os.path.join(out_dir, owner + "_" + repoName + ".json"), response_json)
                break
            except Exception as e:
                print(e)
                print("exception at: " + owner + "/" + repoName)
                continue
        print("get finished")


if __name__ == "__main__":
    v3 = GithubAPIv3()
    v3.search_repos("topic:deep-learning", "stars", "desc", 100)

    # v4 = GithubAPIv4()
    # v4.get_repo("pytorch/pytorch")
