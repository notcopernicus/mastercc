# Inclusive Growth Score Data Portal

## Overview
The Inclusive Growth Score (IGS) Data Portal is an interactive dashboard designed for policymakers, researchers, and economic analysts. It provides insights into socioeconomic metrics for two counties: **Robeson County** and **Montgomery County**. The portal enables users to analyze historical data, visualize trends, and project future scores for inclusive growth.

---

## Features

### 1. **Data Loading**
- Reads data from an Excel file (`mastercc.xlsx`) containing two sheets:
  - `robenson_data` for Robeson County.
  - `montgomery_data` for Montgomery County.
- Combines and reshapes the data for analysis.

### 2. **Interactive Filters**
- Select a county (e.g., Robeson or Montgomery).
- Choose a metric category (e.g., Housing, Labor Market).

### 3. **Visualizations**
- **Bar Chart**: Displays metric scores over time for the selected county and category.
- **Line Chart**: Highlights gaps and disparities in metrics across counties.
- **Scatter Plot**: Shows labor market trends with bubble sizes representing scores.
- **Correlation Heatmap**: Visualizes relationships between counties' metrics.
- **Pie Chart**: Displays cumulative projected scores by county.
- **Line Chart for Trends**: Shows trends in projected scores across metrics.

### 4. **2025 Projections**
- Uses **Linear Regression** to predict the 2025 IGS for each metric and county.
- Displays projections in a table and visualizes them using bar, pie, and line charts.

### 5. **Additional Features**
- **Policy Simulation**: Simulate changes in metrics and visualize the impact.
- **Data Upload**: Upload new Excel files for analysis.
- **Download Filtered Data**: Download filtered results as a CSV file.

---

## Technical Details

### Tech Stack
- **Python 3.10+**: Core programming language.
- **Streamlit**: Framework for building interactive dashboards.
- **Pandas**: Data manipulation and analysis.
- **Plotly Express**: For creating interactive visualizations.
- **Scikit-learn**: For training the Linear Regression model.

### Data Handling
- Data is reshaped using `pd.melt` to convert wide-format data into long-format for easier analysis.
- Missing values and insufficient data points are handled gracefully to ensure model reliability.

### Modeling
- **Linear Regression**:
  - Trains separate models for each metric and county.
  - Predicts the 2025 score based on historical data (e.g., 2015–2024).
- **Cumulative Projections**:
  - Aggregates predictions across metrics to calculate a total score for each county.

### Caching
- The `@st.cache_data` decorator is used to cache data loading and model training, improving performance.

---

## How to Run the Project

### 1. **Install Dependencies**
Ensure you have Python 3.10+ installed. Then, install the required dependencies:
```bash
pip install -r requirements.txt
```

### 2. **Run the App**
Start the Streamlit app:
```bash
streamlit run app.py
```

### 3. **Access the Dashboard**
Open the URL provided by Streamlit (e.g., `http://localhost:8501`) in your browser.

---

## Folder Structure
```
mastercc.xlsx          # Excel file containing the data
app.py                 # Main Streamlit application
requirements.txt       # Python dependencies
README.md              # Documentation
```

---

## Future Enhancements
- Add support for additional counties.
- Integrate advanced machine learning models for more accurate projections.
- Provide downloadable visualizations in PDF or PNG format.

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.