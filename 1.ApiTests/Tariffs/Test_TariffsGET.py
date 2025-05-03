import pytest
import requests
import string
import random

def test_get_tariffs200():
    
    Params = ["tariff_id", "tariff_name", "tariff_desc", "type_id", "interval", "price", "param_id", "param_value" ]

    url = "http://romashka.ru/api/v1.2/tariffs"
    response = requests.get(url, auth=('admin', 'admin'))
    
    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}" 
    assert response.headers["Content-Type"] == "application/json; charset=UTF-8"
    
    tariffslist = response.json() 
    assert isinstance(tariffslist, list)
    assert len(tariffslist) > 0, "Список тарифов пуст"
    
    for tariff in tariffslist:
        for key in Params:
            assert key in tariff, f"Поле {key} отсутствует у тарифа {tariff}"

def test_get_tariffs400():

    bad_header = {"Content-Type": "💀/💀💀"}
    url = "http://romashka.ru/api/v1.2/tariffs"
    response = requests.get(url, auth=('admin', 'admin'), headers=bad_header)
    
    assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}" 

def test_get_tariffs401():
    characters_for_generate = string.ascii_letters + string.digits + '!$%^'
    password = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 32)))
    username = ''.join(random.choice(characters_for_generate) for _ in range(random.randint(5, 10)))

    url = "http://romashka.ru/api/v1.2/tariffs"
    response = requests.get(url, auth=(username, password))
    
    assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}"  

def test_get_tariffs404():
    url = "http://romashka.ru/api/v1.2/tariffi"
    response = requests.get(url, auth=('admin', 'admin'))
    
    assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}" 