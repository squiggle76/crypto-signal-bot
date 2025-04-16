from config.config import API_KEY, SECRET_KEY

def get_api_keys():
    """Возвращает API-ключи из конфигурации."""
    if not API_KEY or not SECRET_KEY:
        print("⚠️ API-ключи не заданы! Укажите их в config.py")
    return API_KEY, SECRET_KEY
