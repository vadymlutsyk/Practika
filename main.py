import json
import os
import sys

# Назва файлу для збереження даних між сесіями
DATA_FILE = "passwords.json"

def load_data():
    """Завантажує дані з JSON файлу. Обробляє винятки, якщо файл пошкоджено."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, PermissionError):
        print("\n[Помилка] Файл даних пошкоджено або відсутній доступ. Створено нову базу.")
        return {}

def save_data(data):
    """Безпечно зберігає дані у JSON файл."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except IOError:
        print("\n[Помилка] Не вдалося зберегти дані на диск.")

def mask_password(password):
    """Маскує пароль, залишаючи видимими лише перші та останні символи, якщо він довгий."""
    if len(password) <= 4:
        return "****"
    return f"{password[:2]}...{password[-2:]}"

def add_record(data):
    """Функція 1: Додавання запису (сервіс, логін, пароль)"""
    print("\n--- ДОДАВАННЯ НОВОГО ЗАПИСУ ---")
    
    # Валідація назви сервісу (запобігання порожнім рядкам)
    service = input("Введіть назву сервісу (напр., GitHub, Gmail): ").strip()
    if not service:
        print("[Помилка] Назва сервісу не може бути порожньою!")
        return

    # Перевірка на дублікати (реєстронезалежна)
    service_key = service.lower()
    if service_key in data:
        overwrite = input(f"Сервіс '{service}' вже існує. Оновити дані? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Операцію скасовано.")
            return

    login = input("Введіть логін/email: ").strip()
    if not login:
        print("[Помилка] Логін не може бути порожнім!")
        return

    password = input("Введіть пароль: ").strip()
    if not password:
        print("[Помилка] Пароль не може бути порожнім!")
        return

    # Зберігаємо оригінальну назву для відображення, але ключ залишаємо в нижньому регістрі
    data[service_key] = {
        "display_name": service,
        "login": login,
        "password": password
    }
    save_data(data)
    print(f"[Успіх] Запис для сервісу '{service}' успішно збережено!")

def view_all_records(data):
    """Функція 2: Перегляд усіх записів із маскуванням пароля за замовчуванням"""
    print("\n--- СПИСОК ЗБЕРЕЖЕНИХ СЕРВІСІВ ---")
    if not data:
        print("Ваш менеджер паролів порожній.")
        return

    print(f"{'№':<4} | {'Сервіс':<20} | {'Логін':<25} | {'Пароль (Маскований)':<15}")
    print("-" * 72)
    
    for idx, (key, item) in enumerate(data.items(), 1):
        masked = mask_password(item["password"])
        print(f"{idx:<4} | {item['display_name']:<20} | {item['login']:<25} | {masked:<15}")

def search_record(data):
    """Функція 3: Пошук за сервісом з можливістю відкрити пароль"""
    print("\n--- ПОШУК ЗАПИСУ ---")
    if not data:
        print("База даних порожня. Немає де шукати.")
        return

    search_query = input("Введіть назву сервісу для пошуку: ").strip().lower()
    
    if search_query in data:
        item = data[search_query]
        print(f"\nЗнайдено запис для '{item['display_name']}':")
        print(f"  Логін:  {item['login']}")
        print(f"  Пароль: {mask_password(item['password'])}")
        
        # Додаткова зручність: запит на показ реального пароля
        reveal = input("\nПоказати пароль повністю? (y/n): ").strip().lower()
        if reveal == 'y':
            print(f"  [РЕАЛЬНИЙ ПАРОЛЬ]: {item['password']}")
    else:
        print(f"[Повідомлення] Запис для сервісу '{search_query}' не знайдено.")

def delete_record(data):
    """Функція 4: Видалення запису за назвою сервісу"""
    print("\n--- ВИДАЛЕННЯ ЗАПИСУ ---")
    if not data:
        print("База даних порожня. Нічого видаляти.")
        return

    target_service = input("Введіть назву сервісу, який потрібно видалити: ").strip().lower()
    
    if target_service in data:
        confirm = input(f"Ви впевнені, що хочете видалити запис '{data[target_service]['display_name']}'? (y/n): ").strip().lower()
        if confirm == 'y':
            del data[target_service]
            save_data(data)
            print("[Успіх] Запис успішно видалено з бази.")
        else:
            print("Видалення скасовано.")
    else:
        print(f"[Помилка] Сервіс '{target_service}' не знайдено в базі.")

def main():
    """Головний цикл програми. Забезпечує стійкість до некоректного вводу."""
    data = load_data()
    
    while True:
        print("\n========================================")
        print("  CLI МЕНЕДЖЕР ПАРОЛІВ (Варіант 13)")
        print("========================================")
        print("1. Додати новий запис")
        print("2. Переглянути всі записи (масковані)")
        print("3. Пошук запису за сервісом (+ демаскування)")
        print("4. Видалити запис")
        print("5. Вихід")
        print("----------------------------------------")
        
        choice = input("Оберіть дію (1-5): ").strip()
        
        # Обробка некоректного вводу без аварійного завершення
        if choice == "1":
            add_record(data)
        elif choice == "2":
            view_all_records(data)
        elif choice == "3":
            search_record(data)
        elif choice == "4":
            delete_record(data)
        elif choice == "5":
            print("\nДякуємо за використання Менеджера паролів. До побачення!")
            sys.exit(0)
        else:
            print("\n[Некоректний ввід] Будь ласка, введіть число від 1 до 5.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Обробка раптового закриття через Ctrl+C
        print("\n\nПрограму примусово завершено користувачем. Дані збережено.")
        sys.exit(0)
