import init
import queries
import utils
import requests
from datetime import datetime
import os
import numpy as np
import matplotlib.pyplot as plt

def query_request(query, owner, repo, type, last_end_cursor=None):
    """封装后的 GraphQL 请求"""
    retry_flag = False
    token = "302c872edc4a37e563de72986e09749b12196c88"
    headers = {"Authorization": "Bearer %s" % token}
    if last_end_cursor == None:
        query_ = query % (owner, repo, type)
    else:
        query_ = query % (owner, repo, type, last_end_cursor)

    response = requests.post(
        'https://api.github.com/graphql', json={'query': query_}, headers=headers, stream=True)


    if response.status_code == 200:
        try:
            return response.json()
        except:
            print("return error and retry")
            r1 = query_request(query, owner, repo, type, last_end_cursor)
            return r1
    else:
        print( str(response.status_code) + " retry")
        r1 = query_request(query, owner, repo, type, last_end_cursor)
        return r1


def request_graphQL(owner, repo, type):
    """
    :param owner: repository owner
    :param repo:  repository name
    :param type:  pullRequests or issues
    :return:  response of pr or issues
    """
    count = 0
    output_response_file = init.local_data_filepath+owner+"/"+repo+"/response_"+type+".json"
    if os.path.isfile(output_response_file):
        r = utils.read_json_from_file(output_response_file)
    else:
        r = query_request(queries.first_page, owner, repo, type)
    if not r['data']['repository'][type]['pageInfo']['hasNextPage']:
        return r
    while True:
        count += 1
        print(count,datetime.now(),r['data']['repository'][type]['totalCount'],len(r['data']['repository'][type]['nodes']))
        if count % 1 == 0:
            utils.save_json_to_file(output_response_file, r)
        else:
            pass
        earliest_pr_cursor = r['data']['repository'][type]['edges'][-1]['cursor']
        r2 = query_request(queries.other_page, owner, repo, type, earliest_pr_cursor)
        r['data']['repository'][type]['pageInfo'] = r2['data']['repository'][type]['pageInfo']
        r['data']['repository'][type]['edges']+= r2['data']['repository'][type]['edges']
        r['data']['repository'][type]['nodes'] += r2['data']['repository'][type]['nodes']
        if not r['data']['repository'][type]['pageInfo']['hasNextPage']:
            utils.save_json_to_file(output_response_file,r)
            break
    return r



def extract_link_type(response,type,filepath=None):
    """

    :param response:
    :param type:
    :param filepath: input ”‘init.local_data_filepath+owner+’/’+repo+‘/’“ when need to save to file
    :return:
    """
    nodes = response['data']['repository'][type]['nodes']
    pr_pr = []
    pr_iss = []
    iss_pr = []
    iss_iss = []
    for item in nodes:
        node1_type = type
        node1_number = item['number']
        node1_time = item['createdAt']
        for node in item['timelineItems']['nodes']:
            if node:
                # 判断另一个node是pr还是issues
                if "id" in node['source'].keys():
                    node2_type = "pullRequests"
                else:
                    node2_type = "issues"

                node2_number = node["source"]['number']
                node2_ref_date = node["referencedAt"]

                link = {}
                link['target'] = node1_number
                link['source'] = node2_number
                type = node1_type
                target_type = node2_type
                link['timeInterval'] = abs(datetime.strptime(node1_time, "%Y-%m-%dT%H:%M:%SZ")
                                           .__sub__(datetime.strptime(node2_ref_date, "%Y-%m-%dT%H:%M:%SZ")).days)
                if type == "pullRequests" and target_type == 'pullRequests':
                    pr_pr.append(link)
                if type == "issues" and target_type == 'pullRequests':
                    iss_pr.append(link)
                if type == "pullRequests" and target_type == 'issues':
                    pr_iss.append(link)
                if type == "issues" and target_type == 'issues':
                    iss_iss.append(link)

    if type == "pullRequests":
        if filepath:
            utils.save_json_to_file(filepath+"pr_pr.json",pr_pr)
            utils.save_json_to_file(filepath+"pr_iss.json",pr_iss)
        else:
            pass
        return pr_pr, pr_iss
    elif type == "issues":
        if filepath:
            utils.save_json_to_file(filepath + "iss_pr.json", iss_pr)
            utils.save_json_to_file(filepath + "iss_iss.json", iss_iss)
        else:
            pass
        return iss_pr, iss_iss

