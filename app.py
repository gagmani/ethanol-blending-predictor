import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR

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
    years = np.arange(2015, 2026)
    blend_pct = np.array([1.5, 2.0, 3.8, 4.2, 5.0, 6.2, 8.1, 10.0, 11.5, 13.0, 15.0])
    
    co2_reduction_mmt = blend_pct * 2.4 + np.random.normal(0, 0.5, len(years))
    forex_savings_billion_usd = blend_pct * 0.32 + np.random.normal(0, 0.1, len(years))
    
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
# Dynamic Machine Learning Model Factory
# -------------------------------------------------------------------------
def get_model(algo_name):
    if algo_name == "Linear Regression (Straight Line)":
        return make_pipeline(PolynomialFeatures(degree=1), LinearRegression())
    elif algo_name == "Polynomial Regression (Degree 2 - Curve)":
        return make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
    elif algo_name == "Polynomial Regression (Degree 3 - High Curve)":
        return make_pipeline(PolynomialFeatures(degree=3), LinearRegression())
    elif algo_name == "Decision Tree":
        return DecisionTreeRegressor(random_state=42)
    elif algo_name == "Random Forest":
        return RandomForestRegressor(n_estimators=100, random_state=42)
    elif algo_name == "Support Vector Regression (SVR)":
        return SVR(kernel='rbf', C=100, gamma='scale')

# -------------------------------------------------------------------------
# Streamlit Dashboard UI Layout
# -------------------------------------------------------------------------
st.title("🇮🇳 Ethanol Blending in Petrol: Economic & Environmental Impact App")
st.markdown("""
This data science dashboard models and predicts the environmental and macroeconomic impacts of India's **Ethanol Blended Petrol (EBP)** programme.
""")

# Sidebar Navigation / Controls
st.sidebar.header("🕹️ Control Dashboard")
app_mode = st.sidebar.radio("Choose App Module", ["Environmental & Economic Simulator", "Future Feedstock Projections"])

st.sidebar.header("⚙️ Machine Learning Settings")
ml_algorithm = st.sidebar.selectbox(
    "Select Prediction Algorithm",
    [
        "Linear Regression (Straight Line)",
        "Polynomial Regression (Degree 2 - Curve)",
        "Polynomial Regression (Degree 3 - High Curve)",
        "Decision Tree",
        "Random Forest",
        "Support Vector Regression (SVR)"
    ],
    index=1
)

if app_mode == "Environmental & Economic Simulator":
    st.header("🌱 Custom Ethanol Blend Impact Simulator")
    
    # Train Models dynamically based on user selection
    X_blend = df_hist[['Blend_Percentage']]
    model_co2 = get_model(ml_algorithm).fit(X_blend, df_hist['CO2_Reduction_MMT'])
    model_forex = get_model(ml_algorithm).fit(X_blend, df_hist['Forex_Savings_Billion_USD'])
    
    st.markdown("### Select or Input a Target Blend Level")
    preset = st.radio(
        "Quick Presets:",
        ["Custom Slider", "E10 (10%)", "E20 (20% Target)", "E30 (30%)", "E85 (85% Flex-Fuel)", "E100 (100% Pure Ethanol)"],
        index=2
    )
    
    if preset == "E10 (10%)": custom_blend = 10.0
    elif preset == "E20 (20% Target)": custom_blend = 20.0
    elif preset == "E30 (30%)": custom_blend = 30.0
    elif preset == "E85 (85% Flex-Fuel)": custom_blend = 85.0
    elif preset == "E100 (100% Pure Ethanol)": custom_blend = 100.0
    else: custom_blend = st.slider("Select Custom Ethanol Blend Percentage (%)", 1.0, 100.0, 25.0, 0.5)

    # Predictions
    predicted_co2 = max(0.0, model_co2.predict(pd.DataFrame([[custom_blend]], columns=['Blend_Percentage']))[0])
    predicted_forex = max(0.0, model_forex.predict(pd.DataFrame([[custom_blend]], columns=['Blend_Percentage']))[0])

    # Display Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Target Blend Selected", value=f"{custom_blend}%")
    col2.metric(label="Predicted Annual CO₂ Reduction", value=f"{predicted_co2:.2f} MMT")
    col3.metric(label="Est. Annual Forex Import Savings", value=f"${predicted_forex:.2f} Billion")

    # Interactive Plots
    st.markdown("### Historical Trends vs. Modelled Prediction Line")
    
    # Generate continuous values for drawing the prediction line accurately
    x_line = np.linspace(1, max(100, custom_blend), 200).reshape(-1, 1)
    df_line = pd.DataFrame(x_line, columns=['Blend_Percentage'])
    y_co2_line = np.maximum(0, model_co2.predict(df_line))
    y_forex_line = np.maximum(0, model_forex.predict(df_line))

    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    sns.set_theme(style="whitegrid")
    
    # Plot 1: CO2 Reduction Curve
    ax[0].scatter(df_hist["Blend_Percentage"], df_hist["CO2_Reduction_MMT"], color="seagreen", label="Historical Data", zorder=3)
    ax[0].plot(x_line, y_co2_line, color="darkgreen", linestyle="--", label=f"Prediction Line ({ml_algorithm})", zorder=2)
    ax[0].scatter([custom_blend], [predicted_co2], color="red", s=150, zorder=5, label=f"Target ({custom_blend}%)")
    ax[0].set_title("Ethanol Blend % vs Annual CO2 Reduction")
    ax[0].set_xlabel("Ethanol Blend in Petrol (%)")
    ax[0].set_ylabel("CO2 Reduction (MMT)")
    ax[0].legend()
    
    # Plot 2: Forex Savings Curve
    ax[1].scatter(df_hist["Blend_Percentage"], df_hist["Forex_Savings_Billion_USD"], color="teal", label="Historical Data", zorder=3)
    ax[1].plot(x_line, y_forex_line, color="darkblue", linestyle="--", label=f"Prediction Line ({ml_algorithm})", zorder=2)
    ax[1].scatter([custom_blend], [predicted_forex], color="red", s=150, zorder=5, label=f"Target ({custom_blend}%)")
    ax[1].set_title("Ethanol Blend % vs Forex Savings")
    ax[1].set_xlabel("Ethanol Blend in Petrol (%)")
    ax[1].set_ylabel("Forex Savings (Billion USD)")
    ax[1].legend()
    
    st.pyplot(fig)

