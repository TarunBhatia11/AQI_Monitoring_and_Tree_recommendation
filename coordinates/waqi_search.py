# CELL 2 - search WAQI for stations matching a keyword/place
import requests
import os
from dotenv import load_dotenv

load_dotenv()



def waqi_search_stations(keyword, token= os.getenv('WAQI_TOKEN')):
    """
    Uses WAQI Search API:
    GET https://api.waqi.info/search/?token={token}&keyword={keyword}
    Returns list of station dicts with at least: name, geo (lat, lon), uid, url, maybe aqi
    """
    base = "https://api.waqi.info/search/"
    params = {"token": token, "keyword": keyword}
    try:
        r = requests.get(base, params=params, timeout=10)
        data = r.json()
    except Exception as e:
        return {"status": "error", "message": f"WAQI search request failed: {e}"}
    
    if data.get("status") != "ok":
        return {"status": "error", "message": data.get("data", "unknown error from WAQI")}
    
    results = []
    for item in data.get("data", []):
        # typical returned structure (see WAQI docs / demo)
        station = item.get("station", {})
        geo = station.get("geo") or item.get("geo") or []
        lat = geo[0] if len(geo) > 0 else None
        lon = geo[1] if len(geo) > 1 else None
        results.append({
            "uid": item.get("uid"),
            "waqi_aqi": item.get("aqi"),
            "station_name": station.get("name") or item.get("station"),
            "station_url": station.get("url"),
            "lat": lat,
            "lon": lon
        })
    return {"status": "ok", "data": results}

