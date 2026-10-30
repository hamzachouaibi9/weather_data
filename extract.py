import requests
import json
from datetime import datetime
from pathlib import Path

def fetch_weather(lat, long):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude" : lat,
        "longitude" : long,
        "hourly" : "temperature_2m",    
    }
    response = requests.get(url, params=params)
    print(response.url)
    response.raise_for_status()
    data = response.json()
    return data

def save_raw(data, date_str):
    path = Path("data")
    path.mkdir(exist_ok=True)
    file = path / f"weather_{date_str}.json"
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return file

def main():
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    weather = fetch_weather(52.52, 13.41)
    path = save_raw(weather, today)
    return print(f"file saved at : {path}")
        
if __name__ == "__main__":
    main()





