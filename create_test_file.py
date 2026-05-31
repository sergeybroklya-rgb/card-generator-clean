import pandas as pd

data = {
    'product_name': [
        'Наушники',
        'Наушники JBL Tune 510BT',
        'Беспроводные наушники JBL Tune 510BT с шумоподавлением и гарантией 1 год'
    ],
    'brand': ['Noname', 'JBL', 'JBL'],
    'category': ['Аудио', 'Аудио', 'Аудио'],
    'price': [5000, 3500, 3500],
    'color': ['чёрный', 'чёрный', 'чёрный'],
    'features': [
        'нет',
        'Bluetooth, 40 часов работы',
        'Bluetooth 5.0, 40 часов работы, быстрая зарядка, гарантия 1 год, оригинал'
    ]
}

df = pd.DataFrame(data)
df.to_excel('test_products.xlsx', index=False)
print("✅ Файл test_products.xlsx создан!")