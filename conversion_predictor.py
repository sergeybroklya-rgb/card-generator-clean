import re
from typing import Dict, List, Tuple

# Слова-убийцы конверсии (снижают оценку)
KILLER_WORDS = {
    "дешёвый": -5, "дешевый": -5, "китай": -8, "аналог": -5,
    "копия": -10, "реплика": -8, "не оригинал": -10, "б/у": -15,
    "дешевле": -3, "скидка": 0  # не штрафуем за скидку
}

# Слова-якоря (повышают оценку)
BOOSTER_WORDS = {
    "гарантия": +8, "оригинал": +10, "сертификат": +7,
    "бесплатно": +5, "доставка": +3, "скидка": +5,
    "акция": +4, "хит": +3, "топ": +3
}

# Нишевые бенчмарки (усреднённые данные)
NICHE_BENCHMARKS = {
    "sneakers": {
        "avg_price": 4500,
        "avg_conversion": 7.2,
        "min_title_len": 60,
        "max_title_len": 120,
        "min_description_len": 400
    },
    "kettles": {
        "avg_price": 2500,
        "avg_conversion": 5.8,
        "min_title_len": 50,
        "max_title_len": 100,
        "min_description_len": 300
    },
    "toys": {
        "avg_price": 1200,
        "avg_conversion": 6.5,
        "min_title_len": 50,
        "max_title_len": 110,
        "min_description_len": 350
    },
    "smartphones": {
        "avg_price": 25000,
        "avg_conversion": 4.2,
        "min_title_len": 70,
        "max_title_len": 130,
        "min_description_len": 500
    },
    "headphones": {
        "avg_price": 3500,
        "avg_conversion": 6.8,
        "min_title_len": 60,
        "max_title_len": 120,
        "min_description_len": 400
    }
}

def analyze_text(text: str) -> Tuple[int, List[str], List[str]]:
    """Анализирует текст, возвращает балл, найденные убийцы и усилители"""
    text_lower = text.lower()
    killers_found = []
    boosters_found = []
    score = 0
    
    for word, points in KILLER_WORDS.items():
        if word in text_lower:
            killers_found.append(word)
            score += points
    
    for word, points in BOOSTER_WORDS.items():
        if word in text_lower:
            boosters_found.append(word)
            score += points
    
    return score, killers_found, boosters_found

def check_length(title: str, description: str, niche: str) -> Tuple[int, List[str]]:
    """Проверяет длину полей и возвращает штрафы/бонусы"""
    score = 0
    tips = []
    benchmark = NICHE_BENCHMARKS.get(niche, NICHE_BENCHMARKS["sneakers"])
    
    title_len = len(title)
    if title_len < benchmark["min_title_len"]:
        score -= 8
        tips.append(f"⚠️ Название слишком короткое ({title_len} символов). Добавьте характеристики")
    elif title_len > benchmark["max_title_len"]:
        score -= 5
        tips.append(f"⚠️ Название слишком длинное ({title_len} символов). Сократите до 120 символов")
    else:
        score += 5
        tips.append(f"✅ Длина названия оптимальна ({title_len} символов)")
    
    desc_len = len(description)
    if desc_len < benchmark["min_description_len"]:
        score -= 10
        tips.append(f"⚠️ Описание слишком короткое ({desc_len} символов). Раскройте характеристики подробнее")
    else:
        score += 8
        tips.append(f"✅ Длина описания хорошая ({desc_len} символов)")
    
    return score, tips

def compare_price(price: float, niche: str) -> Tuple[int, List[str]]:
    """Сравнивает цену с бенчмарком"""
    score = 0
    tips = []
    benchmark = NICHE_BENCHMARKS.get(niche, NICHE_BENCHMARKS["sneakers"])
    
    if price < benchmark["avg_price"] * 0.8:
        score += 15
        tips.append(f"✅ Цена ниже среднего по категории. Хорошее преимущество")
    elif price > benchmark["avg_price"] * 1.2:
        score -= 10
        tips.append(f"⚠️ Цена выше среднего. Добавьте больше преимуществ в описание")
    else:
        score += 5
        tips.append(f"✅ Цена в среднем диапазоне")
    
    return score, tips

def predict_conversion(title: str, description: str, price: float, niche: str = "sneakers") -> Dict:
    """
    Главная функция прогнозирования конверсии
    
    Returns:
        Dict с оценкой, списком рекомендаций и факторами успеха
    """
    # 1. Анализ текста (слова-убийцы и усилители)
    text_score, killers, boosters = analyze_text(f"{title} {description}")
    
    # 2. Проверка длины
    length_score, length_tips = check_length(title, description, niche)
    
    # 3. Сравнение цены
    price_score, price_tips = compare_price(price, niche)
    
    # 4. Базовая оценка (стартуем с 50)
    base_score = 50
    
    # 5. Итоговая оценка (ограничиваем 0-100)
    total_score = base_score + text_score + length_score + price_score
    total_score = max(0, min(100, total_score))
    
    # 6. Собираем рекомендации
    recommendations = []
    
    if killers:
        recommendations.append(f"❌ Избегайте слов: {', '.join(killers)} (снижают доверие)")
    
    if boosters:
        recommendations.append(f"✅ Хорошо: используйте слова {', '.join(boosters)}")
    
    recommendations.extend(length_tips)
    recommendations.extend(price_tips)
    
    # 7. Определяем уровень конверсии
    if total_score >= 80:
        level = "🟢 Высокая"
        level_desc = "Карточка хорошо оптимизирована. Отличная работа!"
    elif total_score >= 60:
        level = "🟡 Средняя"
        level_desc = "Карточка неплохая, но есть потенциал для улучшения"
    else:
        level = "🔴 Низкая"
        level_desc = "Карточка требует доработки. Внесите изменения по рекомендациям"
    
    return {
        "score": total_score,
        "level": level,
        "level_desc": level_desc,
        "recommendations": recommendations[:5],  # топ-5 рекомендаций
        "details": {
            "killers": killers,
            "boosters": boosters,
            "price_comparison": f"Цена {price}₽",
            "title_len": len(title),
            "description_len": len(description)
        }
    }

# Пример использования
if __name__ == "__main__":
    test_title = "Наушники JBL Tune 510BT беспроводные с Bluetooth"
    test_desc = "Отличные наушники с хорошим звуком и долгой батареей. Гарантия 1 год."
    result = predict_conversion(test_title, test_desc, 3500, "headphones")
    print(f"Оценка: {result['score']}/100 - {result['level']}")
    print(f"Уровень: {result['level_desc']}")
    print("Рекомендации:")
    for rec in result["recommendations"]:
        print(f"  {rec}")