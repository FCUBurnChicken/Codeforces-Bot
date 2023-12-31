import json
import requests

url = "https://codeforces.com/api"

class Codeforces_API():
    def __init__(self) -> None:
        pass

    async def get_user_info(self, handle):
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

    async def get_AC_problem(self, handle):
        response = requests.get(url + "/user.status?handle=" + handle)
        response = json.loads(response.text)
        problem = []
        problem_name = []
        for i in range(len(response['result'])):
            if 'rating' in response['result'][i]['problem'] :
                obj = {
                    'id': response['result'][i]['problem']['contestId'],
                    'index': response['result'][i]['problem']['index'],
                    'name': response['result'][i]['problem']['name'],
                    'rating': response['result'][i]['problem']['rating'],
                    'tags': ','.join(response['result'][i]['problem']['tags'])
                }
                if response['result'][i]['verdict'] == 'OK' and response['result'][i]['problem']['name'] not in problem_name and obj not in problem:
                    problem_name.append(response['result'][i]['problem']['name'])
                    problem.append([obj['id'], obj['index'], obj['name'], obj['rating'], obj['tags']])
        return problem
    
    async def get_problem_list(self):
        response = requests.get(url + '/problemset.problems')
        response = json.loads(response.text)
        if not response:
            return False
        else:
            return response['result']['problems']
    
    
