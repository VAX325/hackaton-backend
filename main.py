import random
import requests

def main():
    r = requests.post("http://127.0.0.1:8000/api/v1/users/signin",json={
        "username": "user",
        "pass": "pass"
    })
    print(r.request.body)


