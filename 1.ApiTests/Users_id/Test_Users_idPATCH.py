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


@pytest.fixture
def db_engine():

    server = 'localhost'
    database = 'romashka'
    return create_engine(f'postgresql://{uid}:{pwd}@{server}:54320/{database}')


@pytest.fixture
def create_request(db_engine):
    sql = "SELECT user_id,user_name, msisdn FROM users_saved ORDER BY RANDOM() LIMIT 1;"
    df = pd.read_sql_query(sql, db_engine)
    return df

@pytest.fixture
def select_user_id_bd(create_request):
    id = create_request.iloc[0]['user_id']
    return id

@pytest.fixture
def select_user_name_bd(create_request):
    username = create_request.iloc[0]['user_name']
    return username

@pytest.fixture
def select_user_number_bd(create_request):
    telephone_number = create_request.iloc[0]['msisdn']
    return telephone_number

def Check_changes_in_bd(select_user_id_bd,db_engine):
    sql = f"SELECT user_name, msisdn FROM users_saved WHERE user_id = {select_user_id_bd}"
    df = pd.read_sql_query(sql, db_engine)
    user_data = df.iloc[0]
    return user_data

def test_patch_user_name_id200(select_user_id_bd,select_user_name_bd,db_engine):
    
    Params = ["user_id", "user_name", "tariff_id", "msisdn", "balance", "registration_date", "payment_day", "minutes", ]
    
    username = generate_name(style='capital')
    payload_with_name = {
        "user_name": username 
    }

    url = f"http://romashka.ru/api/v1.2/users/{select_user_id_bd}"
    response = requests.patch(url, auth=(API_USER, API_PASS), json=payload_with_name)
    
    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}" 
    assert response.headers["Content-Type"] == "application/json; charset=UTF-8"
    
    user = response.json() 
    assert isinstance(user, dict)
    for key in Params:
        assert key in user, f"Поле {key} отсутствует у пользователя"
    
    new_data_for_check = Check_changes_in_bd(db_engine, select_user_id_bd)
    assert select_user_name_bd != new_data_for_check['user_name'], "Имя не поменялось, ожидалось, что имя изменится"

def test_patch_user_msisdn_id200(select_user_id_bd,select_user_number_bd,db_engine):
    Params = ["user_id", "user_name", "tariff_id", "msisdn", "balance", "registration_date", "payment_day", "minutes", ]

    telephone_number = '7999' +  str(random.randint(1000000, 9999999))
    payload_with_number = {
        "msisdn": telephone_number 
    }
    url = f"http://romashka.ru/api/v1.2/users/{select_user_id_bd}"
    response = requests.patch(url, auth=(API_USER, API_PASS), json=payload_with_number)
    
    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}" 
    assert response.headers["Content-Type"] == "application/json; charset=UTF-8"
    
    user = response.json() 
    assert isinstance(user, dict)
    for key in Params:
        assert key in user, f"Поле {key} отсутствует у пользователя"

    new_data_for_check = Check_changes_in_bd(db_engine, select_user_id_bd)
    assert select_user_number_bd != new_data_for_check['msisdn'], "Номер телефона не изменился, ожидалось, что номер изменится"

def test_patch_user_id400(select_user_id_bd):

    telephone_number = '7999' +  str(random.randint(1000000, 9999999))
    payload_with_number = {
        "phone_num": telephone_number 
    }
    url = f"http://romashka.ru/api/v1.2/users/{select_user_id_bd}"
    response = requests.patch(url, auth=(API_USER, API_PASS), json=payload_with_number)
    
    assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}" 

def test_patch_user_id401(select_user_id_bd):

    characters_for_generate = string.ascii_letters + string.digits + '!$%^'
    password = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 32)))
    username = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 10)))

    url = f"http://romashka.ru/api/v1.2/users/{select_user_id_bd}"
    response = requests.patch(url, auth=(username, password))
    
    assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}"  

def test_patch_user_id404():
    bad_id = random.randint(1000000, 9999999)
    url = f"http://romashka.ru/api/v1.2/users/{bad_id}"
    response = requests.patch(url, auth=(API_USER, API_PASS))
    
    assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}" 