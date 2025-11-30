# CELL 3 - OpenWeather Air Pollution for coordinates
import requests
import os 
from dotenv import load_dotenv
from calculate_AQI import calculateAQI


load_dotenv()

def openweather_pollutants(lat, lon, apikey= os.getenv('OPENWEATHER_KEY')):
    """
    Calls OpenWeather Air Pollution API:
    GET http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={key}
    Returns dict with 'aqi' and 'components' if present
    """
    base = "http://api.openweathermap.org/data/2.5/air_pollution"
    params = {"lat": lat, "lon": lon, "appid": apikey}
    try:
        r = requests.get(base, params=params, timeout=10)
        data = r.json()
    except Exception as e:
        return {"status": "error", "message": f"OpenWeather request failed: {e}"}
    
    if "list" not in data or len(data["list"]) == 0:
        return {"status": "error", "message": "No air pollution data returned"}
    
    entry = data["list"][0]
    # map components safely (some fields might be missing)
    components = entry.get("components", {})

    calculate_aqi = calculateAQI.calculate_aqi_using_formula(components)

    pollutants = {
        "co": components.get("co"),
        "no2": components.get("no2"),
        "o3": components.get("o3"),
        "so2": components.get("so2"),
        "pm2_5": components.get("pm2_5"),
        "pm10": components.get("pm10"),
        "AQI": calculate_aqi
    }
    return {"status": "ok", "data": {"ow_aqi": entry.get("main", {}).get("aqi"), "pollutants": pollutants}}
