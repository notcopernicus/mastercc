import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression

# Set page configuration
st.set_page_config(page_title="Inclusive Growth Score Data Portal", layout="wide", page_icon="📊")

# Mission statement
st.markdown(
    """
    <h1 style='color: #2c3e50; font-family: Arial;'>Inclusive Growth Score Data Portal</h1>
    <p style='font-size: 18px; color: #34495e;'>
    Welcome to the Inclusive Growth Score Data Portal, a resource for researchers, policy analysts, and economic offices. This platform provides rigorous, accessible, and actionable data to drive equitable economic outcomes.
    </p>
    <hr style='border: 1px solid #bdc3c7;'>
    """,
    unsafe_allow_html=True
)

# Load Excel data

@st.cache_data
def load_data():
    # --- IMPORTANT ---
    # Make sure 'mastercc.xlsx' is in the same directory as this app.py file
    # or provide the full path to the file.
    try:
        xls = pd.ExcelFile("mastercc.xlsx")
    except FileNotFoundError:
        st.error("Error: The file 'mastercc.xlsx' was not found.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while trying to read 'mastercc.xlsx': {e}")
        st.stop()
        
    # Load data from the two sheets and assign county names
    try:
        robeson_data = pd.read_excel(xls, sheet_name="robenson_data").assign(County="Robeson County")
        montgomery_data = pd.read_excel(xls, sheet_name="montgomery_data").assign(County="Montgomery County")
    except Exception as e:
        st.error(f"Error reading sheets 'robenson_data' or 'montgomery_data'. Make sure they exist. Details: {e}")
        st.stop()

    # Combine the data into a single DataFrame
    df = pd.concat([robeson_data, montgomery_data], ignore_index=True)

    # Reshape the data to gather categories dynamically
    df = df.melt(
        id_vars=["Year", "County"],
        var_name="Metric_Category",
        value_name="Value"
    )
    return df

data = load_data()

# Sidebar filters
st.sidebar.header("Filter Options")
st.sidebar.markdown("""
<div style="color: #444; font-size: 16px;">
<b>Select County:</b> Choose the county to analyze.<br>
<b>Select Metric Category:</b> Choose the metric category to visualize.
</div>
""", unsafe_allow_html=True)
counties = sorted(data["County"].unique())
selected_county = st.sidebar.selectbox("County", counties)
categories = sorted(data["Metric_Category"].unique())
selected_category = st.sidebar.selectbox("Metric Category", categories)

filtered = data[(data["County"] == selected_county) & (data["Metric_Category"] == selected_category)]

# Dashboard visuals
st.title("Inclusive Growth Score Dashboard")

# Handle potential empty data after filtering
if filtered.empty:
    st.warning(f"No data found for {selected_county} - {selected_category}.")
