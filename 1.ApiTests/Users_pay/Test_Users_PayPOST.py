import pytest
import requests
import random
from names_generator import generate_name
import string
from sqlalchemy import create_engine
import pandas as pd

@pytest.fixture(scope="module")
def db_engine():
    uid = 'admin'
    pwd = 'admin'
    server = 'localhost'
    database = 'romashka'
    return create_engine(f'postgresql://{uid}:{pwd}@{server}:54320/{database}')

@pytest.fixture
def create_request(db_engine):
    sql = "SELECT msisdn,balance FROM users_saved ORDER BY RANDOM() LIMIT 1;"
    df = pd.read_sql_query(sql, db_engine)
    return df

@pytest.fixture
def select_user_msisdn_bd(create_request):
    number = create_request.iloc[0]['msisdn']
    return number

@pytest.fixture
def select_user_balance_bd(create_request):
    us_balance = create_request.iloc[0]['balance']
    return us_balance

def check_changes_in_bd(db_engine, select_user_msisdn_bd):
    sql = f"SELECT balance FROM users_saved WHERE msisdn = '{select_user_msisdn_bd}'"
    df = pd.read_sql_query(sql, db_engine)
    return df.iloc[0]['balance']

def test_post_positive_balance_200(db_engine, select_user_msisdn_bd, select_user_balance_bd):
    payload_new_balance = {
        "balance": random.randint(10, 300)
    }

    url = "http://romashka.ru/api/v1.2/users/pay"
    response = requests.post(url, auth=(select_user_msisdn_bd, ''), json=payload_new_balance)

    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}" 
    assert response.headers["Content-Type"] == "application/json; charset=UTF-8"
    
    user_balance = response.json()
    assert "balance" in user_balance, "Баланс не отобразился"
    
    new_balance_for_check = check_changes_in_bd(db_engine, select_user_msisdn_bd)
    assert new_balance_for_check != select_user_balance_bd, "Баланс не изменен, ожидалось, что баланс изменится"


def test_post_zero_balance_400(db_engine, select_user_msisdn_bd, select_user_balance_bd):
    payload_new_balance = {
        "balance":0
    }

    url = "http://romashka.ru/api/v1.2/users/pay"
    response = requests.post(url, auth=(select_user_msisdn_bd, ''), json=payload_new_balance)

    assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}" 
    assert response.headers["Content-Type"] == "application/json; charset=UTF-8"
    
    user_balance = response.json()
    assert "balance" in user_balance, "Баланс не отобразился"
    
    new_balance_for_check = check_changes_in_bd(db_engine, select_user_msisdn_bd)
    assert new_balance_for_check == select_user_balance_bd, "Баланс изменился, ожидалось, что баланс не изменится"

def test_post_negative_balance_400(db_engine, select_user_msisdn_bd, select_user_balance_bd):
    payload_new_balance = {
        "balance": random.randint(-300, -10)
    }

    url = "http://romashka.ru/api/v1.2/users/pay"
    response = requests.post(url, auth=(select_user_msisdn_bd, ''), json=payload_new_balance)

    assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}" 
    assert response.headers["Content-Type"] == "application/json; charset=UTF-8"
    
    user_balance = response.json()
    assert "balance" in user_balance, "Баланс не отобразился"
    
    new_balance_for_check = check_changes_in_bd(db_engine, select_user_msisdn_bd)
    assert new_balance_for_check == select_user_balance_bd, "Баланс изменился, ожидалось, что баланс не изменится"


def test_post_create_user401(db_engine):
    characters_for_generate = string.ascii_letters + string.digits + '!$%^'
    username = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 10)))
    payload_new_balance = {
        "balance": random.randint(10, 200)
    }

    url = "http://romashka.ru/api/v1.2/users/pay"
    response = requests.post(url, auth=(username, ''), json=payload_new_balance)
    assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}" 
    

def test_post_create_user404(db_engine):
    
    msisdn = '7999' + str(random.randint(1000000, 9999999)),
    
    payload_new_balance = {
        "balance": random.randint(10, 200)
    }

    url = "http://romashka.ru/api/v1.2/users/pay"
    response = requests.post(url, auth=(msisdn, ''), json=payload_new_balance)
    assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}" 