def plot_link_classes(pr_pr,pr_iss,iss_pr,iss_iss):
    y1 = np.array([len(pr_pr),len(pr_iss)])
    y2 = np.array([len(iss_pr),len(iss_iss)])
    x = ["pullRequests", "issues"]
    plt.bar(x, y1,color='cornflowerblue',label='link to pullRequests')
    plt.bar(x, y2,color='lightslategray',label='link to issues')
    plt.legend()
    plt.show()

def plot_link_mode(dataset):
    y1 = np.array([len(dataset[0]),len(dataset[2]),len(dataset[4]),len(dataset[6])])
    y2 = np.array([len(dataset[1]),len(dataset[3]),len(dataset[5]),len(dataset[7])])
    x = ["pr2pr","pr2iss", "iss2pr", "iss1iss"]
    plt.bar(x, y1,color='cornflowerblue',label='1 to 1')
    plt.bar(x, y2,color='lightslategray',label='1 to N')
    plt.legend()
    plt.show()

def extract_link_mode(linkset,save_file_path):
    source_list = []
    target_list = []
    for link in linkset:
        source = link['source']
        target = []
        if source not in source_list:
            source_list.append(source)
            for sub_iter in linkset:
                if sub_iter['source'] == source:
                    target.append(sub_iter['target'])
                else:
                    pass
            target_list.append(target)
        else:
            pass

    link_1_1 = []
    link_1_N = []
    for source,target in zip(source_list,target_list):
        if len(target) == 1:
            link_1_1.append({'source':source,'target':target})
        else:
            link_1_N.append({'source': source, 'target': target})

    utils.save_json_to_file(save_file_path+"link_1_1.json",link_1_1)
    utils.save_json_to_file(save_file_path+"link_1_N.json",link_1_N)


    return link_1_1,link_1_N

def work_on_repos():
    with open(init.repo_list_file,'r') as f:
        repo_list = f.readlines()
        repos_to_get_info = []
        for item in repo_list:
            repos_to_get_info.append([item.strip().split("/")[0],item.strip().split("/")[1]])

    for o_r in repos_to_get_info:
        owner = o_r[0]
        repo = o_r[1]
        print("--------------------handle "+owner+"/"+repo+"---------------------------")

        response_pr = request_graphQL(owner, repo, 'pullRequests')
        reponse_iss = request_graphQL(owner,repo,'issues')

        pr_pr, pr_iss = extract_link_type(response_pr,"pullRequests",init.local_data_filepath+owner+"/"+repo+"/")
        iss_pr, iss_iss = extract_link_type(reponse_iss,"issues",init.local_data_filepath+owner+"/"+repo+"/")
        plot_link_classes(pr_pr, pr_iss,iss_pr, iss_iss)


        pr_pr_1_1,pr_pr_1_N = extract_link_mode(pr_pr,init.local_data_filepath+owner+"/"+repo+"/pr_pr")
        pr_iss_1_1,pr_iss_1_N = extract_link_mode(pr_iss,init.local_data_filepath+owner+"/"+repo+"/pr_iss")
        iss_pr_1_1,iss_pr_1_N = extract_link_mode(iss_pr,init.local_data_filepath+owner+"/"+repo+"/iss_pr")
        iss_iss_1_1,iss_iss_1_N = extract_link_mode(iss_iss,init.local_data_filepath+owner+"/"+repo+"/iss_iss")

        link_mode = [pr_pr_1_1,pr_pr_1_N,pr_iss_1_1,pr_iss_1_N,iss_pr_1_1,iss_pr_1_N,iss_iss_1_1,iss_iss_1_N]
        plot_link_mode(link_mode)


if __name__ == '__main__':
    work_on_repos()