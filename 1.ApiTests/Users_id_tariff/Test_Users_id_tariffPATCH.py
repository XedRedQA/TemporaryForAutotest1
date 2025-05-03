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
    sql = "SELECT user_id,tariff_id FROM users_saved ORDER BY RANDOM() LIMIT 1;"
    df = pd.read_sql_query(sql, db_engine)
    return df

@pytest.fixture
def select_user_id_bd(create_request):
    id = create_request.iloc[0]['user_id']
    return id

@pytest.fixture
def select_user_tariff_bd(create_request):
    tariff = create_request.iloc[0]['tariff_id']
    return tariff

def check_changes_in_bd(db_engine, select_user_id_bd):
    sql = f"SELECT tariff_id FROM users_saved WHERE user_id = {select_user_id_bd}"
    df = pd.read_sql_query(sql, db_engine)
    user_data = df.iloc[0]
    return user_data

def test_patch_user_id_tariff200(select_user_id_bd,select_user_tariff_bd,db_engine):

    if select_user_tariff_bd == 12:
        payload_new_tariff = {
            "tariff_id": 11
        }
    else:
        payload_new_tariff = {
            "tariff_id": 12
        }

    url = f"http://romashka.ru/api/v1.2/users/{select_user_id_bd}/tariff"
    response = requests.patch(url, auth=('admin', 'admin'), json=payload_new_tariff)

    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}" 
    assert response.headers["Content-Type"] == "application/json; charset=UTF-8"
    
    user_tariff = response.json()
    assert "tariff" in user_tariff, "Поле tariff не отобразилось"
    
    new_tariff_for_check = check_changes_in_bd(db_engine, select_user_id_bd)
    assert select_user_tariff_bd != new_tariff_for_check['tariff_id'], "Тариф не изменился, ожидалось, что имя изменится"

def test_patch_user_id_tariff400(select_user_id_bd, select_user_tariff_bd, db_engine):

    if select_user_tariff_bd == 12:
        payload_new_tariff = {
            "tariff_id": 12
        }
    else:
        payload_new_tariff = {
            "tariff_id": 11
        }

    url = f"http://romashka.ru/api/v1.2/users/{select_user_id_bd}/tariff"
    response = requests.patch(url, auth=('admin', 'admin'), json=payload_new_tariff)

    assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}" 
    assert response.headers["Content-Type"] == "application/json; charset=UTF-8"
    
    user_tariff = response.json()
    assert "error" in user_tariff
    assert user_tariff["error"] == "Абонент уже подключен к этому тарифу"

    current = check_changes_in_bd(db_engine, select_user_id_bd)
    assert current['tariff_id'] == select_user_tariff_bd, "Тариф изменился, хотя не должен был"

def test_patch_user_id_tariff401(select_user_id_bd):

    characters_for_generate = string.ascii_letters + string.digits + '!$%^'
    password = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 32)))
    username = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 10)))

    url = f"http://romashka.ru/api/v1.2/users/{select_user_id_bd}/tariff"
    response = requests.patch(url, auth=(username, password))
    
    assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}"  

def test_patch_user_id_tariff404(select_user_id_bd):
    bad_tariff_id = random.randint(1000000, 9999999)
    data = {
            "tariff_id": bad_tariff_id
        }
    url = f"http://romashka.ru/api/v1.2/users/{select_user_id_bd}/tariff"
    response = requests.patch(url, auth=('admin', 'admin'), json=data)
    
    assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}" 
