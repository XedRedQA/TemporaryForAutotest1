import pytest
import requests
from sqlalchemy import create_engine
import pandas as pd
import random
import string
from names_generator import generate_name
from dotenv import load_dotenv
import os
load_dotenv()

uid = os.getenv('DB_USER')
pwd = os.getenv('DB_PASSWORD')
API_USER = os.getenv('API_USER')
API_PASS = os.getenv('API_PASS')


@pytest.fixture(scope="module")
def db_engine():
    server = 'localhost'
    database = 'romashka'
    return create_engine(f'postgresql://{uid}:{pwd}@{server}:54320/{database}')

def generator():
    return {
        "user_name": generate_name(style='capital'),
        "tariff_id": random.randint(11, 12),
        "msisdn": '7999' + str(random.randint(1000000, 9999999)),
        "balance": random.randint(100, 500)
    }

def check_new_user_in_bd(db_engine, msisdn):
    sql = f"SELECT user_id,user_name,tariff_id, msisdn,balance FROM users_saved WHERE msisdn = {msisdn};"
    df = pd.read_sql_query(sql, db_engine)
    return df if not df.empty else None

def test_post_create_user200(db_engine):
    user_data = generator()
    url = "http://romashka.ru/api/v1.2/users"

    response = requests.post(url, auth=(API_USER, API_PASS), json=user_data)
    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}" 
    assert response.headers["Content-Type"] == "application/json; charset=UTF-8"
    
    user_from_db = check_new_user_in_bd(db_engine, user_data["msisdn"])
    assert user_from_db is not None, "Пользователь не найден в БД"
    
    row = user_from_db.iloc[0]
    assert row['user_name'] == user_data['user_name']
    assert row['tariff_id'] == user_data['tariff_id']
    assert row['balance'] == user_data['balance']

def test_post_create_user400(db_engine):
    bad_data = {
        "username": generate_name(style='capital'),
        "tariff": random.randint(999, 10000),
        "number": '7999' + str(random.randint(1000000, 9999999)),
        "money": random.randint(100, 500)
    }

    url = "http://romashka.ru/api/v1.2/users"
    response = requests.post(url, auth=(API_USER, API_PASS), json=bad_data)
    
    assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}" 
    user_from_db = check_new_user_in_bd(db_engine, bad_data["number"])
    assert user_from_db is None, "Некорректный пользователь создался в БД" 

def test_post_create_user401(db_engine):
    user_data = generator()
    characters_for_generate = string.ascii_letters + string.digits + '!$%^'
    password = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 32)))
    username = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 10)))

    url = "http://romashka.ru/api/v1.2/users"
    response = requests.post(url, auth=(username, password), json=user_data)
    assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}" 
    
    user_from_db = check_new_user_in_bd(db_engine, user_data["msisdn"])
    assert user_from_db is None, "Пользователь создался в БД при неверной авторизации"

def test_post_create_user404(db_engine):
    bad_data = {
        "user_name": generate_name(style='capital'),
        "tariff_id": random.randint(999, 10000),
        "msisdn": '7999' + str(random.randint(1000000, 9999999)),
        "balance": random.randint(100, 500)
    }

    url = "http://romashka.ru/api/v1.2/users"
    response = requests.post(url, auth=(API_USER, API_PASS), json=bad_data)
    assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}" 
    
    user_from_db = check_new_user_in_bd(db_engine, bad_data["msisdn"])
    assert user_from_db is None, "Пользователь с несуществующим тарифом создался в БД"