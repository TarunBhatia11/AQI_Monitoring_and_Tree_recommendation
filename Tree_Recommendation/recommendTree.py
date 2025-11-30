import json

with open("Tree_data.json", "r") as f:
    TREE_DATA = json.load(f)

def recommend_trees_from_dataset(pollutants, top_n=5):
    scored = []

    for tree in TREE_DATA:
        # ✅ FIX: Weight the tree's absorption rate by the local pollutant concentration.
        # Use .get(key, 0) to safely handle any missing pollutant data from the station.
        score = (
            tree.get("PM2_5_g_year", 0) * pollutants.get("pm2_5", 0) +
            tree.get("PM10_g_year", 0) * pollutants.get("pm10", 0) +
            tree.get("NO2_g_year", 0) * pollutants.get("no2", 0) +
            tree.get("SO2_g_year", 0) * pollutants.get("so2", 0) +
            tree.get("CO_g_year", 0) * pollutants.get("co", 0) +
            tree.get("O3_g_year", 0) * pollutants.get("o3", 0)
        )
        scored.append((tree, score))

    # Handle the case where all scores might be 0 (e.g., if pollutant data is missing/zero)
    # The sort and slice logic remains the same.
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]
