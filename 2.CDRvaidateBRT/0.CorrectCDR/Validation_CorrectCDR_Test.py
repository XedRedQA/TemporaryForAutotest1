import pytest
import allure
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

uid = os.getenv("DB_USER")
pwd = os.getenv("DB_PASSWORD")
rmq_user = os.getenv('RMQ_USER')
rmq_password = os.getenv('RMQ_PASSWORD')

with open('CDR1.csv', 'r') as file:
    lines = file.readlines()

@pytest.fixture(scope="module")
def browser():
    browser = webdriver.Firefox()
    browser.get("http://127.0.0.1:15672/#/")
    yield browser
    browser.quit()

@allure.title("Тест входа в RabbitMQ и публикации сообщения")
def test_enter_rabbitmq(browser):
    wait = WebDriverWait(browser, 10)

    with allure.step("Ввод логина и пароля"): 
        login_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        login_input.send_keys(rmq_user)
        password_input.send_keys(rmq_password)
    
    with allure.step("Клик по кнопке логина"):
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Login"]')))
        assert login_button.is_displayed(), "Кнопка логина не отобразилась"
        login_button.click()
    
    with allure.step("Переход во вкладку очередей"):
        queue_header = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#/queues"]')))
        assert queue_header.is_displayed(), "Вкладка Queue не появилась после логина"
        queue_header.click()
    
    with allure.step("Выбор очереди cdr.queue"):
        cdr_queue_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#/queues/%2F/cdr.queue"]')))
        assert cdr_queue_button.is_displayed(), "Кнопка cdr.queue не отобразилась"
        cdr_queue_button.click()

    with allure.step("Открытие формы публикации сообщения"):
        publish_message_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//h2[text()="Publish message"]')))
        assert publish_message_button.is_displayed(), "Заголовок Publish message не найден"
        publish_message_button.click()
    
    with allure.step("Ввод сообщения и публикация"):
        payload_input = wait.until(EC.presence_of_element_located((By.NAME, "payload")))
        payload_input.send_keys(''.join(lines))

        send_publish_message = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Publish message"]')))
        assert send_publish_message.is_displayed(), "Кнопка 'Publish message' не найдена"
        send_publish_message.click()
    
    with allure.step("Проверка публикации сообщения"):
        assert "Message published" in browser.page_source, "Сообщение не было опубликовано в очередь RabbitMQ"

@allure.title("Подготовка номеров из CDR")
def test_clear_cdr_numbers():
    with allure.step("Очистка исходной CDR от лишних данных"):
        with open('CDR1.csv') as logs:
            words = logs.readlines()

        with open('clear_numbers.csv', 'w') as logs:
            for line in words:
                if "call_type, caller_msisdn, receiver_msisdn, start_time, end_time" not in line:
                    line2 = line[:15]
                    line1 = line2[4:]
                    logs.write(line1 + '\n')
    time.sleep(3)
@allure.title("Проверка записей в базе данных по номерам")
def test_bd_select():
    with allure.step("Чтение номеров из подготовленного файла"):
        with open('clear_numbers.csv', 'r') as brtlog:
            numbers = [line.strip() for line in brtlog if line.strip()]

    with allure.step("Подключение к базе данных и выполнение запроса"):      
        server = 'localhost'
        database = 'romashka'
        engine = create_engine(f'postgresql://{uid}:{pwd}@{server}:54320/{database}')
        numbers_placeholder = "', '".join(numbers)
        sql = f"SELECT * FROM call_records WHERE caller_msisdn IN ('{numbers_placeholder}');"
        df = pd.read_sql_query(sql, engine)
        df.to_csv('selectbd.csv', index=False)

    with allure.step("Проверка наличия записей по каждому номеру"):
        for num in numbers:
            count = df[df['caller_msisdn'] == num].shape[0]
            if count == 0:
                print(f"Предупреждение: для номера {num} нет записей в базе.")

@allure.title("Извлечение логов BRT")
def test_extract_brt_logs():
    with allure.step("Переход в корень проекта и получение логов"):
        os.chdir("..")
        os.chdir("..")
        os.chdir("..")
        command = "docker compose logs --since 15s brt"
        output_file = "Autotest/2.CDRvaidateBRT/0.CorrectCDR/brtlogs.csv"
        result = os.system(f"{command} > {output_file}")
        assert result == 0, "Не удалось получить логи brt"