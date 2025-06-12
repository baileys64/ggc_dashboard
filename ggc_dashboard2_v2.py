import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import base64
import io

st.set_page_config(page_title="GGC Individual Progress Dashboard", layout="wide")

def extract_year_season(comp):
    match = re.search(r'(Spring|Fall)?\s*(\d{4})', str(comp), re.IGNORECASE)
    if match:
        season = match.group(1)
        year = int(match.group(2))
        season_clean = season.capitalize() if season else None
        return pd.Series([year, season_clean])
    return pd.Series([None, None])

@st.cache_data
def load_data():
   import re

    url = st.secrets["data"]["sheet_url"]
    df = pd.read_csv(url)

    # Extract year and season
    def extract_year_season(comp):
        match = re.search(r'(Spring|Fall)?\s*(\d{4})', str(comp), re.IGNORECASE)
        if match:
            season = match.group(1)
            year = int(match.group(2))
            season_clean = season.capitalize() if season else None
            return pd.Series([year, season_clean])
        return pd.Series([None, None])

    # Apply and assign columns
    parsed = df["Competition"].apply(extract_year_season)
    parsed.columns = ["parsed_year", "parsed_season"]
    df["parsed_year"] = parsed[0]
    df["parsed_season"] = parsed[1]

    # Handle single-season years
    season_counts = df.groupby("parsed_year")["parsed_season"].nunique()
    single_season_years = season_counts[season_counts == 1].index

    df["parsed_season"] = df.apply(
        lambda row: "Spring" if pd.isna(row["parsed_season"]) and row["parsed_year"] in single_season_years
        else row["parsed_season"],
        axis=1
    )

    # Add sorting columns
    season_order_map = {"Spring": 0, "Fall": 1}
    df["season_order"] = df["parsed_season"].map(season_order_map).fillna(-1).astype(int)
    df["year"] = df["parsed_year"].fillna(0).astype(int)

    # DEBUG OUTPUT
    st.write("✅ Columns in df:", df.columns.tolist())
    st.write("🧪 Sample values from df[['Competition', 'parsed_year', 'parsed_season', 'year', 'season_order']]:")
    st.write(df[["Competition", "parsed_year", "parsed_season", "year", "season_order"]].head())

    return df


df = load_data()

st.title("🔒 GGC Individual Progress Dashboard")

# --- STEP 1: Filter to 2024 Fall competition only
fall_2024_df = df[df["Competition"] == "2024 Fall"]
fall_2024_df = fall_2024_df[fall_2024_df['Private']=='Please publish my results']

# --- STEP 2: Get handles from that competition
fall_handles = sorted(fall_2024_df['instagram_handle'].dropna().unique())
handle = st.selectbox("Select your handle (from Fall 2024):", fall_handles)

# --- STEP 3: Get all first_names from that handle in Fall 2024
fall_handle_df = fall_2024_df[fall_2024_df['instagram_handle'] == handle]
first_names = sorted(fall_handle_df["first_name"].dropna().unique())

if len(first_names) > 1:
    first_name = st.selectbox("Multiple names found. Select your first name:", first_names)
else:
    first_name = first_names[0]

# --- STEP 4: Get Unique_ID using handle + first_name from Fall 2024 only
user_row = fall_handle_df[fall_handle_df["first_name"] == first_name].iloc[0]
user_id = user_row["GGC Unique ID"]

# --- STEP 5: Get full history using Unique_ID
# Get full history for that user
user_data = df[df["GGC Unique ID"] == user_id].dropna(subset=["Competition"]).copy()

# Parse year/season again for sorting if needed
user_data[['parsed_year', 'parsed_season']] = user_data["Competition"].apply(extract_year_season)
st.write("Columns in df:", df.columns.tolist())
season_counts = df.groupby('parsed_year')['parsed_season'].nunique()
single_season_years = season_counts[season_counts == 1].index
user_data['parsed_season'] = user_data.apply(
    lambda row: 'Spring' if pd.isna(row['parsed_season']) and row['parsed_year'] in single_season_years
    else row['parsed_season'],
    axis=1
)
season_order_map = {"Spring": 0, "Fall": 1}
user_data['season_order'] = user_data['parsed_season'].map(season_order_map).fillna(-1).astype(int)
user_data['year'] = user_data['parsed_year'].fillna(0).astype(int)


# --- User selects lift and unit
lift = st.selectbox("Select lift to track:", ["Squat", "Bench", "Deadlift", "Total"])
unit = st.selectbox("Select unit:", ["lbs", "kg"])

# --- Drop nulls in lift and convert units
user_data = user_data.dropna(subset=[lift])
if unit == "kg":
    user_data[lift + "_converted"] = user_data[lift] / 2.20462
else:
    user_data[lift + "_converted"] = user_data[lift]

# Sort by year and season
user_data = user_data.sort_values(["year", "season_order"])

# Calculate percentile per competition
def get_percentile(row):
    comp = row['Competition']
    group = df[df['Competition'] == comp]
    value = row[lift]
    group_vals = group[lift] / 2.20462 if unit == "kg" else group[lift]
    return round((group_vals < value).mean() * 100, 2)

user_data["Percentile"] = user_data.apply(get_percentile, axis=1)

# Table of results
table_data = user_data[['Competition', lift + "_converted", "Percentile"]].rename(
    columns={lift + "_converted": f"{lift} ({unit})"}
)

st.markdown("### 📋 Your Lift History")
st.dataframe(table_data, use_container_width=True)

# Line plot of progress
st.markdown("### 📈 Progress Over Time")
fig, ax = plt.subplots()
ax.plot(table_data["Competition"], table_data[f"{lift} ({unit})"], marker='o', linewidth=2)
ax.set_xlabel("Competition")
ax.set_ylabel(f"{lift} ({unit})")
ax.set_title(f"{lift} Progress Over Time")
plt.xticks(rotation=45)
st.pyplot(fig)
