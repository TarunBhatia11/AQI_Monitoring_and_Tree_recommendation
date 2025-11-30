from coordinates import waqi_search
from coordinates import openweatherstations
from Tree_Recommendation import recommendTree, calculate_tree_pollutant
import os
import requests
from dotenv import load_dotenv
from time import sleep


load_dotenv()

def get_place_stations_with_pollutants(place, max_stations=30):
    """
    1. Use WAQI search to get station candidates for `place`
    2. For each station (with lat/lon) call OpenWeather for pollutant data
    3. For each station generate tree recommendations
    4. Return combined JSON structure
    """
    out = {
        "query": place,
        "waqi_search": None,
        "stations": []
    }
    
    # 1) WAQI search
    waqi_res = waqi_search.waqi_search_stations(place)
    out["waqi_search"] = waqi_res
    
    if waqi_res.get("status") != "ok":
        return out  # return error info
    
    stations = waqi_res.get("data", [])
    if len(stations) == 0:
        return out
    
    stations = stations[:max_stations]
    
    # 2) Loop through stations
    for st in stations:
        lat, lon = st.get("lat"), st.get("lon")
        
        station_entry = {
            "uid": st.get("uid"),
            "station_name": st.get("station_name"),
            "station_url": st.get("station_url"),
            "waqi_aqi": st.get("waqi_aqi"),
            "lat": lat,
            "lon": lon,
            "openweather_status": None,
            "openweather_pollutants": None,
            "tree_recommendations": []  # FIXED: added correct field
        }
        
        # 3) Get OpenWeather pollutants
        if lat is not None and lon is not None:
            ow = openweatherstations.openweather_pollutants(lat, lon)
            station_entry["openweather_status"] = ow.get("status")
            
            if ow.get("status") == "ok":
                pollutants = ow.get("data").get("pollutants", {})
                station_entry["openweather_pollutants"] = ow.get("data")
                
                # 4) Generate tree recommendations based on REAL pollutant data
                recommended = recommendTree.recommend_trees_from_dataset(pollutants)
                
                # 5) Add reduction calculations for 50, 100, 200 trees
                for tree_obj, score in recommended:
                    station_entry["tree_recommendations"].append({
                        "tree_name": tree_obj["Common_Name"],
                        "scientific_name": tree_obj["Scientific_Name"],
                        "canopy_density": tree_obj["Canopy_Density"],
                        "score": score,
                        "benefit_50":  calculate_tree_pollutant.calculate_tree_pollutant_reduction_fixed(pollutants, tree_obj, 50),
                        "benefit_100": calculate_tree_pollutant.calculate_tree_pollutant_reduction_fixed(pollutants, tree_obj, 100),
                        "benefit_200": calculate_tree_pollutant.calculate_tree_pollutant_reduction_fixed(pollutants, tree_obj, 200),
                    })
            
            else:
                station_entry["openweather_pollutants"] = {"error": ow.get("message")}
            
            sleep(float(os.getenv('API_SLEEP')))
        
        else:
            station_entry["openweather_status"] = "missing_coordinates"
        
        # 6) Store station
        out["stations"].append(station_entry)
    
    return out 