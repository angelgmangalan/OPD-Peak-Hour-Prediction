from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

def find_existing_file(candidates):
    """Return the first existing project data file from a list of candidate names."""
    for name in candidates:
        path = DATA_DIR / name
        if path.exists():
            return path
    return None

def load_hourly_data(file_path=None):
    """Load Member 1's hourly patient-count file and standardise its columns."""
    path = Path(file_path) if file_path else find_existing_file([
        "hourly_patient_counts.csv",
        "hourly_patient_count.csv",
        "hourly_counts.csv",
    ])
    if path is None or not path.exists():
        raise FileNotFoundError(
            "Could not find hourly_patient_counts.csv. Put Member 1's file in the project's data folder."
        )

    df = pd.read_csv(path)
    datetime_col = next(
        (c for c in ["datetime_hour", "datetime", "hour_datetime", "timestamp"] if c in df.columns),
        None,
    )
    count_col = next(
        (c for c in ["patient_count", "hourly_patient_count", "count", "patients"] if c in df.columns),
        None,
    )
    if datetime_col is None or count_col is None:
        raise ValueError(
            "Hourly file must contain a datetime column (e.g. datetime_hour) "
            "and a patient count column (e.g. patient_count). "
            f"Found columns: {list(df.columns)}"
        )

    df = df.rename(columns={datetime_col: "datetime", count_col: "patient_count"})
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df["patient_count"] = pd.to_numeric(df["patient_count"], errors="coerce")
    df = df.dropna(subset=["datetime", "patient_count"]).copy()
    df["patient_count"] = df["patient_count"].clip(lower=0)
    df["patient_count"] = df["patient_count"].round().astype(int)
    df = df.sort_values("datetime").drop_duplicates(subset=["datetime"], keep="last")
    df["date"] = df["datetime"].dt.date.astype(str)
    df["hour"] = df["datetime"].dt.hour
    df["weekday"] = df["datetime"].dt.day_name()
    df["month"] = df["datetime"].dt.month_name()
    return df.reset_index(drop=True)

def load_forecast_data(uploaded_file=None, file_path=None):
    """Load and standardise Member 2's forecast file."""
    if uploaded_file is not None:
        raw = pd.read_csv(uploaded_file)
    else:
        path = Path(file_path) if file_path else find_existing_file([
            "hourly_forecasts.csv",
            "forecast_results.csv",
            "predictions.csv",
            "forecasting_results.csv",
        ])
        if path is None or not path.exists():
            return None
        raw = pd.read_csv(path)

    datetime_col = next(
        (c for c in ["datetime_hour", "datetime", "timestamp", "forecast_datetime", "date_time"] if c in raw.columns),
        None,
    )
    predicted_col = next(
        (c for c in ["predicted", "predicted_count", "prediction", "forecast", "y_pred", "predicted_patients"] if c in raw.columns),
        None,
    )
    if datetime_col is None or predicted_col is None:
        raise ValueError(
            "Forecast file needs a date/time column and a predicted patient-count column. "
            f"Found columns: {list(raw.columns)}"
        )

    rename = {datetime_col: "datetime", predicted_col: "predicted"}
    lower_col = next((c for c in ["lower_bound", "lower", "lower_limit", "lower_prediction_limit", "prediction_lower"] if c in raw.columns), None)
    upper_col = next((c for c in ["upper_bound", "upper", "upper_limit", "upper_prediction_limit", "prediction_upper"] if c in raw.columns), None)
    if lower_col:
        rename[lower_col] = "lower_bound"
    if upper_col:
        rename[upper_col] = "upper_bound"

    df = raw.rename(columns=rename)
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    for col in ["predicted", "lower_bound", "upper_bound"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["datetime", "predicted"]).copy()
    for col in ["predicted", "lower_bound", "upper_bound"]:
        if col in df.columns:
            df[col] = df[col].clip(lower=0)
    df = df.sort_values("datetime").drop_duplicates(subset=["datetime"], keep="last")
    df["date"] = df["datetime"].dt.date.astype(str)
    df["hour"] = df["datetime"].dt.hour
    return df.reset_index(drop=True)

def calculate_thresholds(historical_counts):
    """
    Calculate thresholds from positive historical hourly counts.
    Zero-arrival hours are retained as Low demand but excluded from percentile
    calculation so overnight zeroes do not force both thresholds close to zero.
    """
    values = pd.to_numeric(pd.Series(historical_counts), errors="coerce").dropna()
    values = values[values > 0]
    if values.empty:
        return {"low_threshold": 0.0, "high_threshold": 0.0, "method": "No positive historical counts"}

    q1 = float(values.quantile(0.25))
    q3 = float(values.quantile(0.75))
    return {
        "low_threshold": q1,
        "high_threshold": q3,
        "method": "25th and 75th percentiles of positive historical hourly counts",
    }

def classify_values(values, low_threshold, high_threshold):
    """Assign Low, Normal, or High using the historical thresholds."""
    s = pd.to_numeric(pd.Series(values), errors="coerce")
    labels = []
    for value in s:
        if pd.isna(value):
            labels.append("Unknown")
        elif value <= low_threshold:
            labels.append("Low")
        elif value <= high_threshold:
            labels.append("Normal")
        else:
            labels.append("High")
    return pd.Series(labels, index=s.index)

def apply_classification(df, value_column, low_threshold, high_threshold):
    result = df.copy()
    result["demand_category"] = classify_values(
        result[value_column], low_threshold, high_threshold
    )
    return result
