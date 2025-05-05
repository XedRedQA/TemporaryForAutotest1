import pytest
import requests
from sqlalchemy import create_engine
import pandas as pd
import random
import string
from dotenv import load_dotenv
import os
load_dotenv()

uid = os.getenv('DB_USER')
pwd = os.getenv('DB_PASSWORD')
API_USER = os.getenv('API_USER')
API_PASS = os.getenv('API_PASS')


@pytest.fixture
def user_select_bd():
    server = 'localhost'
    database = 'romashka'
    engine = create_engine(f'postgresql://{uid}:{pwd}@{server}:54320/{database}')
    sql = "SELECT user_id FROM users_saved ORDER BY RANDOM() LIMIT 1;"
    df = pd.read_sql_query(sql, engine)
    id = df.iloc[0]['user_id']
    return id

def test_get_user_id_tariff200(user_select_bd):

    url = f"http://romashka.ru/api/v1.2/users/{user_select_bd}/tariff"
    response = requests.get(url, auth=(API_USER, API_PASS))
    user_tariff = response.json() 
    
    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}" 
    assert response.headers["Content-Type"] == "application/json; charset=UTF-8"
    
    assert "tariff" in user_tariff, "Поле tariff не отобразилось"

def test_get_user_id_tariff400(user_select_bd):

    bad_header = {"Content-Type": "💀/💀💀"}
    url = f"http://romashka.ru/api/v1.2/users/{user_select_bd}/tariff"
    response = requests.get(url, auth=(API_USER, API_PASS), headers=bad_header)
    
    assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}" 

def test_get_user_id_tariff401(user_select_bd):

    characters_for_generate = string.ascii_letters + string.digits + '!$%^'
    password = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 32)))
    username = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 10)))

    url = f"http://romashka.ru/api/v1.2/users/{user_select_bd}/tariff"
    response = requests.get(url, auth=(username, password))
    
    assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}"  

def test_get_user_id_tariff404():
    bad_id = random.randint(1000000, 9999999)
    url = f"http://romashka.ru/api/v1.2/users/{bad_id}/tariff"
    response = requests.get(url, auth=(API_USER, API_PASS))
    
    assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}" 
