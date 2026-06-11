import json
import csv
import pickle
import urllib.request
import copy
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

class PrecipitationType(Enum):
    RAIN = "Дощ 🌧️"
    SNOW = "Сніг ❄️"
    CLEAR = "Ясно ☀️"

@dataclass
class WeatherRecord:
    date: datetime
    temperature: float
    precipitation: PrecipitationType

    def __str__(self):
        return f"{self.date.strftime('%d.%m.%Y %H:%M')} | {self.temperature}°C | {self.precipitation.value}"

    def __repr__(self):
        return f"WeatherRecord({self.date}, {self.temperature}, {self.precipitation.name})"

    def __lt__(self, other):
        if not isinstance(other, WeatherRecord):
            return NotImplemented
        return self.temperature < other.temperature

class Report:
    def __init__(self, title: str):
        self.title = title
        self.records = []

    def generate_info(self) -> str:
        raise NotImplementedError

class DailyForecast(Report):
    def __init__(self, title: str, confidence: int = 100):
        super().__init__(title)
        self.confidence = confidence 

    @property
    def confidence(self):
        return self._confidence

    @confidence.setter
    def confidence(self, value):
        if not (0 <= value <= 100):
            raise ValueError("Впевненість прогнозу має бути від 0 до 100%")
        self._confidence = value

    def generate_info(self) -> str:
        return f"📈 Щоденний звіт '{self.title}' (точність: {self.confidence}%)"

class MonthlyReport(Report):
    def generate_info(self) -> str:
        return f"📊 Місячний звіт '{self.title}' (проаналізовано записів: {len(self.records)})"

class SeasonIterator:
    def __init__(self, records, target_months: list):
        self._records = [r for r in records if r.date.month in target_months]
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self._records):
            item = self._records[self.index]
            self.index += 1
            return item
        raise StopIteration

class SatelliteConnection:
    def __init__(self, station):
        self.station = station

    def __enter__(self):
        print("\n[System] 📡 Встановлення безпечного з'єднання з супутником...")
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        print("[System] 📡 З'єднання закрито. Ресурси звільнено.")
        if exc_type:
            print(f"[Увага] Збій транзакції: {exc_val}")
        return True 

# ===  Менеджер контексту для РЕДАГУВАННЯ  ===
class RecordEditor:
    def __init__(self, station, index):
        self.station = station
        self.index = index
        self.original_record = None

    def __enter__(self):
        # Робимо копію запису. Якщо під час редагування буде помилка, ми повернемо цю копію.
        self.original_record = copy.deepcopy(self.station._records[self.index])
        return self.station._records[self.index]

    def __exit__(self, exc_type, exc_val, traceback):
        if exc_type is not None:
            # Сталася помилка! Відкочуємо зміни назад (Rollback)
            print(f"\n[System] ❌ Помилка введення ({exc_val}). Відкат змін...")
            self.station._records[self.index] = self.original_record
        else:
            print("\n[System] ✅ Запис успішно оновлено (Транзакцію завершено).")
        return True 

class MeteoStation:
    def __init__(self):
        self._records = []
        self.config = {"app_name": "MeteoAnalyzer", "version": "1.0"}

    def __getitem__(self, index):
        return self._records[index]

    def get_season_iterator(self, season_months: list):
        return SeasonIterator(self._records, season_months)

    def load_config(self, filepath="config.json"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            pass

    def save_config(self, filepath="config.json"):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
        print("[System] ⚙️ Налаштування застосунку збережено у JSON.")

    def save_system_state(self, filepath="meteo_backup.pkl"):
        with open(filepath, 'wb') as f:
            pickle.dump(self._records, f)
        print("[System] 💾 Стан системи законсервовано (pickle).")

    def load_system_state(self, filepath="meteo_backup.pkl"):
        try:
            with open(filepath, 'rb') as f:
                self._records = pickle.load(f)
        except FileNotFoundError:
            pass

    def import_from_csv(self, filepath="test_weather.csv"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader) 
                count = 0
                for row in reader:
                    date_obj = datetime.strptime(row[0], "%Y-%m-%d")
                    temp = float(row[1])
                    precip = PrecipitationType[row[2]]
                    self.add_record(WeatherRecord(date_obj, temp, precip))
                    count += 1
                print(f"[System] 📥 Успішно імпортовано {count} записів із CSV.")
        except FileNotFoundError:
            print(f"[System] ⚠️ Файл {filepath} не знайдено.")
        except Exception as e:
            print(f"[System] ❌ Помилка імпорту: {e}")

    def export_csv_report(self, filepath="weather_export.csv"):
        with open(filepath, 'w', newline='', encoding='utf-16') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(['Дата', 'Температура (°C)', 'Опади'])
            for r in sorted(self._records): 
                writer.writerow([r.date.strftime("%d.%m.%Y"), r.temperature, r.precipitation.name])
        print(f"[System] 📊 Звіт успішно експортовано у {filepath}")

    def add_record(self, record: WeatherRecord):
        self._records.append(record)

    def get_all_records(self):
        return self._records

    def fetch_live_weather(self, lat=49.2328, lon=28.481):
        with SatelliteConnection(self): 
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            req = urllib.request.urlopen(url)
            data = json.loads(req.read())
            temp = data["current_weather"]["temperature"]
            code = data["current_weather"]["weathercode"]
            
            if code in [71, 73, 75, 77, 85, 86]: precip = PrecipitationType.SNOW
            elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: precip = PrecipitationType.RAIN
            else: precip = PrecipitationType.CLEAR
                
            record = WeatherRecord(datetime.now(), temp, precip)
            self.add_record(record)
            return record