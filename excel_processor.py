import pandas as pd
from card_generator import process_product

def process_products(input_file: str, output_file: str = None) -> str:
    """
    Обрабатывает Excel файл с товарами и генерирует карточки
    """
    print(f"📖 Читаю файл: {input_file}")
    df = pd.read_excel(input_file)
    
    # Проверяем наличие обязательных колонок
    required_cols = ['product_name', 'brand', 'category', 'price']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Отсутствуют колонки: {missing_cols}")
    
    # Добавляем колонки для результатов
    new_cols = [
        'generated_title', 'generated_description_1', 'generated_description_2',
        'generated_description_3', 'generated_keywords', 'generated_specs'
    ]
    for col in new_cols:
        df[col] = ""
    
    # Обрабатываем каждый товар
    total = len(df)
    for idx, row in df.iterrows():
        # Преобразуем строку в словарь
        row_dict = row.to_dict()
        result = process_product(row_dict)
        
        for col, value in result.items():
            df.at[idx, col] = value
        
        if (idx + 1) % 10 == 0:
            print(f"   Обработано {idx + 1} из {total}...")
    
    # Сохраняем результат
    if output_file is None:
        output_file = input_file.replace('.xlsx', '_cards.xlsx')
    
    df.to_excel(output_file, index=False)
    print(f"✅ Готово! Результат сохранён в: {output_file}")
    print(f"📊 Обработано товаров: {total}")
    
    return output_file

if __name__ == "__main__":
    process_products("products.xlsx")