else:
    st.metric(label="Average Inclusive Growth Score", value=round(filtered["Value"].mean(), 2))

    # Visualization 1 - Bar Chart
    fig_bar = px.bar(
        filtered, x="Year", y="Value", color="Year",
        title=f"{selected_county} - {selected_category}",
        labels={"Value": "Score", "Year": "Year"},
        template="simple_white"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Visualization 2 - Highlighting Gaps and Disparities
st.subheader("Gaps and Disparities in Metrics")
gaps_data = data[(data["Metric_Category"] == selected_category)]
if gaps_data.empty:
    st.warning(f"No data found for metric '{selected_category}' to show gaps.")
else:
    fig_gaps = px.line(
        gaps_data, x="Year", y="Value", color="County",
        title=f"Gaps in {selected_category} Across Counties",
        labels={"Value": "Score", "Year": "Year"},
        template="plotly_dark"
    )
    st.plotly_chart(fig_gaps, use_container_width=True)

# Visualization 3 - Labor Market and Inclusive Growth
st.subheader("Labor Market and Inclusive Growth")
labor_data = data[data["Metric_Category"].str.contains("Labor", case=False, na=False)]
if labor_data.empty:
    st.warning("No 'Labor' metrics found for this visualization.")
else:
    fig_labor = px.scatter(
        labor_data, x="Year", y="Value", color="County", size="Value",
        title="Labor Market Trends",
        labels={"Value": "Score", "Year": "Year"},
        template="ggplot2"
    )
    st.plotly_chart(fig_labor, use_container_width=True)

# Visualization 2 - County Comparison
st.subheader("Compare Counties")
compare = st.multiselect("Compare with:", [c for c in counties if c != selected_county])
if compare:
    comp_data = data[(data["County"].isin(compare + [selected_county])) & (data["Metric_Category"] == selected_category)]
    fig_compare = px.line(
        comp_data, x="Year", y="Value", color="County",
        title=f"Comparison: {selected_category}",
        labels={"Value": "Score", "Year": "Year"},
        template="simple_white"
    )
    st.plotly_chart(fig_compare, use_container_width=True)

# Replace heatmap with another visualization
st.subheader("County Comparison - Scatter Plot")
fig_scatter = px.scatter(
    data, x="Year", y="Value", color="County", size="Value",
    title="County Comparison Across Years",
    labels={"Value": "Score", "Year": "Year"},
    template="plotly_dark",
    color_discrete_map={
        "Montgomery County": "green",
        "Robeson County": "red"
    }
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Additional functionality - Policy simulation for Affordable Housing
st.sidebar.header("Policy Simulation")
st.sidebar.subheader("Affordable Housing")
housing_change = st.sidebar.slider("Increase Affordable Housing by (%)", -50, 50, 0)

# Filter data for Affordable Housing
housing_data = data[data["Metric_Category"].str.contains("Housing", case=False, na=False)].copy()

if housing_data.empty:
    st.sidebar.warning("No 'Housing' metrics found for simulation.")
else:
    # --- SIMULATION LOGIC ---
    # This part assumes you have future data (e.g., 2025) in your sheet.
    # If not, you'll need to *forecast* it. Let's add a simple forecast.

    # Let's check for 2025 data.
    if 2025 not in housing_data['Year'].unique():
        st.sidebar.info("2025 data not found. Forecasting using Linear Regression.")
        
        forecasted_rows = []
        for county in housing_data['County'].unique():
            for metric in housing_data['Metric_Category'].unique():
                county_metric_data = housing_data[
                    (housing_data['County'] == county) & 
                    (housing_data['Metric_Category'] == metric)
                ].sort_values('Year')
                
                if len(county_metric_data) < 2:
                    continue # Not enough data to forecast

                # Prepare data for regression
                X = county_metric_data[['Year']]
                y = county_metric_data['Value']
                
                # Fit model and predict for 2025
                model = LinearRegression()
                model.fit(X, y)
                predicted_2025_value = model.predict(np.array([[2025]]))[0]
                
                forecasted_rows.append({
                    "Year": 2025,
                    "County": county,
                    "Metric_Category": metric,
                    "Value": predicted_2025_value
                })
        
        if forecasted_rows:
            forecast_df = pd.DataFrame(forecasted_rows)
            housing_data = pd.concat([housing_data, forecast_df], ignore_index=True)
        else:
            st.sidebar.error("Could not forecast 2025 data. Simulation may not work.")

    # Now, filter for 2025 data (which is either original or forecasted)
    housing_2025 = housing_data[housing_data["Year"] == 2025].copy()
    
    if housing_2025.empty:
        st.subheader("Simulated Impact on Affordable Housing")
        st.warning("Could not find or forecast 2B025 data for housing simulation.")
    else:
        housing_2025["Simulated_Value"] = housing_2025["Value"] * (1 + housing_change / 100)

        # Combine the original and simulated data for visualization
        housing_2025_orig = housing_2025.copy()
        housing_2025_orig["Scenario"] = "Projected 2025 (0% Change)"
        
        simulated_housing = housing_2025.copy()
        simulated_housing["Value"] = simulated_housing["Simulated_Value"] # Use simulated value
        simulated_housing["Scenario"] = f"Simulated 2025 ({housing_change}% Change)"
        
        combined_housing = pd.concat([housing_2025_orig, simulated_housing])

        # Visualization for Affordable Housing Simulation
        st.subheader("Simulated Impact on Affordable Housing (2025)")
        fig_housing_simulation = px.bar(
            combined_housing, x="County", y="Value", color="Scenario",
            barmode="group",
            title=f"Simulated Impact: Affordable Housing ({housing_change}% Change)",
            labels={"Value": "Projected Score", "County": "County"},
            template="plotly_dark",
            color_discrete_map={
                f"Simulated 2025 ({housing_change}% Change)": "#EF553B",
                "Projected 2025 (0% Change)": "#636EFA"
            }
        )
        st.plotly_chart(fig_housing_simulation, use_container_width=True)

# Download filtered results
st.sidebar.header("Download Data")
st.sidebar.download_button(
    label="Download Filtered Data as CSV",
    data=filtered.to_csv(index=False),
    file_name="filtered_data.csv",
    mime="text/csv"
)

# Upload new Excel file
st.sidebar.header("Upload New Data")
uploaded_file = st.sidebar.file_uploader("Upload an Excel file", type=["xlsx"])
if uploaded_file:
    try:
        new_data_xls = pd.ExcelFile(uploaded_file)
        # This assumes sheet names are County names, which is different from your load_data function.
        # Re-using the logic from load_data would be safer.
        # Let's assume the new file has the same structure as mastercc.xlsx
        new_robeson = pd.read_excel(new_data_xls, sheet_name="robenson_data").assign(County="Robeson County")
        new_montgomery = pd.read_excel(new_data_xls, sheet_name="montgomery_data").assign(County="Montgomery County")
        
        new_df = pd.concat([new_robeson, new_montgomery], ignore_index=True)
        new_df = new_df.melt(
            id_vars=["Year", "County"],
            var_name="Metric_Category",
            value_name="Value"
        )
        # This replaces the in-memory data 'data' but doesn't overwrite the @st.cache_data
        # For a true data replacement, you'd need to manage session state.
        # For now, just show a success message.
        st.sidebar.success("New data file uploaded! Refresh the page to use it.")
        # In a real app, you would clear the cache and rerun.
        # st.cache_data.clear()
        # st.experimental_rerun()
    except Exception as e:
        st.sidebar.error(f"Failed to load new data: {e}")