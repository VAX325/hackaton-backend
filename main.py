import requests
import json
import ast

def main():
    r = requests.get("http://127.0.0.1:8000/users",
    json={
        "username":"test",
        "password":"password",
        "email":"test@mail.com",

    })


main()
