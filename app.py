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
    xls = pd.ExcelFile("mastercc.xlsx")
    # Load data from the two sheets and assign county names
    robeson_data = pd.read_excel(xls, sheet_name="robenson_data").assign(County="Robeson County")
    montgomery_data = pd.read_excel(xls, sheet_name="montgomery_data").assign(County="Montgomery County")

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
counties = sorted(data["County"].unique())
selected_county = st.sidebar.selectbox("Select County", counties)
categories = sorted(data["Metric_Category"].unique())
selected_category = st.sidebar.selectbox("Select Category", categories)

filtered = data[(data["County"] == selected_county) & (data["Metric_Category"] == selected_category)]

# Dashboard visuals
st.title("Inclusive Growth Score Dashboard")
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

# Visualization 3 - Correlation Heatmap
try:
    pivot = data.pivot_table(index="Year", columns="County", values="Value")
    corr = pivot.corr()
    fig_heat = px.imshow(
        corr, text_auto=True, color_continuous_scale="Blues",
        title="County Correlation Heatmap",
        template="simple_white"
    )
    st.plotly_chart(fig_heat, use_container_width=True)
except Exception as e:
    st.warning("Correlation heatmap not available for this selection.")

# Additional functionality - Policy simulation slider
st.sidebar.header("Policy Simulation")
policy_change = st.sidebar.slider("Increase metric by (%)", -50, 50, 0)
if policy_change != 0:
    simulated = filtered.copy()
    simulated["Value"] *= (1 + policy_change / 100)
    st.subheader("Simulated Impact")
    fig_simulated = px.bar(
        simulated, x="Year", y="Value", color="Year",
        title=f"Simulated Impact: {policy_change}% Change",
        labels={"Value": "Score", "Year": "Year"},
        template="simple_white"
    )
    st.plotly_chart(fig_simulated, use_container_width=True)

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
    new_data = pd.ExcelFile(uploaded_file)
    data = pd.concat(
        [pd.read_excel(new_data, sheet_name=s).assign(County=s) for s in new_data.sheet_names],
        ignore_index=True
    )
    st.sidebar.success("New data uploaded successfully!")

# Function to train a linear regression model and predict 2025 scores
@st.cache_data
def train_and_predict(data):
    projections = []
    for metric in data["Metric_Category"].unique():
        for county in data["County"].unique():
            # Filter data for the specific metric and county
            subset = data[(data["Metric_Category"] == metric) & (data["County"] == county)]
            
            # Ensure there is enough data to train the model
            if len(subset) < 2:
                continue

            # Prepare the data for training
            X = subset["Year"].values.reshape(-1, 1)
            y = subset["Value"].values

            # Train the linear regression model
            model = LinearRegression()
            model.fit(X, y)

            # Predict the 2025 score
            projected_score = model.predict([[2025]])[0]

            # Append the projection
            projections.append({
                "County": county,
                "Metric_Category": metric,
                "Projected_Year": 2025,
                "Projected_Score": projected_score
            })

    # Convert projections to a DataFrame
    projection_df = pd.DataFrame(projections)
    return projection_df

# Train the model and get projections
projection_data = train_and_predict(data)

# Display projections in a table
st.subheader("2025 Projected Inclusive Growth Scores")
st.dataframe(projection_data, use_container_width=True)

# Visualization 1 - Bar Chart for Projections
st.subheader("Projected Scores by Metric")
fig_projection_bar = px.bar(
    projection_data, x="Metric_Category", y="Projected_Score", color="County",
    title="2025 Projected Scores by Metric",
    labels={"Projected_Score": "Projected Score", "Metric_Category": "Metric"},
    template="plotly_white"
)
st.plotly_chart(fig_projection_bar, use_container_width=True)

# Visualization 2 - Cumulative Projections
st.subheader("Cumulative Projected Scores")
cumulative_data = projection_data.groupby("County")["Projected_Score"].sum().reset_index()
fig_cumulative = px.pie(
    cumulative_data, names="County", values="Projected_Score",
    title="Cumulative Projected Scores by County",
    template="seaborn"
)
st.plotly_chart(fig_cumulative, use_container_width=True)

# Visualization 3 - Line Chart for Trends
st.subheader("Trends in Projected Scores")
fig_trends = px.line(
    projection_data, x="Metric_Category", y="Projected_Score", color="County",
    title="Trends in Projected Scores by Metric",
    labels={"Projected_Score": "Projected Score", "Metric_Category": "Metric"},
    template="ggplot2"
)
st.plotly_chart(fig_trends, use_container_width=True)