else:
    st.header("🔮 Future Feedstock Production Projections (India)")
    st.markdown("Estimate production capacities using your selected Machine Learning algorithm.")
    
    target_year = st.slider("Select Horizon Prediction Year", 2026, 2035, 2030)
    
    # Train Models dynamically based on user selection for Feedstocks
    feedstocks = [
        "Sugarcane_Million_Litres", "Maize_Million_Litres", 
        "Rice_Million_Litres", "2G_Biomass_Million_Litres", "3G_Algae_Million_Litres"
    ]
    feedstock_models = {}
    X_years = df_hist[['Year']]
    
    for feed in feedstocks:
        model = get_model(ml_algorithm)
        model.fit(X_years, df_hist[feed])
        feedstock_models[feed] = model
        
    # Predict future values
    future_years = np.arange(2026, target_year + 1)
    future_df_list = []
    for yr in future_years:
        row = {"Year": yr}
        for feed in feedstocks:
            pred_val = feedstock_models[feed].predict(pd.DataFrame([[yr]], columns=['Year']))[0]
            row[feed] = max(0.0, pred_val) 
        future_df_list.append(row)
        
    df_future = pd.DataFrame(future_df_list)
    df_combined = pd.concat([df_hist[["Year"] + feedstocks], df_future]).reset_index(drop=True)
    
    # Year-on-Year Growth Comparisons Display
    st.markdown(f"### Growth Comparison: Baseline (2025) vs Target ({target_year})")
    metric_cols = st.columns(3)
    
    # Calculate difference for top 3 feedstocks as an example
    val_2025_sugar = df_hist.iloc[-1]['Sugarcane_Million_Litres']
    val_tgt_sugar = df_future.iloc[-1]['Sugarcane_Million_Litres'] if not df_future.empty else val_2025_sugar
    metric_cols[0].metric(label=f"Sugarcane (2025 ➔ {target_year})", value=f"{val_tgt_sugar:.0f} ML", delta=f"{val_tgt_sugar - val_2025_sugar:.0f} ML")

    val_2025_maize = df_hist.iloc[-1]['Maize_Million_Litres']
    val_tgt_maize = df_future.iloc[-1]['Maize_Million_Litres'] if not df_future.empty else val_2025_maize
    metric_cols[1].metric(label=f"Maize (2025 ➔ {target_year})", value=f"{val_tgt_maize:.0f} ML", delta=f"{val_tgt_maize - val_2025_maize:.0f} ML")

    val_2025_2g = df_hist.iloc[-1]['2G_Biomass_Million_Litres']
    val_tgt_2g = df_future.iloc[-1]['2G_Biomass_Million_Litres'] if not df_future.empty else val_2025_2g
    metric_cols[2].metric(label=f"2G Biomass (2025 ➔ {target_year})", value=f"{val_tgt_2g:.0f} ML", delta=f"{val_tgt_2g - val_2025_2g:.0f} ML")

    # Combined Data Visualization
    st.markdown(f"### Production Trajectory Modelled via {ml_algorithm}")
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot historical lines (solid)
    for feed, marker, label in zip(
        feedstocks, 
        ['o', 's', '^', 'x', 'd'], 
        ["Sugarcane (1G)", "Maize (1G)", "Rice (1G)", "2G Biomass", "3G Algae"]
    ):
        ax.plot(df_hist["Year"], df_hist[feed], marker=marker, color=sns.color_palette("tab10")[feedstocks.index(feed)], label=f"{label} (Historical)")
        
        # Plot future prediction line (dashed straight/exponential line based on model)
        if not df_future.empty:
            # combine last point of hist with future to connect the line
            df_connector = pd.concat([df_hist.iloc[-1:], df_future])
            ax.plot(df_connector["Year"], df_connector[feed], linestyle="--", color=sns.color_palette("tab10")[feedstocks.index(feed)])

    ax.axvline(x=2025.5, color='red', linestyle=':', alpha=0.7, label='Prediction Horizon Start (2026+)')
    
    ax.set_title(f"Feedstock Supply Projections to {target_year}", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Ethanol Production Capacity (Million Litres)")
    
    # Ensure X-axis displays integers for years properly
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    
    st.pyplot(fig)
