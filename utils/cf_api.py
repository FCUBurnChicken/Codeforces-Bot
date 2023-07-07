import json
import requests

url = "https://codeforces.com/api"

class Codeforces_API():
    def __init__(self) -> None:
        pass

    async def get_problem_list(self):
        response = requests.get(url + '/problemset.problems').json()
        if not response:
            return False
        else:
            return response['result']['problems']