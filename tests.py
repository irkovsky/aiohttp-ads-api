import requests
from requests.auth import HTTPBasicAuth

url = "http://127.0.0.1:5000"

# 1. Регистрация пользователя
r = requests.post(f"{url}/users", json={"email": "anna@example.com", "password": "secret"})
print("Регистрация:", r.status_code, r.json())  # 201
print("Текст ответа:", r.text)

# 2. Создание объявления БЕЗ авторизации (должно быть 401)
r = requests.post(f"{url}/ads", json={"title": "Без авторизации"})
print("Без авторизации:", r.status_code, r.json())  # 401

# 3. Создание объявления С авторизацией
auth = HTTPBasicAuth("anna@example.com", "secret")
r = requests.post(f"{url}/ads", json={"title": "Велосипед", "description": "Почти новый"}, auth=auth)
print("Создание:", r.status_code, r.json())  # 201
ad_id = r.json()["id"]

# 4. Получение объявления (доступно всем)
r = requests.get(f"{url}/ads/{ad_id}")
print("Получение:", r.status_code, r.json())  # 200

# 5. Редактирование СВОЕГО объявления
r = requests.patch(f"{url}/ads/{ad_id}", json={"title": "Велосипед (скидка)"}, auth=auth)
print("Редактирование:", r.status_code, r.json())  # 200

# 6. Попытка удалить чужое объявление (создадим второго пользователя)
requests.post(f"{url}/users", json={"email": "bob@example.com", "password": "secret2"})
bob_auth = HTTPBasicAuth("bob@example.com", "secret2")
r = requests.delete(f"{url}/ads/{ad_id}", auth=bob_auth)
print("Удаление чужого:", r.status_code, r.json())  # 403

# 7. Удаление СВОЕГО объявления
r = requests.delete(f"{url}/ads/{ad_id}", auth=auth)
print("Удаление своего:", r.status_code, r.json())  # 200