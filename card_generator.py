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

def get_niche_instruction(niche: str) -> str:
    instructions = {
        "default": "Опиши товар универсально, без привязки к конкретной нише.",
        "sneakers": """
Учитывай особенности категории "Кроссовки / Обувь":
- Обязательно укажи: материал верха, подошвы, размерную сетку
- Важно: амортизация, вес пары, сезонность (лето/зима/демисезон)
- Используй слова: "лёгкие", "дышащие", "износостойкие", "удобная колодка"
""",
        "kettles": """
Учитывай особенности категории "Чайники / Кухонная техника":
- Обязательно укажи: объём, мощность, материал корпуса
- Важно: наличие автоотключения, защита от кипения, съёмный фильтр
- Используй слова: "быстрый нагрев", "энергоэффективный", "безопасное использование"
""",
        "toys": """
Учитывай особенности категории "Игрушки / Детские товары":
- Обязательно укажи: возрастную группу, материал, безопасность
- Важно: развитие навыков (моторика, логика, творчество)
- Используй слова: "безопасные материалы", "развивающая", "сертифицировано"
""",
        "smartphones": """
Учитывай особенности категории "Смартфоны / Телефоны":
- Обязательно укажи: диагональ экрана, процессор, память, камеру
- Важно: время работы от батареи, поддержка 5G, защита от воды
- Используй слова: "производительный", "ёмкий аккумулятор", "яркий дисплей"
""",
        "headphones": """
Учитывай особенности категории "Наушники / Аудиотехника":
- Обязательно укажи: тип (вкладыши/накладные), Bluetooth, время работы
- Важно: шумоподавление, поддержка кодеков, складная конструкция
- Используй слова: "чистый звук", "долгая автономность", "удобная посадка"
""",
        "clothing": """
Учитывай особенности категории "Одежда":
- Обязательно укажи: размерную сетку, состав ткани, сезон
- Важно: уход за вещью, наличие карманов, капюшона
- Используй слова: "дышащая", "не теряет форму", "приятная к телу"
""",
        "watches": """
Учитывай особенности категории "Часы / Аксессуары":
- Обязательно укажи: тип механизма (кварцевые/механические), материал корпуса и ремешка
- Важно: водозащита, подсветка, дополнительные функции (секундомер, будильник)
- Используй слова: "стильный", "надёжный", "точный ход"
""",
        "bags": """
Учитывай особенности категории "Сумки / Рюкзаки":
- Обязательно укажи: материал, размер, количество отделений
- Важно: вес, ремни, карманы, защита от воды
- Используй слова: "вместительный", "лёгкий", "практичный"
""",
        "furniture": """
Учитывай особенности категории "Мебель":
- Обязательно укажи: материал, размеры, максимальную нагрузку
- Важно: сборка (требуется/нет), уход, гарантия
- Используй слова: "прочный", "экологичный", "долговечный"
""",
        "tools": """
Учитывай особенности категории "Инструменты":
- Обязательно укажи: мощность, тип питания (сеть/аккумулятор), комплектацию
- Важно: вес, гарантия, наличие кейса
- Используй слова: "надёжный", "мощный", "профессиональный"
""",
        "cosmetics": """
Учитывай особенности категории "Косметика":
- Обязательно укажи: тип кожи, состав, объём
- Важно: наличие сертификатов, гипоаллергенность, срок годности
- Используй слова: "натуральный", "безопасный", "эффективный"
""",
        "sports": """
Учитывай особенности категории "Спорт / Фитнес":
- Обязательно укажи: назначение, размеры, материал
- Важно: вес, регулировки, безопасность
- Используй слова: "профессиональный", "удобный", "надёжный"
""",
        "books": """
Учитывай особенности категории "Книги":
- Обязательно укажи: автор, жанр, год издания, количество страниц
- Важно: формат (твердый/мягкий переплёт), иллюстрации
- Используй слова: "бестселлер", "подарочное издание", "классика"
""",
        "auto": """
Учитывай особенности категории "Автотовары":
- Обязательно укажи: совместимость с марками авто, материал
- Важно: сертификация, гарантия, установка
- Используй слова: "оригинал", "качественный", "безопасный"
""",
        "pets": """
Учитывай особенности категории "Зоотовары":
- Обязательно укажи: для какого животного, размер, материал
- Важно: безопасность, гигиеничность, срок службы
- Используй слова: "натуральный", "безопасный", "удобный"
""",
        "garden": """
Учитывай особенности категории "Товары для сада":
- Обязательно укажи: материал, размеры, назначение
- Важно: устойчивость к погоде, сборка, хранение
- Используй слова: "прочный", "надёжный", "долговечный"
""",
        "office": """
Учитывай особенности категории "Офисные товары":
- Обязательно укажи: формат, совместимость, упаковку
- Важно: качество печати, срок службы, экологичность
- Используй слова: "качественный", "экономичный", "удобный"
""",
        "food": """
Учитывай особенности категории "Продукты питания":
- Обязательно укажи: состав, калорийность, срок годности
- Важно: условия хранения, сертификация, страна производства
- Используй слова: "натуральный", "вкусный", "полезный"
""",
        "jewelry": """
Учитывай особенности категории "Украшения":
- Обязательно укажи: материал, пробу, вес
- Важно: уход, сертификация, упаковка
- Используй слова: "изящный", "классический", "подарочный"
""",
    }
    return instructions.get(niche, instructions["default"])

