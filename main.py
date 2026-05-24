import sys
from excel_processor import process_products

def main():
    print("=" * 50)
    print("📦 ГЕНЕРАТОР КАРТОЧЕК ТОВАРОВ ДЛЯ МАРКЕТПЛЕЙСОВ")
    print("=" * 50)
    print("Поддерживаемые колонки в Excel: product_name, brand, category, price, color, features")
    print("")
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("📁 Введите путь к Excel файлу с товарами: ").strip()
    
    if not input_file:
        print("❌ Файл не указан")
        return
    
    try:
        output_file = process_products(input_file)
        print(f"\n💾 Результат сохранён: {output_file}")
        print("\n📋 Как использовать:")
        print("1. Откройте полученный Excel файл")
        print("2. Скопируйте сгенерированные названия и описания")
        print("3. Вставьте в карточки товаров на маркетплейсе")
        print("\n🚀 Готово! Карточки сгенерированы.")
    except FileNotFoundError:
        print(f"❌ Файл не найден: {input_file}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()