# TemporaryForAutotest" 
## Запуск 1.ApiTests
```bash
pytest .\{Name_of_file.py}
```
## Запуск 2.CDRvaidateBRT
```bash
pytest -s .\ValidationTest.py
```
## Запуск 3.e2eProcess
```bash
pytest .\{Name_of_file.py}
```
## Запуск 4.GenerateCDR
```bash
.\{Name_of_file.py}
```
## Работа с Allure report
### Запуск автотеста с создание файлов отчета 
```bash
pytest --alluredir allure-results
```
### Просмотр отчета
```bash
allure serve allure-results
```
