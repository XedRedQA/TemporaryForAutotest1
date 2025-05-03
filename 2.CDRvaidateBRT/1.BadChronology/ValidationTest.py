import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from sqlalchemy import create_engine
import pandas as pd

with open('BadChronologyCDR1.csv', 'r') as file:
    lines = file.readlines()

@pytest.fixture(scope="module")
def browser():
    browser = webdriver.Firefox()
    browser.get("http://127.0.0.1:15672/#/")
    yield browser
    browser.quit()

def test_enter_rabbitmq(browser):
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

    payload_input.send_keys(''.join(lines))

    send_publish_message = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Publish message"]')))
    assert send_publish_message.is_displayed(), "Кнопка 'Publish message' не найдена"
    send_publish_message.click()

    assert "Message published" in browser.page_source, "Сообщение не было опубликовано в очередь RabbitMQ"

    
def test_extract_brt_logs():
    os.chdir("..")
    os.chdir("..")
    os.chdir("..")
    command = "docker compose logs --tail 34 brt"
    output_file = "Autotest/2.CDRvaidateBRT/1.BadChronology/brtlogs.csv"
    result = os.system(f"{command} > {output_file}")

    assert result == 0, "Не удалось получить логи brt"

    os.chdir("Autotest/2.CDRvaidateBRT/1.BadChronology/")
    with open('BadChronologyCDR1.csv') as logs:
        words = logs.readlines()


    with open('clear_numbers.csv', 'w') as logs:
        for line in words:
            line2 = line[:15]
            line1 = line2[4:]
            logs.write(line1 + '\n')

def test_bd_select():
    with open('clear_numbers.csv', 'r') as brtlog:
        numbers = [line.strip() for line in brtlog if line.strip()]
    
    assert len(numbers) == 10, "Файл очищенных логов содержит не 10 строк"
    
    uid = 'admin'
    pwd = 'admin'
    server = 'localhost'
    database = 'romashka'
    engine = create_engine(f'postgresql://{uid}:{pwd}@{server}:54320/{database}')
    numbers_placeholder = "', '".join(numbers)
    sql = f"SELECT * FROM call_records WHERE caller_msisdn IN ('{numbers_placeholder}');"
    df = pd.read_sql_query(sql, engine)
    df.to_csv('selectbd.csv', index=False)

    for num in numbers:
        count = df[df['caller_msisdn'] == num].shape[0]
        if count == 0:
            print(f"Предупреждение: для номера {num} нет записей в базе.")