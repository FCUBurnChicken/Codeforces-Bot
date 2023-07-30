import json
import requests
from collections import namedtuple

url = "https://codeforces.com/api"

class Codeforces_API():
    def __init__(self) -> None:
        pass

    def get_user_info(self, handle):
        response = requests.get(url + "/user.info?handles=" + handle)
        response = json.loads(response.text)
        return {
            'handle': handle,
            'rating': response['result'][0]['rating'],
            'maxRating': response['result'][0]['maxRating'],
            'rank': response['result'][0]['rank'],
            'maxRank': response['result'][0]['maxRank'],
            'titlePhoto': response['result'][0]['titlePhoto']
        }

    def get_AC_problem(self, handle):
        response = requests.get(url + "/user.status?handle=" + handle)
        response = json.loads(response.text)
        problem = []
        problem_name = []
        for i in range(len(response['result'])):
            if response['result'][i]['verdict'] == 'OK' and hasattr(response['result'][i]['problem'], 'rating') and response['result'][i]['problem']['name'] not in problem_name:
                obj = {
                    'id': response['result'][i]['problem']['contestId'],
                    'index': response['result'][i]['problem']['index'],
                    'name': response['result'][i]['problem']['name'],
                    'rating': response['result'][i]['problem']['rating'],
                    'tags': response['result'][i]['problem']['tags']
                }
                problem_name.append(response['result'][i]['problem']['name'])
                problem.append(obj)
        return problem
    
    async def get_problem_list(self):
        response = requests.get(url + '/problemset.problems')
        response = json.loads(response.text)
        if not response:
            return False
        else:
            return response['result']['problems']