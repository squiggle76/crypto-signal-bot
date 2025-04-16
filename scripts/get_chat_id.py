import requests

TOKEN = "7775976297:AAGXD9KqM_x9y4ITM8IroODuiJuwuHmvhAw"

def get_updates():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url)
    data = response.json()
    print(data)
    if data["ok"] and data["result"]:
        for update in data["result"]:
            print("👤 chat_id:", update["message"]["chat"]["id"])
    else:
        print("⚠️ Не найдено сообщений. Напиши что-нибудь своему боту в Telegram.")

if __name__ == "__main__":
    get_updates()
