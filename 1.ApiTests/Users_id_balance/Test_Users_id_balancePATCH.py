import pytest
import requests
from sqlalchemy import create_engine
import pandas as pd
import random
import string


@pytest.fixture
def db_engine():
    uid = 'admin'
    pwd = 'admin'
    server = 'localhost'
    database = 'romashka'
    return create_engine(f'postgresql://{uid}:{pwd}@{server}:54320/{database}')


@pytest.fixture
def create_request(db_engine):
    sql = "SELECT user_id,balance FROM users_saved ORDER BY RANDOM() LIMIT 1;"
    df = pd.read_sql_query(sql, db_engine)
    return df

@pytest.fixture
def select_user_id_bd(create_request):
    id = create_request.iloc[0]['user_id']
    return id

@pytest.fixture
def select_user_balance_bd(create_request):
    us_balance = create_request.iloc[0]['balance']
    return us_balance

def check_changes_in_bd(db_engine, select_user_id_bd):
    sql = f"SELECT balance FROM users_saved WHERE user_id = {select_user_id_bd}"
    df = pd.read_sql_query(sql, db_engine)
    user_data = df.iloc[0]
    return user_data

def test_patch_user_id_balance200(select_user_id_bd,select_user_balance_bd,db_engine):

    payload_new_balance = {
        "balance": random.randint(10, 300)
    }

    url = f"http://romashka.ru/api/v1.2/users/{select_user_id_bd}/balance"
    response = requests.patch(url, auth=('admin', 'admin'), json=payload_new_balance)

    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}" 
    assert response.headers["Content-Type"] == "application/json; charset=UTF-8"
    
    user_balance = response.json()
    assert "balance" in user_balance, "Баланс не отобразился"
    
    new_balance_for_check = check_changes_in_bd(db_engine, select_user_id_bd)
    assert select_user_balance_bd != new_balance_for_check['balance'], "Баланс не изменен, ожидалось, что имя изменится"

def test_patch_user_id_zero_balance200(select_user_id_bd,select_user_balance_bd,db_engine):

    payload_new_balance = {
        "balance": 0
    }

    url = f"http://romashka.ru/api/v1.2/users/{select_user_id_bd}/balance"
    response = requests.patch(url, auth=('admin', 'admin'), json=payload_new_balance)

    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}" 
    assert response.headers["Content-Type"] == "application/json; charset=UTF-8"
    
    user_balance = response.json()
    assert "balance" in user_balance, "Баланс не отобразился"
    
    new_balance_for_check = check_changes_in_bd(db_engine, select_user_id_bd)
    assert select_user_balance_bd != new_balance_for_check['balance'], "Баланс не изменен, ожидалось, что имя изменится"

def test_patch_user_id_negative_balance200(select_user_id_bd,select_user_balance_bd,db_engine):

    payload_new_balance = {
        "balance": random.randint(-300, -10)
    }

    url = f"http://romashka.ru/api/v1.2/users/{select_user_id_bd}/balance"
    response = requests.patch(url, auth=('admin', 'admin'), json=payload_new_balance)

    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}" 
    assert response.headers["Content-Type"] == "application/json; charset=UTF-8"
    
    user_balance = response.json()
    assert "balance" in user_balance, "Баланс не отобразился"
    
    new_balance_for_check = check_changes_in_bd(db_engine, select_user_id_bd)
    assert select_user_balance_bd != new_balance_for_check['balance'], "Баланс не изменен, ожидалось, что имя изменится"

def test_patch_user_id_balance400(select_user_id_bd, select_user_balance_bd, db_engine):

    payload_new_balance = {
        "balance": 'abc'
    }
    url = f"http://romashka.ru/api/v1.2/users/{select_user_id_bd}/balance"
    response = requests.patch(url, auth=('admin', 'admin'), json=payload_new_balance)

    assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}" 
    assert response.headers["Content-Type"] == "application/json; charset=UTF-8"
    
    user_balance = response.json()
    assert "error" in user_balance
    assert user_balance["error"] == "Некорректный тип данных для поля balance"

    current = check_changes_in_bd(db_engine, select_user_id_bd)
    assert current["balance"] == select_user_balance_bd, "Баланс изменился, хотя не должен был"

def test_patch_user_id_balance401(select_user_id_bd):

    characters_for_generate = string.ascii_letters + string.digits + '!$%^'
    password = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 32)))
    username = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 10)))

    url = f"http://romashka.ru/api/v1.2/users/{select_user_id_bd}/balance"
    response = requests.patch(url, auth=(username, password))
    
    assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}"  

def test_patch_user_id_balance404():
    bad_id = random.randint(1000000, 9999999)
    url = f"http://romashka.ru/api/v1.2/users/{bad_id}/balance"
    response = requests.patch(url, auth=('admin', 'admin'))
    
    assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}" 
