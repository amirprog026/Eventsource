import requests
from flask import current_app


class AuthService:
    BASE_URL = "http://auth.dbcloud.ir/index.php"

    @staticmethod
    def _request(endpoint, method='POST', headers=None, data=None):
        if headers is None:
            headers = {
                "Content-Type": "application/json",
                "X-Api-Key": "123a"  # Replace with your static API key
            }
        url = f"{AuthService.BASE_URL}?action={endpoint}"
        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def register(platform, username, password):
        data = {
            "platform": platform,
            "username": username,
            "password": password
        }
        return AuthService._request("register", data=data)

    @staticmethod
    def login(username, password):
        data = {
            "username": username,
            "password": password
        }
        return AuthService._request("login", data=data)

    @staticmethod
    def add_user_meta(user_id, meta_key, meta_value):
        data = {
            "user_id": user_id,
            "meta_key": meta_key,
            "meta_value": meta_value
        }
        return AuthService._request("add-meta", data=data)