def generate_title(product_name, brand, category, features, tone="professional", marketplace="wildberries", niche="default"):
    if USE_YANDEX_GPT and YANDEX_API_KEY:
        tone_inst = get_tone_instruction(tone)
        marketplace_inst = get_marketplace_instruction(marketplace)
        niche_inst = get_niche_instruction(niche)
        prompt = f"""
Ты — копирайтер для маркетплейсов. Напиши SEO-оптимизированное название товара длиной до 100 символов.

Товар: {product_name}
Бренд: {brand}
Категория: {category}
Особенности: {features}

{tone_inst}
{marketplace_inst}
{niche_inst}

Название должно включать бренд, тип товара, главную характеристику.
Только название, без лишних слов.
"""
        result = call_yandex_gpt(prompt)
        if result:
            return result.strip()
    return f"{brand} {product_name} - {category}"

def generate_descriptions(product_name, brand, features, price, tone="professional", marketplace="wildberries", niche="default"):
    if USE_YANDEX_GPT and YANDEX_API_KEY:
        tone_inst = get_tone_instruction(tone)
        marketplace_inst = get_marketplace_instruction(marketplace)
        niche_inst = get_niche_instruction(niche)
        prompt = f"""
Ты — копирайтер для маркетплейсов. Напиши 3 варианта описания товара (по 2-3 предложения).

Товар: {product_name}
Бренд: {brand}
Особенности: {features}
Цена: {price} ₽

{tone_inst}
{marketplace_inst}
{niche_inst}

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

def process_product(row, tone="professional", marketplace="wildberries", niche="default"):
    product_name = row.get('product_name', '')
    brand = row.get('brand', '')
    category = row.get('category', '')
    price = row.get('price', 0)
    color = row.get('color', '')
    features = row.get('features', '')

    descriptions = generate_descriptions(product_name, brand, features, price, tone, marketplace, niche)

    return {
        'generated_title': generate_title(product_name, brand, category, features, tone, marketplace, niche),
        'generated_description_1': descriptions[0] if len(descriptions) > 0 else "",
        'generated_description_2': descriptions[1] if len(descriptions) > 1 else "",
        'generated_description_3': descriptions[2] if len(descriptions) > 2 else "",
        'generated_keywords': generate_keywords(product_name, brand, category),
        'generated_specs': generate_specs(features, color)
    }