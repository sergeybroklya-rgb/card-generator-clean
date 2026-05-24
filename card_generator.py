import os
os.environ["NO_PROXY"] = "*"
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["ALL_PROXY"] = ""

import requests
import json
import random
from config import USE_YANDEX_GPT, YANDEX_API_KEY, YANDEX_FOLDER_ID

def call_yandex_gpt(prompt: str) -> str:
    """Отправляет запрос к YandexGPT и возвращает ответ"""
    if not USE_YANDEX_GPT or not YANDEX_API_KEY:
        return ""

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 250
        },
        "messages": [
            {"role": "user", "text": prompt}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result["result"]["alternatives"][0]["message"]["text"]
        else:
            print(f"⚠️ Ошибка YandexGPT: статус {response.status_code}")
            return ""
    except Exception as e:
        print(f"⚠️ Ошибка YandexGPT: {e}")
        return ""

# ================= ШАБЛОНЫ (запасной вариант) =================
def generate_title_fallback(product_name, brand, category, features):
    templates = [
        f"{brand} {product_name} - {category}, {features.split(',')[0] if features else 'отличное качество'}",
        f"{product_name} {brand}, {category} с доставкой по России",
        f"{product_name} купить в интернет-магазине - {brand}, {category}"
    ]
    return random.choice(templates)

def generate_description_fallback(product_name, brand, features, price):
    return [
        f"✅ {product_name} от бренда {brand} — отличный выбор. Цена: {price} ₽. {features}",
        f"🔥 {brand} {product_name} по лучшей цене! ⭐ {features}. Быстрая доставка.",
        f"🎯 Успей купить {product_name}! {brand} — качество. {features}. Цена: {price} ₽."
    ]

def generate_keywords_fallback(product_name, brand, category):
    keywords = [f"{product_name} купить", f"{brand} {category}", f"{category} с доставкой", f"{brand} официальный магазин"]
    return ", ".join(keywords)

def generate_specs_fallback(features, color):
    return f"Цвет: {color}, {features}"

# ================= ОСНОВНЫЕ ФУНКЦИИ С ИИ =================
def generate_title(product_name, brand, category, features):
    if USE_YANDEX_GPT and YANDEX_API_KEY:
        prompt = f"""
Ты — копирайтер для маркетплейсов (Wildberries, Ozon). 
Напиши SEO-оптимизированное название товара длиной до 100 символов.

Товар: {product_name}
Бренд: {brand}
Категория: {category}
Особенности: {features}

Название должно включать бренд, тип товара, главную характеристику.
Не используй слова "купить", "скидка", "акция".
Только название.
"""
        result = call_yandex_gpt(prompt)
        if result:
            return result.strip()
    return generate_title_fallback(product_name, brand, category, features)

def generate_descriptions(product_name, brand, features, price):
    if USE_YANDEX_GPT and YANDEX_API_KEY:
        prompt = f"""
Ты — копирайтер для маркетплейсов. Напиши 3 варианта описания товара (по 2-3 предложения).

Товар: {product_name}
Бренд: {brand}
Особенности: {features}
Цена: {price} ₽

Описание должно быть продающим, но без кликбейта. Не используй слова "успей", "торопись".
Начни варианты с 1) 2) 3)
"""
        result = call_yandex_gpt(prompt)
        if result:
            lines = [line.strip() for line in result.split('\n') if line.strip()]
            descriptions = []
            for line in lines:
                if line and line[0] in '0123456789' and (len(line) > 1 and line[1] in '. )'):
                    desc = line[2:].strip()
                    descriptions.append(desc)
            while len(descriptions) < 3:
                descriptions.append(f"Отличный выбор — {product_name} от {brand}. {features}. Цена: {price} ₽.")
            return descriptions[:3]
    return generate_description_fallback(product_name, brand, features, price)

def generate_keywords(product_name, brand, category):
    if USE_YANDEX_GPT and YANDEX_API_KEY:
        prompt = f"""
Ты — SEO-специалист. Сгенерируй 7-10 ключевых слов для карточки товара на маркетплейсе.

Товар: {product_name}
Бренд: {brand}
Категория: {category}

Ключевые слова должны быть через запятую, включать бренд, категорию, тип товара.
Пример: наушники jbl, jbl tune 510bt, беспроводные наушники
"""
        result = call_yandex_gpt(prompt)
        if result:
            return result.strip()
    return generate_keywords_fallback(product_name, brand, category)

def generate_specs(features, color):
    if USE_YANDEX_GPT and YANDEX_API_KEY:
        prompt = f"""
Собери характеристики товара в одну строку через запятую.

Особенности: {features}
Цвет: {color}

Формат: "Цвет: X, особенность 1, особенность 2"
"""
        result = call_yandex_gpt(prompt)
        if result:
            return result.strip()
    return generate_specs_fallback(features, color)

def process_product(row):
    product_name = row.get('product_name', '')
    brand = row.get('brand', '')
    category = row.get('category', '')
    price = row.get('price', 0)
    color = row.get('color', '')
    features = row.get('features', '')

    descriptions = generate_descriptions(product_name, brand, features, price)

    return {
        'generated_title': generate_title(product_name, brand, category, features),
        'generated_description_1': descriptions[0] if len(descriptions) > 0 else "",
        'generated_description_2': descriptions[1] if len(descriptions) > 1 else "",
        'generated_description_3': descriptions[2] if len(descriptions) > 2 else "",
        'generated_keywords': generate_keywords(product_name, brand, category),
        'generated_specs': generate_specs(features, color)
    }

if __name__ == "__main__":
    test_row = {
        'product_name': 'Наушники JBL Tune 510BT',
        'brand': 'JBL',
        'category': 'Аудио',
        'price': 3500,
        'color': 'чёрный',
        'features': 'Bluetooth 5.0, 40 часов работы'
    }
    result = process_product(test_row)
    for key, value in result.items():
        print(f"{key}: {value}")