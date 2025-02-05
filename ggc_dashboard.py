import streamlit as st
import pandas as pd
import numpy as np

# Load your Garage Gym Competition CSV file
@st.cache_data
def load_data():
    # Replace 'your_file.csv' with your actual CSV file path
    return pd.read_csv('ggc_fall24.csv')

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
st.subheader("Raw Data")
st.dataframe(data)

# Filter data based on selections
filtered_data = data.copy()

if gender != "All":
    filtered_data = filtered_data[filtered_data["Gender"] == gender]

if lift_category in data.columns:
    filtered_data = filtered_data[["Name", "Gender", lift_category]]

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
    except ValueError:
        st.error("Please enter a valid numerical value.")
else:
    st.write("Enter a value and select a category to calculate the percentile.")

# Display filtered data
st.subheader("Filtered Data")
st.dataframe(filtered_data)
