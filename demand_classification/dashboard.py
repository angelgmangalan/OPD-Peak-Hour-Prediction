"""Streamlit dashboard for OPD demand classification and peak-hour alerts."""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

from utils import (
    OUTPUT_DIR, load_hourly_data, load_forecast_data,
    calculate_thresholds, apply_classification
)

st.set_page_config(
    page_title="OPD Peak-Hour Demand Dashboard",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 OPD Peak-Hour Prediction & Demand Dashboard")
st.caption("Historical patient arrivals, forecast demand categories and potential busy-hour alerts")

@st.cache_data
def get_historical():
    return load_hourly_data()

try:
    historical = get_historical()
except Exception as exc:
    st.error(f"Unable to load the historical hourly dataset: {exc}")
    st.info("Place Member 1's hourly_patient_counts.csv inside the project's data folder.")
    st.stop()

thresholds = calculate_thresholds(historical["patient_count"])
low_q = thresholds["low_threshold"]
high_q = thresholds["high_threshold"]
historical = apply_classification(historical, "patient_count", low_q, high_q)

st.sidebar.header("Dashboard controls")
st.sidebar.write("Historical thresholds are calculated from positive hourly counts.")
st.sidebar.metric("Low-demand boundary (Q1)", f"{low_q:.2f}")
st.sidebar.metric("High-demand boundary (Q3)", f"{high_q:.2f}")
st.sidebar.caption("0 to Q1 = Low; above Q1 to Q3 = Normal; above Q3 = High.")

min_date = pd.to_datetime(historical["datetime"]).min().date()
max_date = pd.to_datetime(historical["datetime"]).max().date()
date_range = st.sidebar.date_input(
    "Historical date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    hist_view = historical[
        historical["datetime"].dt.date.between(start_date, end_date)
    ].copy()
else:
    hist_view = historical.copy()

total = int(hist_view["patient_count"].sum())
average = hist_view["patient_count"].mean() if len(hist_view) else 0
peak_count = int(hist_view["patient_count"].max()) if len(hist_view) else 0
peak_time = (
    hist_view.loc[hist_view["patient_count"].idxmax(), "datetime"].strftime("%d %b %Y, %H:%M")
    if len(hist_view) else "N/A"
)
high_hours = int((hist_view["demand_category"] == "High").sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total patient arrivals", f"{total:,}")
c2.metric("Average patients / hour", f"{average:.2f}")
c3.metric("Highest hourly arrivals", f"{peak_count:,}")
c4.metric("High-demand hours", f"{high_hours:,}")

st.divider()
st.subheader("1. Historical patient demand")

hourly_pattern = hist_view.groupby("hour", as_index=False)["patient_count"].mean()
fig_hour = px.bar(
    hourly_pattern, x="hour", y="patient_count",
    title="Average patient arrivals by hour",
    labels={"hour": "Hour of day", "patient_count": "Average patients"}
)
fig_hour.update_xaxes(dtick=1)
st.plotly_chart(fig_hour, use_container_width=True)

daily_pattern = hist_view.groupby("weekday", as_index=False)["patient_count"].mean()
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
daily_pattern["weekday"] = pd.Categorical(daily_pattern["weekday"], categories=weekday_order, ordered=True)
daily_pattern = daily_pattern.sort_values("weekday")
fig_week = px.bar(
    daily_pattern, x="weekday", y="patient_count",
    title="Average hourly arrivals by weekday",
    labels={"weekday": "Weekday", "patient_count": "Average patients per hour"}
)
st.plotly_chart(fig_week, use_container_width=True)

monthly_pattern = hist_view.groupby("month", as_index=False)["patient_count"].mean()
month_order = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]
monthly_pattern["month"] = pd.Categorical(monthly_pattern["month"], categories=month_order, ordered=True)
monthly_pattern = monthly_pattern.sort_values("month")
fig_month = px.bar(
    monthly_pattern, x="month", y="patient_count",
    title="Average hourly arrivals by month",
    labels={"month": "Month", "patient_count": "Average patients per hour"}
)
st.plotly_chart(fig_month, use_container_width=True)

st.subheader("2. Historical demand classification")
category_counts = (
    hist_view["demand_category"].value_counts()
    .reindex(["Low", "Normal", "High"], fill_value=0)
    .rename_axis("Demand category").reset_index(name="Number of hours")
)
fig_categories = px.pie(
    category_counts, names="Demand category", values="Number of hours",
    title="Historical hours by demand category", hole=0.45,
    color="Demand category",
    color_discrete_map={"Low": "#16A34A", "Normal": "#2563EB", "High": "#DC2626"}
)
st.plotly_chart(fig_categories, use_container_width=True)

with st.expander("View historical classified records"):
    st.dataframe(hist_view[["datetime", "patient_count", "demand_category"]], use_container_width=True)
    st.download_button(
        "Download historical classification CSV",
        data=hist_view.to_csv(index=False).encode("utf-8"),
        file_name="classified_historical_demand.csv",
        mime="text/csv"
    )

st.divider()
st.subheader("3. Future demand forecast")
st.write("Upload Member 2's forecast CSV. It must include a date/time column and a predicted patient-count column. Lower and upper prediction limits are optional but recommended.")
forecast_upload = st.file_uploader("Upload forecast CSV", type=["csv"])

forecast = None
try:
    if forecast_upload is not None:
        forecast = load_forecast_data(uploaded_file=forecast_upload)
    else:
        forecast = load_forecast_data()
except Exception as exc:
    st.error(f"Forecast file could not be read: {exc}")

if forecast is None:
    st.info("No forecast file has been loaded yet. The historical dashboard is ready. Upload Member 2's forecast CSV when it is available.")
else:
    forecast = apply_classification(forecast, "predicted", low_q, high_q)
    has_interval = "lower_bound" in forecast.columns and "upper_bound" in forecast.columns

    if has_interval:
        forecast["upper_bound_category"] = apply_classification(
            forecast, "upper_bound", low_q, high_q
        )["demand_category"]
        forecast["potential_busy_warning"] = (
            (forecast["demand_category"] != "High") &
            (forecast["upper_bound_category"] == "High")
        )
    else:
        forecast["potential_busy_warning"] = False

    forecast["alert"] = forecast.apply(
        lambda row: "HIGH DEMAND" if row["demand_category"] == "High"
        else ("POTENTIAL BUSY HOUR" if row["potential_busy_warning"] else "No alert"),
        axis=1
    )

    f1, f2, f3 = st.columns(3)
    f1.metric("Forecast hours", len(forecast))
    f2.metric("Predicted high-demand hours", int((forecast["demand_category"] == "High").sum()))
    f3.metric("Potential busy-hour warnings", int(forecast["potential_busy_warning"].sum()))

    plot_df = forecast.copy()
    fig_forecast = go.Figure()
    if has_interval:
        fig_forecast.add_trace(go.Scatter(
            x=plot_df["datetime"], y=plot_df["upper_bound"],
            mode="lines", line=dict(width=0), showlegend=False, name="Upper limit"
        ))
        fig_forecast.add_trace(go.Scatter(
            x=plot_df["datetime"], y=plot_df["lower_bound"],
            mode="lines", line=dict(width=0), fill="tonexty",
            fillcolor="rgba(59,130,246,0.18)", name="Prediction interval"
        ))
    fig_forecast.add_trace(go.Scatter(
        x=plot_df["datetime"], y=plot_df["predicted"],
        mode="lines+markers", name="Predicted patients",
        line=dict(color="#2563EB", width=2)
    ))
    fig_forecast.update_layout(
        title="Forecasted hourly patient arrivals",
        xaxis_title="Date and hour", yaxis_title="Predicted patients"
    )
    st.plotly_chart(fig_forecast, use_container_width=True)

    color_map = {"Low": "#16A34A", "Normal": "#2563EB", "High": "#DC2626"}
    fig_demand = px.scatter(
        forecast, x="datetime", y="predicted", color="demand_category",
        color_discrete_map=color_map, title="Forecast demand classification",
        labels={"datetime": "Date and hour", "predicted": "Predicted patients",
                "demand_category": "Demand"}
    )
    st.plotly_chart(fig_demand, use_container_width=True)

    alerts = forecast[forecast["alert"] != "No alert"].copy()
    if not alerts.empty:
        st.warning(f"{len(alerts)} forecast hour(s) need attention.")
        st.dataframe(alerts[["datetime", "predicted"] +
                            (["lower_bound", "upper_bound"] if has_interval else []) +
                            ["demand_category", "alert"]], use_container_width=True)
    else:
        st.success("No high-demand or potential busy-hour alerts in the loaded forecast.")

    with st.expander("View all forecast classifications"):
        st.dataframe(forecast, use_container_width=True)

    st.download_button(
        "Download classified forecast CSV",
        data=forecast.to_csv(index=False).encode("utf-8"),
        file_name="classified_forecasts.csv",
        mime="text/csv"
    )
    if not alerts.empty:
        st.download_button(
            "Download peak-hour alerts CSV",
            data=alerts.to_csv(index=False).encode("utf-8"),
            file_name="peak_hour_alerts.csv",
            mime="text/csv"
        )

st.caption("Note: Demand categories are based on historical thresholds. Prediction intervals represent model uncertainty and are not guarantees.")
