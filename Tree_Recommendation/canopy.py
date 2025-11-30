def canopy_area_from_density(density):
    density = density.lower()
    if "very" in density:
        return 70
    if "dense" in density:
        return 50
    if "medium" in density:
        return 35
    return 20  # light
