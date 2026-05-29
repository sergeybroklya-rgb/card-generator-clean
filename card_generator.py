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
            "maxTokens": 300
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
            return ""
    except Exception:
        return ""

def get_tone_instruction(tone: str) -> str:
    if tone == "professional":
        return "Напиши сухо, по фактам. Только характеристики и преимущества. Без эмоций и восклицательных знаков."
    elif tone == "friendly":
        return "Напиши тёпло, вежливо, по-дружески. Используй слова 'пожалуйста', 'рады предложить', 'спасибо за внимание'."
    elif tone == "selling":
        return "Напиши эмоционально, продающе. Используй восклицательные знаки, слова 'выгодно', 'скидка', 'успей', '🔥', '⭐', '✅'."
    else:
        return "Напиши нейтрально, профессионально."

def get_marketplace_instruction(marketplace: str) -> str:
    if marketplace == "wildberries":
        return "Учитывай требования Wildberries: описание короткое, по делу, без воды."
    elif marketplace == "ozon":
        return "Учитывай требования Ozon: первые 2 предложения — ключевые, можно эмоции."
    elif marketplace == "yandex":
        return "Учитывай требования Яндекс Маркета: важна структура, характеристики и описание."
    else:
        return ""

def generate_title(product_name, brand, category, features, tone="professional", marketplace="wildberries"):
    if USE_YANDEX_GPT and YANDEX_API_KEY:
        tone_inst = get_tone_instruction(tone)
        marketplace_inst = get_marketplace_instruction(marketplace)
        prompt = f"""
Ты — копирайтер для маркетплейсов. Напиши SEO-оптимизированное название товара длиной до 100 символов.

Товар: {product_name}
Бренд: {brand}
Категория: {category}
Особенности: {features}

{tone_inst}
{marketplace_inst}

Название должно включать бренд, тип товара, главную характеристику.
Только название, без лишних слов.
"""
        result = call_yandex_gpt(prompt)
        if result:
            return result.strip()
    return f"{brand} {product_name} - {category}"

def generate_descriptions(product_name, brand, features, price, tone="professional", marketplace="wildberries"):
    if USE_YANDEX_GPT and YANDEX_API_KEY:
        tone_inst = get_tone_instruction(tone)
        marketplace_inst = get_marketplace_instruction(marketplace)
        prompt = f"""
Ты — копирайтер для маркетплейсов. Напиши 3 варианта описания товара (по 2-3 предложения).

Товар: {product_name}
Бренд: {brand}
Особенности: {features}
Цена: {price} ₽

{tone_inst}
{marketplace_inst}

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
                descriptions.append(f"{product_name} от {brand}. {features}. Цена: {price} ₽.")
            return descriptions[:3]
    return [f"{product_name} от {brand}. {features}. Цена: {price} ₽."] * 3

def generate_keywords(product_name, brand, category):
    if USE_YANDEX_GPT and YANDEX_API_KEY:
        prompt = f"""
Ты — SEO-специалист. Сгенерируй 7-10 ключевых слов для карточки товара на маркетплейсе.

Товар: {product_name}
Бренд: {brand}
Категория: {category}

Ключевые слова должны быть через запятую.
"""
        result = call_yandex_gpt(prompt)
        if result:
            return result.strip()
    return f"{product_name}, {brand}, {category}"

def generate_specs(features, color):
    if USE_YANDEX_GPT and YANDEX_API_KEY:
        prompt = f"""
Собери характеристики товара в одну строку через запятую.

Особенности: {features}
Цвет: {color}
"""
        result = call_yandex_gpt(prompt)
        if result:
            return result.strip()
    return f"Цвет: {color}, {features}"

def process_product(row, tone="professional", marketplace="wildberries"):
    product_name = row.get('product_name', '')
    brand = row.get('brand', '')
    category = row.get('category', '')
    price = row.get('price', 0)
    color = row.get('color', '')
    features = row.get('features', '')

    descriptions = generate_descriptions(product_name, brand, features, price, tone, marketplace)

    return {
        'generated_title': generate_title(product_name, brand, category, features, tone, marketplace),
        'generated_description_1': descriptions[0] if len(descriptions) > 0 else "",
        'generated_description_2': descriptions[1] if len(descriptions) > 1 else "",
        'generated_description_3': descriptions[2] if len(descriptions) > 2 else "",
        'generated_keywords': generate_keywords(product_name, brand, category),
        'generated_specs': generate_specs(features, color)
    }