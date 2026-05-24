import pandas as pd

# Простые и понятные товары для теста
data = {
    'product_name': [
        'Кроссовки Nike Air Max',
        'Ноутбук Apple MacBook Air',
        'Кофеварка DeLonghi'
    ],
    'brand': [
        'Nike',
        'Apple',
        'DeLonghi'
    ],
    'category': [
        'Обувь',
        'Электроника',
        'Техника для дома'
    ],
    'price': [
        12000,
        95000,
        15000
    ],
    'color': [
        'белый',
        'серый',
        'чёрный'
    ],
    'features': [
        'легкие, амортизация, дышащая сетка',
        '8GB RAM, 256GB SSD, Retina дисплей',
        'капельная, 1.5 литра, автоотключение'
    ]
}

df = pd.DataFrame(data)
df.to_excel('test_products.xlsx', index=False)
print("✅ Файл test_products.xlsx создан!")
print("\n📋 Товары для теста:")
for i, row in df.iterrows():
    print(f"   {i+1}. {row['product_name']} - {row['price']} ₽")