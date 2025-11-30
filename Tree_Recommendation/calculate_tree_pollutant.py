from Tree_Recommendation import canopy

from Tree_Recommendation import canopy

def calculate_tree_pollutant_reduction_fixed(pollutants, tree, num_trees):
    """
    pollutants = openweather pollutant dict (µg/m³)
    tree       = tree data row containing PM2_5_g_year etc.
    num_trees  = 50 / 100 / 200
    """

    # Convert grams per year → micrograms per hour
    def g_year_to_ug_hour(g):
        return (g * 1_000_000) / (365 * 24)

    # --- FIX: Define a fixed Air Volume of Interest (e.g., above 1 hectare) ---
    # We use a fixed area to ensure the reduction scales correctly with num_trees.
    AMBIENT_AREA_OF_INTEREST_M2 = 10000  # 1 hectare (10,000 m^2)
    mixing_height = 50  # meters (WHO urban mixing height)
    
    # This air volume remains constant for all tree groups (50, 100, 200)
    ambient_air_volume_m3 = round(AMBIENT_AREA_OF_INTEREST_M2 * mixing_height, 1)

    reduction = {}
    reduction_values = []

    # Ensure tree absorption keys are correctly mapped
    pollutant_keys = {
        "pm2_5": "pm25",  # Assuming tree data keys are normalized to lowercase in main.py
        "pm10": "pm10",
        "no2":  "no2",
        "so2":  "so2",
        "co":   "co",
        "o3":   "o3"
    }

    for pol, tree_key in pollutant_keys.items():
        conc = pollutants.get(pol, 0)  # Station concentration µg/m³

        # Total pollutant mass in fixed ambient air volume
        air_mass_ug = conc * ambient_air_volume_m3 # Denominator is now FIXED

        # Tree absorption rate (µg/h)
        tree_abs = g_year_to_ug_hour(tree.get(tree_key, 0))

        # Total absorption by all trees
        total_abs = tree_abs * num_trees # Numerator scales linearly with num_trees

        # Compute reduction percentage
        if air_mass_ug > 0:
            reduction_percent = (total_abs / air_mass_ug) * 100
            reduction_percent = min(max(reduction_percent, 0), 90)  # clamp 0-90%
        else:
            reduction_percent = 0

        reduction[pol] = round(reduction_percent, 2)
        reduction_values.append(reduction_percent)

    # Calculate final averages and AQI
    avg_red = sum(reduction_values) / len(reduction_values) if reduction_values else 0
    reduction["avg_reduction_percent"] = round(avg_red, 2)

    # Compute new AQI
    original_aqi = max(pollutants.get("AQI", 0), 0)
    new_aqi = original_aqi * (1 - avg_red / 100)
    reduction["new_AQI"] = round(max(new_aqi, 0), 1)

    return reduction
