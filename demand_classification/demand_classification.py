"""Create historical and forecast demand categories for the OPD project."""
import argparse
from utils import (
    OUTPUT_DIR, load_hourly_data, load_forecast_data,
    calculate_thresholds, apply_classification
)

def main():
    parser = argparse.ArgumentParser(description="Classify OPD hourly patient demand.")
    parser.add_argument("--hourly", help="Path to Member 1's hourly patient-count CSV.")
    parser.add_argument("--forecast", help="Optional path to Member 2's forecast CSV.")
    args = parser.parse_args()

    historical = load_hourly_data(args.hourly)
    thresholds = calculate_thresholds(historical["patient_count"])

    historical_result = apply_classification(
        historical, "patient_count",
        thresholds["low_threshold"], thresholds["high_threshold"]
    )
    historical_output = OUTPUT_DIR / "classified_historical_demand.csv"
    historical_result.to_csv(historical_output, index=False)

    print("\nDEMAND CLASSIFICATION THRESHOLDS")
    print(f"Low threshold (Q1):  {thresholds['low_threshold']:.2f}")
    print(f"High threshold (Q3): {thresholds['high_threshold']:.2f}")
    print(f"Method: {thresholds['method']}")
    print("\nHISTORICAL CATEGORY COUNTS")
    print(historical_result["demand_category"].value_counts().to_string())
    print(f"\nSaved: {historical_output}")

    forecast = load_forecast_data(file_path=args.forecast)
    if forecast is not None:
        forecast_result = apply_classification(
            forecast, "predicted",
            thresholds["low_threshold"], thresholds["high_threshold"]
        )
        if "upper_bound" in forecast_result.columns:
            forecast_result["upper_bound_category"] = apply_classification(
                forecast_result, "upper_bound",
                thresholds["low_threshold"], thresholds["high_threshold"]
            )["demand_category"]
            forecast_result["potential_busy_warning"] = (
                (forecast_result["demand_category"] != "High") &
                (forecast_result["upper_bound_category"] == "High")
            )
        else:
            forecast_result["potential_busy_warning"] = False

        forecast_output = OUTPUT_DIR / "classified_forecasts.csv"
        forecast_result.to_csv(forecast_output, index=False)
        print("\nFORECAST CATEGORY COUNTS")
        print(forecast_result["demand_category"].value_counts().to_string())
        print(f"Saved: {forecast_output}")
    else:
        print("\nForecast file not found. Historical classification is complete.")
        print("Add Member 2's forecast CSV to data/ or upload it in the dashboard later.")

if __name__ == "__main__":
    main()
