import pandas as pd

# Пример данных для теста
data = {
    'product_name': [
        'Наушники JBL Tune 510BT',
        'Смартфон Xiaomi Redmi Note 12',
        'Чехол для iPhone 15 Pro'
    ],
    'brand': ['JBL', 'Xiaomi', 'Apple'],
    'category': ['Аудио', 'Смартфоны', 'Аксессуары'],
    'price': [3500, 25000, 1500],
    'color': ['чёрный', 'синий', 'прозрачный'],
    'features': [
        'Bluetooth 5.0, 40 часов работы, быстрая зарядка',
        '6.67 дюймов, 128 ГБ, камера 50 МП',
        'прозрачный, ударопрочный, MagSafe совместимый'
    ],
    'keywords': [
        'беспроводные наушники, jbl tune, наушники с bluetooth',
        'xiaomi redmi note 12, смартфон сяоми, бюджетный смартфон',
        'чехол iphone 15, magsafe чехол, прозрачный чехол'
    ]
}

df = pd.DataFrame(data)
df.to_excel('products.xlsx', index=False)
print("✅ Файл products.xlsx создан с тестовыми товарами!")