import pytest
import requests
from sqlalchemy import create_engine
import pandas as pd
import random
import string


@pytest.fixture
def user_select_bd():
    uid = 'admin'
    pwd = 'admin'
    server = 'localhost'
    database = 'romashka'
    engine = create_engine(f'postgresql://{uid}:{pwd}@{server}:54320/{database}')
    sql = "SELECT user_id FROM users_saved ORDER BY RANDOM() LIMIT 1;"
    df = pd.read_sql_query(sql, engine)
    id = df.iloc[0]['user_id']
    return id

def test_get_user_id_balance200(user_select_bd):

    url = f"http://romashka.ru/api/v1.2/users/{user_select_bd}/balance"
    response = requests.get(url, auth=('admin', 'admin'))
    user_balance = response.json() 
    
    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}" 
    assert response.headers["Content-Type"] == "application/json; charset=UTF-8"
    
    assert "balance" in user_balance, "Баланс не отобразился"

def test_get_user_id_balance400(user_select_bd):

    bad_header = {"Content-Type": "💀/💀💀"}
    url = f"http://romashka.ru/api/v1.2/users/{user_select_bd}/balance"
    response = requests.get(url, auth=('admin', 'admin'), headers=bad_header)
    
    assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}" 

def test_get_user_id_balance401(user_select_bd):

    characters_for_generate = string.ascii_letters + string.digits + '!$%^'
    password = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 32)))
    username = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 10)))

    url = f"http://romashka.ru/api/v1.2/users/{user_select_bd}/balance"
    response = requests.get(url, auth=(username, password))
    
    assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}"  

def test_get_user_id_balance404():
    bad_id = random.randint(1000000, 9999999)
    url = f"http://romashka.ru/api/v1.2/users/{bad_id}/balance"
    response = requests.get(url, auth=('admin', 'admin'))
    
    assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}" 
