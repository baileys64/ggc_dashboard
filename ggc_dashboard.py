import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the CSV (update this path or use st.file_uploader for deployment)
@st.cache_data
def load_data():
    df = pd.read_csv("combined_ggc_results_public.csv")  # Replace with your actual CSV file
    return df

df = load_data()

# Sidebar inputs
st.title("🏋️ Garage Gym Competition Percentile Dashboard")

lift_type = st.selectbox("Select a lift:", ["Squat", "Bench", "Deadlift", "Total"])
unit = st.selectbox("Select unit:", ["lbs", "kg"])
gender = st.selectbox("Select gender:", ["Male", "Female"])

input_weight = st.number_input(f"Enter your {lift_type} weight ({unit}):", min_value=0.0, step=1.0)

# Convert data and filter
filtered_df = df[df["Gender"].str.lower() == gender.lower()].copy()

if unit == "kg":
    filtered_df[lift_type] = filtered_df[lift_type] / 2.20462  # Convert lbs to kg
    display_weight = input_weight
else:
    display_weight = input_weight

# Calculate percentile
if not filtered_df.empty:
    lift_values = filtered_df[lift_type].dropna()
    percentile = np.round((lift_values < display_weight).mean() * 100, 2)

    st.markdown(f"### 📊 Percentile: You are in the **{percentile}th** percentile for {gender.lower()}s in {lift_type.lower()}.")

    # Plot histogram
    fig, ax = plt.subplots()
    ax.hist(lift_values, bins=30, edgecolor='black', alpha=0.7)
    ax.axvline(display_weight, color='red', linestyle='dashed', linewidth=2)
    ax.set_title(f'{lift_type} Distribution ({unit})')
    ax.set_xlabel(f'{lift_type} Weight ({unit})')
    ax.set_ylabel('Count')
    st.pyplot(fig)

else:
    st.warning("No data available for selected gender.")

