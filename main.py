# from coordinates import waqi_search
# import json
# from AQI_Data import aqi_data_place
# from flask import Flask, render_template, request, jsonify
# import traceback
# from Tree_Recommendation import calculate_tree_pollutant
# from math import fabs
# import pandas as pd

# # location = input('Enter Location')

# # result = aqi_data_place.get_place_stations_with_pollutants(location)

# # print(json.dumps(result, indent=2, ensure_ascii= False))


# app = Flask(__name__, static_folder="static", template_folder="templates")


# def normalize_station_raw(s):
#     """
#     Convert a raw station dict into a normalized metadata dict used by frontend.
#     Ensures keys exist and pollutants is a dict.
#     """
#     # station name
#     name = s.get("station_name") or s.get("station") or s.get("stationName") or "Unknown Station"

#     # coordinates (support multiple possible keys)
#     lat = s.get("lat") or s.get("latitude") or s.get("Lat") or None
#     lon = s.get("lon") or s.get("longitude") or s.get("Lon") or None

#     # AQI value: prefer waqi_aqi then aqi
#     aqi = s.get("waqi_aqi") or s.get("aqi") or s.get("AQI") or "N/A"

#     # pollutant object may be nested in openweather_pollutants.pollutants
#     pollutants = {}
#     if "pollutants" in s and isinstance(s.get("pollutants"), dict):
#         pollutants = s.get("pollutants")
#     elif s.get("openweather_pollutants") and isinstance(s.get("openweather_pollutants"), dict):
#         pollutants = s["openweather_pollutants"].get("pollutants", {}) or {}
#     elif s.get("openweather") and isinstance(s.get("openweather"), dict):
#         pollutants = s["openweather"].get("pollutants", {}) or {}

#     # Ensure pollutants is a dict (safety)
#     if not isinstance(pollutants, dict):
#         pollutants = {}

#     return {
#         "station_name": name,
#         "lat": lat,
#         "lon": lon,
#         "aqi": aqi,
#         "pollutants": pollutants
#     }


# @app.route("/")
# def index():
#     return render_template("index.html")


# @app.route("/api/search")
# def api_search():
#     """
#     GET /api/search?q=Kanpur
#     Returns JSON with normalized station metadata:
#     { "query": "...", "stations": [ {station_name, lat, lon, aqi, pollutants}, ... ] }
#     """
#     q = request.args.get("q", "").strip()

#     if not q:
#         return jsonify({"error": "Missing query parameter 'q'"}), 400

#     try:
#         # Use your existing function — it may return a dict with "stations"
#         raw = aqi_data_place.get_place_stations_with_pollutants(q)

#         # If your function returns a direct list, support that too
#         if isinstance(raw, list):
#             raw_stations = raw
#         elif isinstance(raw, dict) and "stations" in raw and isinstance(raw["stations"], list):
#             raw_stations = raw["stations"]
#         else:
#             # If the format is unexpected, try to find a plausible list in common keys
#             raw_stations = []
#             if isinstance(raw, dict):
#                 for k in ("stations", "data", "results"):
#                     if isinstance(raw.get(k), list):
#                         raw_stations = raw[k]
#                         break

#         normalized = [normalize_station_raw(s) for s in raw_stations]

#         # Filter out stations without coords (frontend map needs them; but still include metadata)
#         return jsonify({"query": q, "stations": normalized})
#     except Exception as e:
#         # return stacktrace for debugging (in production hide this)
#         traceback_str = traceback.format_exc()
#         return jsonify({"error": "backend error", "details": str(e), "trace": traceback_str}), 500



# def get_tree_recommendation(pollutants, aqi_value):
#     """
#     Returns best tree recommendation for 50, 100 and 200 trees.
#     pollutants = station["pollutants"]
#     aqi_value = station["waqi_aqi"]
#     """
#     df = pd.read_json("Tree_data.json")
#     tree_list = df.to_dict(orient="records")   # convert to list of dicts


    
    

#     # -------------------------------
#     # 1. Compute score for every tree
#     # -------------------------------
#     tree_scores = []
#     for tree in tree_list:
#         score = 0

