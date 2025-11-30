# CELL — AQI formula implementation

def calculate_aqi_using_formula(components):
    """
    Calculates AQI from pollutant concentrations using US EPA breakpoints.
    Works for PM2.5, PM10, O3, CO, NO2, SO2.
    AQI = max(sub-index values for each pollutant)
    """

    # Breakpoints (EPA standard)
    breakpoints = {
        "pm2_5": [
            (0.0, 12.0, 0, 50),
            (12.1, 35.4, 51, 100),
            (35.5, 55.4, 101, 150),
            (55.5, 150.4, 151, 200),
            (150.5, 250.4, 201, 300),
            (250.5, 500.4, 301, 500),
        ],
        "pm10": [
            (0, 54, 0, 50),
            (55, 154, 51, 100),
            (155, 254, 101, 150),
            (255, 354, 151, 200),
            (355, 424, 201, 300),
            (425, 604, 301, 500),
        ],
        "o3": [
            (0.000, 0.054, 0, 50),
            (0.055, 0.070, 51, 100),
            (0.071, 0.085, 101, 150),
            (0.086, 0.105, 151, 200),
            (0.106, 0.200, 201, 300),
        ],
        "co": [
            (0.0, 4.4, 0, 50),
            (4.5, 9.4, 51, 100),
            (9.5, 12.4, 101, 150),
            (12.5, 15.4, 151, 200),
            (15.5, 30.4, 201, 300),
        ],
        "so2": [
            (0, 35, 0, 50),
            (36, 75, 51, 100),
            (76, 185, 101, 150),
            (186, 304, 151, 200),
            (305, 604, 201, 300),
        ],
        "no2": [
            (0, 53, 0, 50),
            (54, 100, 51, 100),
            (101, 360, 101, 150),
            (361, 649, 151, 200),
            (650, 1249, 201, 300),
        ]
    }

    def compute_subindex(cp, bplist):
        """Compute the sub-index using linear AQI formula."""
        for (low_c, high_c, low_i, high_i) in bplist:
            if low_c <= cp <= high_c:
                return round(((high_i - low_i) / (high_c - low_c)) * (cp - low_c) + low_i)
        return None  # out of range

    sub_indexes = []

    for pollutant, bp_list in breakpoints.items():
        cp = components.get(pollutant)
        if cp is not None:
            si = compute_subindex(cp, bp_list)
            if si is not None:
                sub_indexes.append(si)

    if not sub_indexes:
        return None

    return max(sub_indexes)  # AQI = highest sub-index
