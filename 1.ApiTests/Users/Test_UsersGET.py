import pytest
import requests
import random
import string
from dotenv import load_dotenv
import os
load_dotenv()

API_USER = os.getenv('API_USER')
API_PASS = os.getenv('API_PASS')

def test_get_user200():
    
    Params = ["user_id", "user_name", "tariff_id", "msisdn", "balance", "registration_date", "payment_day", "minutes", ]

    url = "http://romashka.ru/api/v1.2/users"
    response = requests.get(url, auth=(API_USER, API_PASS))
    
    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}" 
    assert response.headers["Content-Type"] == "application/json; charset=UTF-8"
    
    userslist = response.json() 
    assert isinstance(userslist, list)
    assert len(userslist) > 0, "Список пользователей пуст"
    
    for user in userslist:
        for key in Params:
            assert key in user, f"Поле {key} отсутствует у пользователя {user}"

def test_get_user400():

    bad_header = {"Content-Type": "💀/💀💀"}
    url = "http://romashka.ru/api/v1.2/users"
    response = requests.get(url, auth=(API_USER, API_PASS), headers=bad_header)
    
    assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}" 

def test_get_user401():
    characters_for_generate = string.ascii_letters + string.digits + '!$%^'
    password = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 32)))
    username = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 10)))

    url = "http://romashka.ru/api/v1.2/users"
    response = requests.get(url, auth=(username, password))
    
    assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}"  

def test_get_user404():
    url = "http://romashka.ru/api/v1.2/useri"
    response = requests.get(url, auth=(API_USER, API_PASS))
    
    assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}" 