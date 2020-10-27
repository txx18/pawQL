import random


def read_token():
    token_file = open("../config/token_list.txt", 'r')
    tokens = token_file.readlines()
    return tokens


def rest_search_repos(q, sort, order):
    """

    :param q: tetris+language:assembly
    :param sort: stars
    :param order: desc
    :return:
    """
    tokens = read_token()
    token = tokens[random.randint(0, 8)].strip()
    headers = {"Authorization": "token %s" % token,
               "Accept": "application/vnd.github.mercy-preview+json"}
    url = "https://api.github.com/search/repositories?q=%s&sort=%s&order=%s" % (q, sort, order)