#         # Match tree to the pollutants
#         # Increase score for trees absorbing dominant pollutants
#         if "pm2_5" in pollutants:
#             score += tree.get("PM2_5_g_year", 0) * pollutants["pm2_5"]

#         if "pm10" in pollutants:
#             score += tree.get("PM10_g_year", 0) * pollutants["pm10"]

#         if "no2" in pollutants:
#             score += tree.get("NO2_g_year", 0) * pollutants["no2"]

#         if "so2" in pollutants:
#             score += tree.get("SO2_g_year", 0) * pollutants["so2"]

#         if "co" in pollutants:
#             score += tree.get("CO_g_year", 0) * pollutants["co"]

#         if "o3" in pollutants:
#             score += tree.get("O3_g_year", 0) * pollutants["o3"]

#         tree_scores.append({
#             "Tree_name": tree["Common_Name"],
#             "Scientific_name": tree["Scientific_Name"],
#             "Canopy_density": tree["Canopy_Density"],
#             "Score": score,
#             "Raw": tree
#         })

#         print({
#             "Tree_name":tree["Common_Name"],
#             "Scientific_name":tree["Scientific_Name"],
#             "Canopy_density": tree["Canopy_Density"],
#             "Score": score,
#             "Raw": tree
#         })


#     # Sort by score descending
#     tree_scores = sorted(tree_scores, key=lambda x: x["score"], reverse=True)

#     # Pick best 1 tree
#     best_tree = tree_scores[0]["raw"]

#     # -------------------------------
#     # 2. Compute reductions for 50, 100, 200 trees
#     # -------------------------------


#     output = {}

#     for group in [50, 100, 200]:
#         reduction = calculate_tree_pollutant.calculate_tree_pollutant_reduction_fixed(
#             pollutants=pollutants,
#             tree=best_tree,
#             num_trees=group
#         )

#         output[group] = {
#             "tree_name": best_tree["Tree_Name"],
#             "scientific_name": best_tree["Scientific_Name"],
#             "canopy_density": best_tree["Canopy_Density"],
#             "benefits": reduction
#         }

#     return output





# @app.route("/tree_recommendations")
# def tree_recommendations():
#     location = request.args.get("location", "").strip()
#     if not location:
#         return jsonify({"error": "location is required"}), 400

#     try:
#         data = aqi_data_place.get_place_stations_with_pollutants(location)

#         # FIX: Normalize data so every station always has pollutants key
#         normalized_stations = [normalize_station_raw(s) for s in data["stations"]]

#         results = []
#         for station in normalized_stations:

#             tree_output = get_tree_recommendation(
#                 pollutants=station["pollutants"],   # now always exists {}
#                 aqi_value=station["aqi"]            # use normalized key
#             )

#             results.append({
#                 "station_name": station["station_name"],
#                 "tree_groups": tree_output
#             })

#         return jsonify({
#             "location": location,
#             "status": "success",
#             "recommendations": results
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



# if __name__ == "__main__":
#     # Debug mode helps during development
#     app.run(debug=True, port=5000)


from coordinates import waqi_search
import json
from AQI_Data import aqi_data_place
from flask import Flask, render_template, request, jsonify
import traceback
from Tree_Recommendation import calculate_tree_pollutant
from math import fabs
import pandas as pd

app = Flask(__name__, static_folder="static", template_folder="templates")


def normalize_station_raw(s):
    """
    Convert a raw station dict into a normalized metadata dict used by frontend.
    Ensures keys exist and pollutants is a dict.
    """
    name = s.get("station_name") or s.get("station") or s.get("stationName") or "Unknown Station"
    lat = s.get("lat") or s.get("latitude") or s.get("Lat") or None
    lon = s.get("lon") or s.get("longitude") or s.get("Lon") or None
    aqi = s.get("waqi_aqi") or s.get("aqi") or s.get("AQI") or "N/A"

    pollutants = {}
    if "pollutants" in s and isinstance(s.get("pollutants"), dict):
        pollutants = s.get("pollutants")
    elif s.get("openweather_pollutants") and isinstance(s.get("openweather_pollutants"), dict):
        pollutants = s["openweather_pollutants"].get("pollutants", {}) or {}
    elif s.get("openweather") and isinstance(s.get("openweather"), dict):
        pollutants = s["openweather"].get("pollutants", {}) or {}
    if not isinstance(pollutants, dict):
        pollutants = {}

    return {
        "station_name": name,
        "lat": lat,
        "lon": lon,
        "aqi": aqi,
        "pollutants": pollutants
    }


