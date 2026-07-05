import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

# -------------------------------------------------------------------------
# Page Configuration & Styling
# -------------------------------------------------------------------------
st.set_page_config(
    page_title="India Ethanol Blending Impact Predictor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------------
# Data Generation (Historical Baseline & Future Estimates for India)
# -------------------------------------------------------------------------
@st.cache_data
def generate_historical_data():
    # Historical data matching Indian bioenergy trajectory (2015-2025)
    years = np.arange(2015, 2026)
    
    # Blend percentages evolving over time
    blend_pct = np.array([1.5, 2.0, 3.8, 4.2, 5.0, 6.2, 8.1, 10.0, 11.5, 13.0, 15.0])
    
    # CO2 Emission Reduction (Million Metric Tonnes - MMT) matching blend penetration
    # Approximated relationship based on life-cycle assessments
    co2_reduction_mmt = blend_pct * 2.4 + np.random.normal(0, 0.5, len(years))
    
    # Forex savings in Billion USD
    forex_savings_billion_usd = blend_pct * 0.32 + np.random.normal(0, 0.1, len(years))
    
    # Historical feedstock production in Million Litres
    sugarcane_m_litres = np.array([700, 900, 1200, 1500, 1800, 2200, 2700, 3100, 3400, 3600, 3800])
    maize_m_litres = np.array([50, 60, 80, 110, 150, 250, 400, 600, 850, 1100, 1300])
    rice_m_litres = np.array([10, 15, 20, 35, 70, 120, 250, 450, 700, 950, 1150])
    tech_2g_m_litres = np.array([0, 0, 1, 2, 5, 10, 15, 30, 50, 80, 120])
    tech_3g_m_litres = np.array([0, 0, 0, 0, 0, 1, 2, 4, 8, 12, 20])
    
    df = pd.DataFrame({
        "Year": years,
        "Blend_Percentage": blend_pct,
        "CO2_Reduction_MMT": co2_reduction_mmt,
        "Forex_Savings_Billion_USD": forex_savings_billion_usd,
        "Sugarcane_Million_Litres": sugarcane_m_litres,
        "Maize_Million_Litres": maize_m_litres,
        "Rice_Million_Litres": rice_m_litres,
        "2G_Biomass_Million_Litres": tech_2g_m_litres,
        "3G_Algae_Million_Litres": tech_3g_m_litres
    })
    return df

df_hist = generate_historical_data()

# -------------------------------------------------------------------------
# Machine Learning Model Training
# -------------------------------------------------------------------------
# Model 1: CO2 Reduction Predictor based on Blend Percentage
X_blend = df_hist[['Blend_Percentage']]
y_co2 = df_hist['CO2_Reduction_MMT']
y_forex = df_hist['Forex_Savings_Billion_USD']

# Using Polynomial Features to capture slight efficiency scaling
model_co2 = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
model_co2.fit(X_blend, y_co2)

model_forex = make_pipeline(PolynomialFeatures(degree=1), LinearRegression())
model_forex.fit(X_blend, y_forex)

# Model 2: Feedstock Future Projections (Time Series Regression)
feedstocks = [
    "Sugarcane_Million_Litres", "Maize_Million_Litres", 
    "Rice_Million_Litres", "2G_Biomass_Million_Litres", "3G_Algae_Million_Litres"
]
feedstock_models = {}

X_years = df_hist[['Year']]
for feed in feedstocks:
    # 2G and 3G follow exponential/polynomial scaling paths in policy mandates
    deg = 2 if "2G" in feed or "3G" in feed or "Maize" in feed or "Rice" in feed else 1
    model = make_pipeline(PolynomialFeatures(degree=deg), LinearRegression())
    model.fit(X_years, df_hist[feed])
    feedstock_models[feed] = model

# -------------------------------------------------------------------------
# Streamlit Dashboard UI Layout
# -------------------------------------------------------------------------
st.title("🇮🇳 Ethanol Blending in Petrol: Economic & Environmental Impact App")
st.markdown("""
This data science dashboard models and predicts the environmental and macroeconomic impacts of India's **Ethanol Blended Petrol (EBP)** programme.
Using historical supply data and predictive machine learning, it evaluates carbon footprint reductions, forex changes, and future supply security.
""")

# Sidebar Navigation / Controls
st.sidebar.header("🕹️ Control Dashboard")
app_mode = st.sidebar.radio("Choose App Module", ["Environmental & Economic Simulator", "Future Feedstock Projections"])

if app_mode == "Environmental & Economic Simulator":
    st.header("🌱 Custom Ethanol Blend Impact Simulator")
    
    st.markdown("### Select or Input a Target Blend Level")
    preset = st.radio(
        "Quick Presets:",
        ["Custom Slider", "E10 (10%)", "E20 (20% Target)", "E30 (30%)", "E85 (85% Flex-Fuel)", "E100 (100% Pure Ethanol)"],
        index=2
    )
    
    # Map preset selections to value
    if preset == "E10 (10%)":
        custom_blend = 10.0
    elif preset == "E20 (20% Target)":
        custom_blend = 20.0
    elif preset == "E30 (30%)":
        custom_blend = 30.0
    elif preset == "E85 (85% Flex-Fuel)":
        custom_blend = 85.0
    elif preset == "E100 (100% Pure Ethanol)":
        custom_blend = 100.0
    else:
        custom_blend = st.slider("Select Custom Ethanol Blend Percentage (%)", 1.0, 100.0, 25.0, 0.5)

    # Predictions via ML Model
    predicted_co2 = model_co2.predict(np.array([[custom_blend]]))[0]
    predicted_forex = model_forex.predict(np.array([[custom_blend]]))[0]
    
    # Clamping down values to avoid negative boundaries on ultra-low edge cases
    predicted_co2 = max(0.0, predicted_co2)
    predicted_forex = max(0.0, predicted_forex)

    # Display Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Target Blend Selected", value=f"{custom_blend}%")
    col2.metric(label="Predicted Annual CO₂ Reduction", value=f"{predicted_co2:.2f} MMT")
    col3.metric(label="Est. Annual Forex Import Savings", value=f"${predicted_forex:.2f} Billion")

    # Interactive Plots
    st.markdown("### Historical Trends vs. Modelled Predictions")
    
    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    sns.set_theme(style="whitegrid")
    
    # Plot 1: CO2 Reduction Curve
    sns.regplot(x="Blend_Percentage", y="CO2_Reduction_MMT", data=df_hist, ax=ax[0], color="seagreen", label="Historical Data")
    ax[0].scatter([custom_blend], [predicted_co2], color="red", s=150, zorder=5, label=f"Prediction ({custom_blend}%)")
    ax[0].set_title("Ethanol Blend % vs Annual CO2 Reduction")
    ax[0].set_xlabel("Ethanol Blend in Petrol (%)")
    ax[0].set_ylabel("CO2 Reduction (Million Metric Tonnes)")
    ax[0].legend()
    
    # Plot 2: Forex Savings Curve
    sns.regplot(x="Blend_Percentage", y="Forex_Savings_Billion_USD", data=df_hist, ax=ax[1], color="teal", label="Historical Data")
    ax[1].scatter([custom_blend], [predicted_forex], color="red", s=150, zorder=5, label=f"Prediction ({custom_blend}%)")
    ax[1].set_title("Ethanol Blend % vs Forex Savings")
    ax[1].set_xlabel("Ethanol Blend in Petrol (%)")
    ax[1].set_ylabel("Forex Savings (Billion USD)")
    ax[1].legend()
    
    st.pyplot(fig)
    
    # Data display
    with st.expander("📋 View Underlying Historical Baseline Dataset"):
        st.dataframe(df_hist[["Year", "Blend_Percentage", "CO2_Reduction_MMT", "Forex_Savings_Billion_USD"]], use_container_width=True)

else:
    st.header("🔮 Future Feedstock Production Projections (India)")
    st.markdown("""
    To sustain higher blending targets like E20, E30, or beyond, raw material supply must transform. 
    This engine leverages polynomial trend-fitting to estimate production capacities across **1G (Sugarcane, Maize, Rice)** and advanced **2G & 3G** resources.
    """)
    
    target_year = st.slider("Select Horizon Prediction Year", 2026, 2035, 2030)
    
    # Predict future values
    future_years = np.arange(2026, target_year + 1)
    future_df_list = []
    
    for yr in future_years:
        row = {"Year": yr}
        for feed in feedstocks:
            pred_val = feedstock_models[feed].predict(np.array([[yr]]))[0]
            row[feed] = max(0.0, pred_val) # Prevent negative predictions
        future_df_list.append(row)
        
    df_future = pd.DataFrame(future_df_list)
    df_combined = pd.concat([df_hist[["Year"] + feedstocks], df_future]).reset_index(drop=True)
    
    # Combined Data Visualization
    st.markdown(f"### Production Trajectory up to {target_year} (in Million Litres)")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot each feedstock group
    ax.plot(df_combined["Year"], df_combined["Sugarcane_Million_Litres"], marker='o', label="Sugarcane (1G)", linewidth=2.5)
    ax.plot(df_combined["Year"], df_combined["Maize_Million_Litres"], marker='s', label="Maize (1G)", linewidth=2)
    ax.plot(df_combined["Year"], df_combined["Rice_Million_Litres"], marker='^', label="Rice (1G)", linewidth=2)
    ax.plot(df_combined["Year"], df_combined["2G_Biomass_Million_Litres"], marker='x', label="2G Biomass (Agricultural Residues)", linewidth=2)
    ax.plot(df_combined["Year"], df_combined["3G_Algae_Million_Litres"], marker='d', label="3G Algae (Advanced Biofuels)", linewidth=1.5)
    
    # Visual boundary line between history and prediction
    ax.axvline(x=2025.5, color='red', linestyle='--', alpha=0.7, label='Prediction Horizon Start')
    
    ax.set_title("Feedstock Supply Mix Diversification & Projection Trends", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Ethanol Production Capacity (Million Litres)")
    ax.set_xlim(2015, target_year + 0.5)
    ax.legend(loc="upper left")
    
    st.pyplot(fig)
    
    # Aggregated breakdown table
    st.markdown("### Projected Feedstock Volume Breakdown Table")
    st.dataframe(df_combined.style.format(precision=1), use_container_width=True)
