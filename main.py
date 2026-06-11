import sys
from datetime import datetime
from meteo_core import MeteoStation, WeatherRecord, PrecipitationType, DailyForecast, MonthlyReport, RecordEditor

def show_menu():
    print("\n" + "="*50)
    print(" 🌍 УНІВЕРСАЛЬНИЙ МЕТЕОАНАЛІЗАТОР v1.0")
    print("="*50)
    print("1. 📋 Показати архів (СОРТУВАННЯ за температурою)")
    print("2. 🔍 ПОШУК та ФІЛЬТРАЦІЯ записів")
    print("3. ✏️ РЕДАГУВАННЯ запису (безпечно через 'with')")
    print("4. ➕ Додати запис вручну")
    print("5. 📡 Отримати реальну погоду (через API)")
    print("6. 💾 Імпорт / Експорт даних (CSV)")
    print("7. 📊 Згенерувати ООП-звіти")
    print("8. ⚙️ Зберегти стан (Pickle) та конфіг (JSON)")
    print("0. Зберегти та вийти")
    print("="*50)

def main():
    station = MeteoStation()
    station.load_config()
    station.load_system_state()
    
    while True:
        show_menu()
        try:
            choice = input("Оберіть дію (0-8): ").strip()
            
            match choice:
                case "1":
                    records = station.get_all_records()
                    if not records:
                        print("\n[Info] База даних порожня.")
                    else:
                        print("\n--- Архів записів (ВІДСОРТОВАНО від найхолоднішого) ---")
                        # Демонстрація СОРТУВАННЯ
                        for i, r in enumerate(sorted(records)): 
                            print(f"[{i}] {r}")
                            
                case "2":
                    print("\n--- 🔍 ПОШУК ТА ФІЛЬТРАЦІЯ ---")
                    print("1 - Знайти за датою (Пошук)")
                    print("2 - Показати літні записи (Фільтрація)")
                    sub = input("Оберіть: ").strip()
                    if sub == "1":
                        d_str = input("Введіть дату (ДД.ММ.РРРР): ").strip()
                        found = False
                        for i, r in enumerate(station.get_all_records()):
                            if r.date.strftime("%d.%m.%Y") == d_str:
                                print(f"Знайдено: Індекс [{i}] -> {r}")
                                found = True
                        if not found: print("Записів не знайдено.")
                    elif sub == "2":
                        print("☀️ Літні записи (Фільтрація через ітератор):")
                        found = False
                        for r in station.get_season_iterator([6, 7, 8]):
                            print(f" -> {r}")
                            found = True
                        if not found: print("Літніх записів немає.")
                        
                case "3":
                    print("\n--- ✏️ РЕДАГУВАННЯ (Транзакція 'with') ---")
                    records = station.get_all_records()
                    if not records:
                        print("База порожня. Спочатку додайте дані.")
                        continue
                        
                    idx_str = input("Введіть індекс запису для редагування (наприклад, 0): ").strip()
                    idx = int(idx_str)
                    if 0 <= idx < len(records):
                        # ВИКОРИСТАННЯ WITH ДЛЯ РЕДАГУВАННЯ
                        with RecordEditor(station, idx) as record:
                            print(f"Поточний стан: {record}")
                            val = input("Введіть нову температуру (введіть текст, щоб перевірити відкат помилки): ")
                            record.temperature = float(val) 
                    else:
                        print("Невірний індекс.")

                case "4":
                    print("\n--- Додавання запису ---")
                    temp = float(input("Введіть температуру (°C): "))
                    print("Типи опадів: 1 - Ясно, 2 - Дощ, 3 - Сніг")
                    p_choice = input("Оберіть тип (1-3): ").strip()
                    if p_choice == "1": precip = PrecipitationType.CLEAR
                    elif p_choice == "2": precip = PrecipitationType.RAIN
                    elif p_choice == "3": precip = PrecipitationType.SNOW
                    else: raise ValueError("Невідомий тип опадів!")
                    record = WeatherRecord(datetime.now(), temp, precip)
                    station.add_record(record)
                    print(f"\n[Success] Запис додано: {record}")
                    
                case "5":
                    print("\n--- 📡 Отримання реальної погоди ---")
                    lat_str = input("Широта (наприклад 49.23, або Enter для Вінниці): ").strip()
                    lon_str = input("Довгота (наприклад 28.48, або Enter): ").strip()
                    lat = float(lat_str) if lat_str else 49.2328
                    lon = float(lon_str) if lon_str else 28.481
                    record = station.fetch_live_weather(lat, lon)
                    print(f"[Success] Завантажено: {record}")
                    
                case "6":
                    print("\n1 - Імпорт з CSV\n2 - Експорт у CSV")
                    sub = input("Оберіть: ").strip()
                    if sub == "1": station.import_from_csv("test_weather.csv")
                    elif sub == "2": station.export_csv_report()
                    
                case "7":
                    print("\n--- Демонстрація ООП (Звіти) ---")
                    daily = DailyForecast("Прогноз на сьогодні", confidence=95)
                    monthly = MonthlyReport("Статистика за місяць")
                    monthly.records = station.get_all_records()
                    print(daily.generate_info())
                    print(monthly.generate_info())
                    
                case "8":
                    print()
                    station.save_system_state()
                    station.save_config()
                    
                case "0":
                    station.save_system_state()
                    station.save_config()
                    print("Завершення роботи. Безхмарного неба! ☀️")
                    sys.exit(0)
                    
                case _:
                    print("\n[Warning] Невідома команда! Оберіть пункт від 0 до 8.")
                    
        except ValueError as e:
            print(f"\n❌ [Помилка валідації]: {e}")
        except Exception as e:
            print(f"\n🛑 [Критична помилка]: {e}")

if __name__ == "__main__":
    main()