def normalize_tree_row(row):
    """Convert a raw tree row to consistent field names for your scoring logic."""
    return {
        "tree_name": row.get("Common_Name"),
        "scientific_name": row.get("Scientific_Name"),
        "canopy_density": row.get("Canopy_Density"),
        "pm25": row.get("PM2_5_g_year", 0),
        "pm10": row.get("PM10_g_year", 0),
        "no2": row.get("NO2_g_year", 0),
        "so2": row.get("SO2_g_year", 0),
        "co": row.get("CO_g_year", 0),
        "o3": row.get("O3_g_year", 0)
    }


def load_tree_data():
    raw = json.load(open("Tree_data.json", "r", encoding="utf-8"))
    trees = [normalize_tree_row(t) for t in raw]
    return trees


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    try:
        raw = aqi_data_place.get_place_stations_with_pollutants(q)
        if isinstance(raw, list):
            raw_stations = raw
        elif isinstance(raw, dict) and "stations" in raw and isinstance(raw["stations"], list):
            raw_stations = raw["stations"]
        else:
            raw_stations = []
            if isinstance(raw, dict):
                for k in ("stations", "data", "results"):
                    if isinstance(raw.get(k), list):
                        raw_stations = raw[k]
                        break

        normalized = [normalize_station_raw(s) for s in raw_stations]
        return jsonify({"query": q, "stations": normalized})
    except Exception as e:
        traceback_str = traceback.format_exc()
        return jsonify({"error": "backend error", "details": str(e), "trace": traceback_str}), 500


def get_tree_recommendation(pollutants, aqi_value):
    tree_list = load_tree_data()

    # 1. Compute score for every tree
    tree_scores = []
    for tree in tree_list:
        score = 0
        score += tree["pm25"] * pollutants.get("pm2_5", 0)
        score += tree["pm10"] * pollutants.get("pm10", 0)
        score += tree["no2"] * pollutants.get("no2", 0)
        score += tree["so2"] * pollutants.get("so2", 0)
        score += tree["co"] * pollutants.get("co", 0)
        score += tree["o3"] * pollutants.get("o3", 0)

        tree_scores.append({
            "tree": tree,
            "score": score
        })

    # Sort by score descending
    tree_scores = sorted(tree_scores, key=lambda x: x["score"], reverse=True)
    best_tree = tree_scores[0]["tree"]
    

    # 2. Compute reductions for 50, 100, 200 trees
    output = {}
    for group in [50, 100, 200]:
        reduction = calculate_tree_pollutant.calculate_tree_pollutant_reduction_fixed(
            pollutants=pollutants,
            tree=best_tree,
            num_trees=group
        )
        output[group] = {
            "tree_name": best_tree["tree_name"],
            "scientific_name": best_tree["scientific_name"],
            "canopy_density": best_tree.get("canopy_density") or best_tree.get("Canopy_Density"),  # <-- normalized
            "benefits": reduction
        }

    return output



@app.route("/tree_recommendations")
def tree_recommendations():
    location = request.args.get("location", "").strip()
    if not location:
        return jsonify({"error": "location is required"}), 400

    try:
        data = aqi_data_place.get_place_stations_with_pollutants(location)
        normalized_stations = [normalize_station_raw(s) for s in data.get("stations", [])]

        results = []
        for station in normalized_stations:
            tree_output = get_tree_recommendation(
                pollutants=station["pollutants"],
                aqi_value=station["aqi"]
            )
            results.append({
                "station_name": station["station_name"],
                "tree_groups": tree_output
            })

        return jsonify({
            "location": location,
            "status": "success",
            "recommendations": results
        })
    except Exception as e:
        traceback_str = traceback.format_exc()
        return jsonify({"error": str(e), "trace": traceback_str}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
