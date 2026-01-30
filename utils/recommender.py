import pandas as pd

def recommend_crops(crop_data: pd.DataFrame, soil_ph, climate, top_k=3):
    """Filter crops by soil pH and climate, rank by price"""
    if crop_data.empty:
        return []

    try:
        df = crop_data[
            (crop_data["min_ph"] <= float(soil_ph)) &
            (crop_data["max_ph"] >= float(soil_ph)) &
            (crop_data["climate"].str.contains(climate, case=False, na=False))
        ]
    except Exception:
        df = crop_data.copy()

    if df.empty:
        df = crop_data.sort_values("price", ascending=False).head(top_k)
    else:
        df = df.sort_values("price", ascending=False).head(top_k)

    return df.to_dict(orient="records")
