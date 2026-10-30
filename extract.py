import requests
import json
import logging
import sys
from datetime import datetime, UTC
from pathlib import Path

logger = logging.getLogger(__name__)

def fetch_weather(lat, long):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude" : lat,
        "longitude" : long,
        "hourly" : "temperature_2m",    
    }
    response = requests.get(url, params=params, timeout=10)
    try:
        response.raise_for_status()
        data = response.json()
        return data
    except(requests.exceptions.RequestException) as e:
        logger.error(f"Failed to fetch weather data: {e} - {response.text}")
        raise

def save_raw(data, date_str):
    path = Path("data")
    path.mkdir(exist_ok=True)
    file = path / f"weather_{date_str}.json"
    logger.info(f"Saving data to {file}")
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return file 
    except IOError as e:
        logger.error(f"Failed to write data to {file}: {e}")
        raise
    
def main():
    now = datetime.now(UTC)
    today = now.strftime("%Y-%m-%d")
    weather = fetch_weather(52.52, 13.41)
    path = save_raw(weather, today)
    logger.info(f"file saved at : {path}")
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    try:
        main()
    except Exception:
        logger.exception("Pipeline failed to run successfully")
        sys.exit(1)





