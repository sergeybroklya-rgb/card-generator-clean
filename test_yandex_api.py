import os
import requests

# ОТКЛЮЧАЕМ ПРОКСИ
os.environ["NO_PROXY"] = "*"
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["ALL_PROXY"] = ""

# ================== ВСТАВЬ СВОИ ДАННЫЕ ==================
API_KEY = ""  # 👈 ВСТАВЬ СВОЙ ПОЛНЫЙ API-КЛЮЧ
FOLDER_ID = ""  # 👈 ВСТАВЬ СВОЙ FOLDER ID

print(f"🔑 Использую Folder ID: {FOLDER_ID}")
print(f"🔐 Использую API Key (первые 6 символов): {API_KEY[:6]}... (скрыто)")

# ================== ПРАВИЛЬНЫЙ ЗАПРОС ==================
url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
headers = {
    "Authorization": f"Api-Key {API_KEY}",
    "Content-Type": "application/json"
}
data = {
    "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
    "completionOptions": {
        "stream": False,
        "temperature": 0.6,
        "maxTokens": 50
    },
    "messages": [
        {"role": "user", "text": "Напиши слово Привет"}
    ]
}

print("📤 Отправляю запрос к YandexGPT...")
try:
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"📥 Статус ответа: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ УСПЕХ! YandexGPT отвечает:")
        print(result["result"]["alternatives"][0]["message"]["text"])
    else:
        print(f"\n❌ Ошибка API. Подробности:")
        print(response.text)
        
except Exception as e:
    print(f"❌ Ошибка при выполнении запроса: {e}")