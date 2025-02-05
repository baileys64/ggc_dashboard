import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load your Garage Gym Competition CSV file
@st.cache_data
def load_data():
    # Replace 'your_file.csv' with your actual CSV file path
    return pd.read_csv('ggc_compile_test.csv')

# Load data
data = load_data()

# Sidebar filters
st.sidebar.header("Filters")
entered_value = st.sidebar.text_input("Enter a value (e.g., weight):", "")
unit = st.sidebar.selectbox("Select unit:", ["", "Pounds", "Kilograms"])
gender = st.sidebar.selectbox("Select gender:", ["All", "Male", "Female"])
lift_category = st.sidebar.selectbox(
    "Select lift category:",
    ["Bench", "Squat", "Deadlift", "Total", "Improvement"]
)

# Main title
st.title("Garage Gym Competition Dashboard")

# Display raw data
# st.subheader("Raw Data")
# st.dataframe(data)

# Filter data based on selections
filtered_data = data.copy()

if gender != "All":
    filtered_data = filtered_data[filtered_data["Gender"] == gender]

if lift_category in data.columns:
    filtered_data = filtered_data[["Gender", lift_category]]

# Calculate percentile if a value is entered
if entered_value and lift_category in filtered_data.columns:
    try:
        entered_value = float(entered_value)
        # Convert entered value if needed
        if unit == "Kilograms":
            entered_value *= 2.20462  # Convert kilograms to pounds

        # Calculate percentile
        percentiles = np.percentile(filtered_data[lift_category].dropna(), np.arange(0, 101))
        entered_percentile = (
            sum(entered_value > percentiles) / 100 * 100
        )

        # Display the percentile
        st.subheader(f"Percentile for {lift_category}")
        st.write(
            f"The entered value of **{entered_value:.2f} ({unit})** corresponds to the "
            f"**{entered_percentile:.2f}th percentile** for {lift_category}."
        )

    # Histogram with Highlighted Value
        st.subheader(f"Histogram of {lift_category} Weights")
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(filtered_data[lift_category], bins=20, alpha=0.7, color='blue', edgecolor='black')
        ax.axvline(entered_value, color='red', linestyle='dashed', linewidth=2, label=f"Your Weight: {entered_value:.2f} lbs")
        ax.set_xlabel(f"{lift_category} Weight (lbs)")
        ax.set_ylabel("Frequency")
        ax.set_title(f"Distribution of {lift_category} Weights")
        ax.legend()

        st.pyplot(fig)
    except ValueError:
        st.error("Please enter a valid numerical value.")
else:
    st.write("Enter a value and select a category to calculate the percentile.")

# Display filtered data
# st.subheader("Filtered Data")
# st.dataframe(filtered_data)
