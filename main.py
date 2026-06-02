import sys
from datetime import datetime
from meteo_core import MeteoStation, WeatherRecord, PrecipitationType, DailyForecast, MonthlyReport

def show_menu():
    print("\n" + "="*45)
    print(" 🌍 УНІВЕРСАЛЬНИЙ МЕТЕОАНАЛІЗАТОР v1.0")
    print("="*45)
    print("1. Показати всі метеозаписи")
    print("2. Додати запис вручну")
    print("3. 📡 Отримати реальну погоду (через API)")
    print("4. 📥 Імпортувати дані з CSV (Вимога вар. 20)")
    print("5. 📤 Експортувати звіт у CSV (Загальна вимога)")
    print("6. 📊 Згенерувати звіти (ООП) та показати Сезони")
    print("7. Зберегти стан (Pickle) та конфігурацію (JSON)")
    print("0. Зберегти та вийти")
    print("="*45)

def main():
    station = MeteoStation()
    station.load_config()
    station.load_system_state()
    
    while True:
        show_menu()
        try:
            choice = input("Оберіть дію (0-6): ").strip()
            
            match choice:
                case "1":
                    records = station.get_all_records()
                    if not records:
                        print("\n[Info] База даних порожня.")
                    else:
                        print("\n--- Архів записів (відсортовано) ---")
                        for r in sorted(records): # Демонстрація магічного методу __lt__
                            print(r)
                            
                case "2":
                    print("\n--- Додавання запису ---")
                    temp_str = input("Введіть температуру (°C): ")
                    if not temp_str:
                        raise ValueError("Температура не може бути порожньою!")
                    temp = float(temp_str) 
                    
                    print("Типи опадів: 1 - Ясно, 2 - Дощ, 3 - Сніг")
                    p_choice = input("Оберіть тип (1-3): ").strip()
                    if p_choice == "1": precip = PrecipitationType.CLEAR
                    elif p_choice == "2": precip = PrecipitationType.RAIN
                    elif p_choice == "3": precip = PrecipitationType.SNOW
                    else:
                        raise ValueError("Невідомий тип опадів! Введіть 1, 2 або 3.")
                        
                    record = WeatherRecord(datetime.now(), temp, precip)
                    station.add_record(record)
                    print(f"\n[Success] Запис додано: {record}")
                    
                case "3":
                    print("\n--- 📡 Отримання реальної погоди ---")
                    lat_str = input("Введіть широту (наприклад, 49.23, або Enter для Вінниці): ").strip()
                    lon_str = input("Введіть довготу (наприклад, 28.48, або Enter): ").strip()
                    lat = float(lat_str) if lat_str else 49.2328
                    lon = float(lon_str) if lon_str else 28.481
                    record = station.fetch_live_weather(lat, lon)
                    print(f"[Success] Завантажено реальні дані: {record}")
                    
                case "4":
                    print("\n--- Імпорт з CSV ---")
                    # Програма спробує знайти файл test_weather.csv
                    station.import_from_csv("test_weather.csv")
                    
                case "5":
                    print("\n--- Експорт у CSV ---")
                    station.export_csv_report()
                    
                case "6":
                    print("\n--- Демонстрація ООП (Звіти та Ітератори) ---")
                    daily = DailyForecast("Прогноз на сьогодні", confidence=95)
                    monthly = MonthlyReport("Статистика за поточний місяць")
                    monthly.records = station.get_all_records()
                    print(daily.generate_info())
                    print(monthly.generate_info())
                    
                    print("\n☀️ Літні записи в базі:")
                    summer_iterator = station.get_season_iterator([6, 7, 8])
                    found = False
                    for rec in summer_iterator:
                        print(f" -> {rec}")
                        found = True
                    if not found:
                        print(" -> Літніх записів поки немає.")
                        
                case "7":
                    print()
                    station.save_system_state()
                    station.save_config()
                    
                case "0":
                    print("\n[Info] Автозбереження перед виходом...")
                    station.save_system_state()
                    station.save_config()
                    print("Завершення роботи. Безхмарного неба! ☀️")
                    sys.exit(0)
                    
                case _:
                    print("\n[Warning] Невідома команда! Оберіть пункт від 0 до 7.")
        except ValueError as e:
            print(f"\n❌ [Помилка валідації]: {e}")
        except Exception as e:
            print(f"\n🛑 [Критична помилка]: {e}")

if __name__ == "__main__":
    main()