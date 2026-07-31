import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


df = pd.read_csv("ghg_features.csv")

st.markdown("""
<style>

/* Style metric cards */
div[data-testid="stMetric"]{
    background: #1f2937;
    padding: 20px;
    border-radius: 15px;
    border-left: 6px solid #22c55e;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}

/* Metric labels */
div[data-testid="stMetricLabel"]{
    color: #d1d5db !important;
    font-size: 18px;
    font-weight: 600;
}

/* Metric values */
div[data-testid="stMetricValue"]{
    color: #ffffff !important;
    font-size: 34px;
    font-weight: bold;
}

/* Delta (increase/decrease) */
div[data-testid="stMetricDelta"]{
    color: #4ade80 !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

.main {
    background-color:#f8fafc;
}

h1 {
    color: blue;
    font-family: 'Trebuchet MS', sans-serif;
}

h2 {
    color:#166534;
}

[data-testid="metric-container"] {
    background:white;
    border-radius:15px;
    padding:20px;
    box-shadow:2px 2px 10px rgba(0,0,0,0.1);
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
section[data-testid="stSidebar"] {
    background-color:dark blue;
}
</style>
""", unsafe_allow_html=True)


st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "Historical Trends",
        "Country Profile",
        "Forecasts",
        "About"
    ]
)


if page == "Overview":
    st.title("🌍 Global Climate Change & CO₂ Emissions Dashboard")

    st.markdown("""
    This interactive dashboard presents a comprehensive analysis of global greenhouse gas emissions using historical climate data and machine learning forecasting models.
    
    **Dataset:** Our World in Data CO₂ Dataset (owid-co2-dataset) 
    **Models:** Linear Regression | Random Forest | ETS(A,Ad,N)
    """)
    st.markdown("""
    <h3 style="color:#0284c7;">
    Historical analysis and future forecasting of greenhouse gas emissions
    </h3>
    """, unsafe_allow_html=True)

    latest_year = df["year"].max()
    latest_data = df[df["year"] == latest_year]

    total_co2 = latest_data["co2"].sum()
    countries = df["country"].nunique()

    base_1990 = df[df["year"] == 1990]["co2"].sum()

    percentage_change = ((total_co2-base_1990)/base_1990)*100

    c1,c2,c3 = st.columns(3)
    
    c1.metric("Latest Global CO₂",f"{total_co2:,.2f} Mt")
    c2.metric("Change Since 1990",f"{percentage_change:.2f}%")
    c3.metric("Countries Analysed",countries)
    
    global_trend = df.groupby("year")["co2"].sum().reset_index()

    fig = px.line(
        global_trend,
        x="year",
        y="co2",
        title="Global CO₂ Emissions Over Time",
        labels={"co2": "CO₂ Emissions (Mt)", "year": "Year"},)

    st.plotly_chart(fig, use_container_width=True)
    
    st.info(
    "This dashboard was developed as part of a Climate Change and CO₂ Emissions Analysis project to study historical emission patterns and evaluate forecasting models for future emission trends.")


elif page == "Historical Trends":
    st.title(" Historical Trends")
    countries = st.multiselect(
        "Select Countries",
        sorted(df["country"].unique()),
        default=[
            "China",
            "India",
            "United States"
        ]
    )

    trend_df = df[
        df["country"].isin(countries)
    ]

    fig = px.line(
        trend_df,
        x="year",
        y="co2",
        color="country",
        title="Historical CO₂ Emissions"
    )
    st.plotly_chart(fig,use_container_width=True)

    st.subheader("GHG Emissions by Gas Type")

    possible_gases = [
        "co2",
        "methane",
        "nitrous_oxide",
        "total_ghg",
        "ghg"
    ]

    available_gases = [
        col for col in possible_gases
        if col in df.columns
    ]

    gases = st.multiselect(
        "Select Gas Type",
        available_gases,
        default=available_gases
    )
    
    if gases:
        gas_df = (
            df.groupby("year")[gases]
            .sum()
            .reset_index()
        )

        gas_df = gas_df.melt(
            id_vars="year",
            var_name="Gas",
            value_name="Emission"
        )

        fig2 = px.area(
            gas_df,
            x="year",
            y="Emission",
            color="Gas",
            title="Stacked Area Chart - GHG Contribution"
        )
        st.plotly_chart(fig2,use_container_width=True)

    else:
        st.warning("No greenhouse gas columns found in dataset.")

