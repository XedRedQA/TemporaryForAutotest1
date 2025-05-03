import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import pandas as pd


def test_SelectAbonentsForCall():

    uid = 'admin'
    pwd = 'admin'
    server = 'localhost'
    database = 'romashka'
    engine = create_engine(f'postgresql://{uid}:{pwd}@{server}:54320/{database}')
    sql = "SELECT msisdn,balance FROM users_saved WHERE balance > 50 AND tariff_id = 11 ORDER BY RANDOM() LIMIT 2;"
    df = pd.read_sql_query(sql, engine)

    assert not df.empty, "Не найдены пользователи с балансом более 50"
    assert 'msisdn' in df.columns, "msisdn отсутствует в результате"
    assert 'balance' in df.columns, "balance отсутствует в результате"

    df.to_csv('UsersWithPositiveBalance.csv',index=False)

def test_CreateCall():
    df = pd.read_csv('UsersWithPositiveBalance.csv', dtype={'msisdn': str})

    assert df.shape[0] >= 2, "Недостаточно пользователей для создания звонка"

    caller = df.iloc[0]['msisdn']
    receiver = df.iloc[1]['msisdn']
    sep = ', '

    call_start = datetime(2025, 4, 30, 00, 00, 00)
    call_ends = call_start + timedelta(seconds=random.randint(1, 59))

    with open('TemporaryNumsHolder.csv', 'w') as tmp:
        tmp.write(caller + '\n' + receiver)
    
    with open('emulatedcall.csv', 'w') as emu:
            emu.write(f"01, " + caller + sep + receiver + sep + call_start.isoformat() + sep + call_ends.isoformat() + "\n")
            emu.write(f"02, " + receiver + sep + caller + sep + call_start.isoformat() + sep + call_ends.isoformat() + "\n")


@pytest.fixture(scope="module")
def browser():
    browser = webdriver.Firefox()
    browser.get("http://127.0.0.1:15672/#/")
    yield browser
    browser.quit()

def test_SendCall(browser):
    
    with open('emulatedcall.csv', 'r') as file:
        lines = file.readlines()
    
    assert lines, "В файле emulatedcall.csv нет данных"

    wait = WebDriverWait(browser, 10)
    
    login_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    
    login_input.send_keys("admin")
    password_input.send_keys("admin")
    
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Login"]')))
    assert login_button.is_displayed(), "Кнопка логина не отобразилась"
    login_button.click()

    queue_header = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#/queues"]')))
    assert queue_header.is_displayed(), "Вкладка Queue не появилась после логина"
    queue_header.click()

    cdr_queue_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#/queues/%2F/cdr.queue"]')))
    assert cdr_queue_button.is_displayed(), "Кнопка cdr.queue не отобразилась"
    cdr_queue_button.click()

    publish_message_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//h2[text()="Publish message"]')))
    assert publish_message_button.is_displayed(), "Заголовок Publish message не найден"
    publish_message_button.click()
    

    payload_input = wait.until(EC.presence_of_element_located((By.NAME, "payload")))

    payload_input.send_keys(lines)

    send_publish_message = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Publish message"]')))
    assert send_publish_message.is_displayed(), "Кнопка 'Publish message' не найдена"
    send_publish_message.click()

def test_SelectAbonents():

    with open('TemporaryNumsHolder.csv', 'r') as tmpN:
        numbers = [line.strip() for line in tmpN if line.strip()]
    
    assert len(numbers) == 2, "TemporaryNumsHolder.csv содержит не два номера"

    uid = 'admin'
    pwd = 'admin'
    server = 'localhost'
    database = 'romashka'
    engine = create_engine(f'postgresql://{uid}:{pwd}@{server}:54320/{database}')
    sql = "SELECT msisdn,balance FROM users_saved WHERE msisdn IN ('" + numbers[0] + "', '" + numbers[1] + "');"
    df = pd.read_sql_query(sql, engine)

    assert df.shape[0] == 2, "Запрос вернул не две записи"
    
    assert 'msisdn' in df.columns, "msisdn отсутствует в результате"
    
    assert 'balance' in df.columns, "balance отсутствует в результате"

    df.to_csv('ChangedBalance.csv', sep=',' ,index=False)

def test_ChangingBalance():
    df1 = pd.read_csv('UsersWithPositiveBalance.csv', nrows=2)
    df2 = pd.read_csv('ChangedBalance.csv')

    assert df1.shape[0] == df2.shape[0], "Количество строк в DataFrame не совпадает"
    
    assert set(df1.columns) == set(df2.columns), "Столбцы в DataFrame не совпадают"

    df1 = df1.sort_values('msisdn').reset_index(drop=True)
    df2 = df2.sort_values('msisdn').reset_index(drop=True)
    df2 = df2[df1.columns]
    df2 = df2.reindex(df1.index)
    df = df1.compare(df2)

    assert not df.empty, "Изменений между DataFrame не найдено"

    df.to_csv('СompareСhanges.csv', index=False)