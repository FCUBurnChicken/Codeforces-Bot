import json
import requests
from collections import namedtuple

url = "https://codeforces.com/api"

class Codeforces_API():
    def __init__(self) -> None:
        pass

    async def get_problem_list(self):
        response = requests.get(url + '/problemset.problems')
        response = response.json()
        if not response:
            return False
        else:
            return response['result']['problems']
    
    async def classify_problems(self, problems, tag):
        new_problems  = []
        for problem in problems:
            if tag in problem['tags']:
                new_problems.append(problem)
        return new_problems

    async def get_user_problems(self, handle, count=None):
        url = f"https://codeforces.com/api/user.status?handle={handle}"
        if count:
            url += f"&from=1&count={count}"
        response = requests.get(url)
        response = response.json()
        if not response:
            return [False, "CF API Error"]
        if response['status'] != 'OK':
            return [False, response['comment']]
        try:
            data = []
            prev = []
            Problem = namedtuple('Problem', 'id index name rating, tag')
            for x in response['result']:
                y = x['problem']
                if 'rating' not in y or x['verdict'] != 'OK' or y['name'] in prev:
                    continue
                prev.append(y['name'])
                data.append(Problem(y['contestId'], y['index'], y['name'], y['rating'], y['tags']))
            return [True, data]
        except Exception as e:
            return [False, str(e)]