elif page == "Country Profile":

    st.title("Country Profile")

    country = st.selectbox(
        "Select Country",
        sorted(df["country"].unique())
    )

    country_df = df[
        df["country"] == country
    ].copy()

    country_df = country_df.sort_values(
        "year"
    )

    country_df["YoY_change"] = (
        country_df["co2"]
        .pct_change()*100
    )

    tab1,tab2,tab3,tab4 = st.tabs(
        [
            "Emissions",
            "Per Capita",
            "YoY Change",
            "Statistics"
        ]
    )
    with tab1:
        fig = px.line(
            country_df,
            x="year",
            y="co2",
            title=f"{country} CO₂ Emissions",
            markers=True
        )
        st.plotly_chart(fig,use_container_width=True)

    with tab2:
        fig = px.line(
            country_df,
            x="year",
            y="co2_per_capita",
            title=f"{country} CO₂ Per Capita",
            markers=True
        )
        st.plotly_chart(fig,use_container_width=True)

    with tab3:
        fig = px.bar(
            country_df,
            x="year",
            y="YoY_change",
            title="Year-on-Year Change (%)"
        )

        st.plotly_chart(fig,use_container_width=True)



    with tab4:
        latest = country_df.iloc[-1]
        a,b,c = st.columns(3)
        a.metric("Latest CO₂",f"{latest['co2']:.2f}")
        b.metric("Per Capita",f"{latest['co2_per_capita']:.2f}")
        c.metric("Latest Year",int(latest["year"]))
        
        stats = pd.DataFrame({
            "Metric":[
                "Maximum CO₂",
                "Minimum CO₂",
                "Average CO₂",
                "Year Range"
            ],
            "Value":[
                country_df["co2"].max(),
                country_df["co2"].min(),
                country_df["co2"].mean(),
                f"{country_df.year.min()}-{country_df.year.max()}"
            ]
        })
        st.dataframe(stats,hide_index=True)


elif page == "Forecasts":

    st.title("ETS(A,Ad,N) Forecast")
    df = pd.read_csv("ghg_features.csv")

    forecast_df = pd.read_csv("forecast_df.csv")

    country = st.selectbox(
        "Select Country",
        sorted(forecast_df["Country"].unique())
    )

    hist = df[df["country"] == country].sort_values("year")


    fc = forecast_df[forecast_df["Country"] == country].sort_values("Year")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=hist["year"],
            y=hist["co2"],
            mode="lines",
            name="Historical CO₂"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=fc["Year"],
            y=fc["Forecast_CO2"],
            mode="lines+markers",
            name="ETS Forecast"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=fc["Year"],
            y=fc["Upper_95_CI"],
            mode="lines",
            line=dict(width=0),
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=fc["Year"],
            y=fc["Lower_95_CI"],
            mode="lines",
            fill="tonexty",
            fillcolor="rgba(0,100,255,0.2)",
            line=dict(width=0),
            name="95% Confidence Interval"
        )
    )

    fig.update_layout(
        title=f"{country} CO₂ Emissions (1990–2043)",
        xaxis_title="Year",
        yaxis_title="CO₂ Emissions",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Forecast Summary")
    st.dataframe(fc, use_container_width=True)

elif page == "About":
    st.title("About")
    st.markdown("""

## Dataset
- Our World in Data CO₂ Dataset (owid-co2-data)

## Methodology
- Data Cleaning
- Exploratory Data Analysis
- Feature Engineering
- Regression Models
- ETS(A,Ad,N) Forecasting

## Tools
Python  
Pandas  
Plotly  
Streamlit  

## Internship Attribution : Indian Statistical Institute (ISI)

## Built by : Haindavi Paladugu
""")