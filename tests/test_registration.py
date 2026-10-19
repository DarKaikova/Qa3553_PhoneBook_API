import time
import uuid
from dataclasses import asdict

import pytest
import requests

from config import API_BASE_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD
from exploration import response, payload
from models.user import User
from tests.conftest import auth_headers, unique_email


def test_registration_success(new_user):
    #unique_email = f"student_{uuid.uuid4().hex[:8]}@gmail.com"


    # 1. Придумываем уникальные данные нового пользователя
    # new_user = {
    #     "username": unique_email,
    #     "password": "StrongPassword124$"
    # }

    # user = User(
    #     username = unique_email,
    #     password= "Password123$"
    # )

    payload = asdict(new_user)


    # 2. Отправляем запрос на регистрацию
    response = requests.post(f"{API_BASE_URL}v1/user/registration/usernamepassword", json=payload)

    # Проверяем, что регистрация прошла успешно
    assert response.status_code == 200

    response_data = response.json()

    assert response_data["token"]

    # 3. Допустим, сервер сразу вернул нам токен в ответе:
    # response_data = response.json()
    # my_brand_new_token = response_data["token"]

    # И теперь мы можем использовать этот новый индивидуальный токен
    # для дальнейших запросов (например, для создания контактов)





# def test_registration_duplicate_user():
#     # registered_user={
#     #     "username": TEST_USER_EMAIL,
#     #     "password": TEST_USER_PASSWORD
#     # }
#
#     user = User(
#         username = TEST_USER_EMAIL,
#         password= TEST_USER_PASSWORD
#     )
#     payload = asdict(user)
#
#     response = requests.post(f"{API_BASE_URL}v1/user/registration/usernamepassword", json=payload)
#     assert response.status_code == 409





def test_registration_with_invalid_email():
    # payload={
    #     "username": "darik.com",
    #     "password": TEST_USER_PASSWORD
    # }

    user = User(
        username = "darik.com",
        password= "Password123$"
    )
    payload = asdict(user)

    response = requests.post(f"{API_BASE_URL}v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400
    assert "username" in response.json()["message"]
    body = response.json()
    assert body["status"] == 400
    assert body["error"] == "Bad Request"
    assert body["path"] == "/v1/user/registration/usernamepassword"




def test_registration_with_invalid_password():
    # payload={
    #     "username": TEST_USER_EMAIL,
    #     "password": "Kk12"
    # }

    user = User(
        username = unique_email(),
        password= "kk12"
    )
    payload = asdict(user)

    response = requests.post(f"{API_BASE_URL}v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400





def test_registration_password_without_uppercase_rejected():
    unique_email = f"student_{uuid.uuid4().hex[:8]}@gmail.com"

    # payload={
    #     "username": unique_email,
    #     "password": "password123$"
    # }

    user = User(
        username = unique_email,
        password= "password123$"
    )
    payload = asdict(user)

    response = requests.post(f"{API_BASE_URL}v1/user/registration/usernamepassword", json=payload)

    assert response.status_code == 400
    assert "password" in response.json()["message"]





def test_registration_password_too_short(unique_email):
    #unique_email = f"student_{uuid.uuid4().hex[:8]}@gmail.com"

    payload={
        "username": unique_email,
        "password": "pP1$"
    }

    response = requests.post(f"{API_BASE_URL}v1/user/registration/usernamepassword", json=payload)

    assert response.status_code == 400
    assert "password" in response.json()["message"]





def test_registration_empty_email():
    registered_user={
        "username": " ",
        "password": TEST_USER_PASSWORD
    }

    response = requests.post(f"{API_BASE_URL}v1/user/registration/usernamepassword", json=registered_user)
    assert response.status_code == 400


def test_registration_empty_password():
    registered_user={
        "username": TEST_USER_EMAIL,
        "password": " "
    }

    response = requests.post(f"{API_BASE_URL}v1/user/registration/usernamepassword", json=registered_user)
    assert response.status_code == 400







@pytest.mark.parametrize(
    "field, bad_value",
    [
        pytest.param("password", "Pass12$", id="password_too_short"),
        pytest.param("password", "password123$", id="password_no_uppercase"),
        pytest.param("password", "PASSWORD123$", id="password_no_lowercase"),
        pytest.param("password", "PASSWORD$", id="password_no_digits"),
        pytest.param("password", "Password123", id="password_no_special_char"),
        # pytest.param("password","PASSWORD123$fddgjhdkfdfdfdfdfdfdfjhfdkhj", id="password_too_long"),
        pytest.param("username", "user@", id="username_no_domain"),
        pytest.param("username", "notanemail", id="username_no_at_sign"),
        pytest.param("username", "@gmail.com", id="username_no_local_part"),
        pytest.param("username", "", id="username_empty"),
    ]
)

def test_registration_with_invalid_value_rejected(new_user, field, bad_value):
    payload = asdict(new_user)
    payload[field] = bad_value

    response = requests.post(f"{API_BASE_URL}v1/user/registration/usernamepassword", json=payload)

    assert response.status_code == 400
    assert field in response.json()["message"]
    body = response.json()
    assert "token" not in body

@pytest.mark.parametrize(
    "missing_field", ["username", "password"]
)

def test_registration_with_missing_field_rejected(new_user, missing_field):
    payload = asdict(new_user)
    del payload[missing_field]

    response = requests.post(f"{API_BASE_URL}v1/user/registration/usernamepassword", json=payload)

    assert response.status_code == 400
    assert missing_field in response.json()["message"]


def test_registration_with_empty_password_rejected(unique_email):
    payload = asdict(User(username=unique_email, password=""))
    response = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)

    assert response.status_code == 400
    assert response.json()["error"] == "Bad Request"



def test_registration_duplicate_user_rejected(new_user):
    payload = asdict(new_user)

    first_response = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)
    assert first_response.status_code == 200

    second_response = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)
    assert second_response.status_code == 409
    assert "already exists" in second_response.json()["message"]
    assert second_response.json()["status"]==409
    assert second_response.json()["error"] == "Conflict"
    assert second_response.json()["path"] == "/v1/user/registration/usernamepassword"

















