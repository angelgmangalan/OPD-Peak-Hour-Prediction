"""Identify forecasted peak hours and potential busy-hour warnings."""
import argparse
from utils import OUTPUT_DIR, load_hourly_data, load_forecast_data, calculate_thresholds, apply_classification

def main():
    parser = argparse.ArgumentParser(description="Identify OPD forecast peak hours.")
    parser.add_argument("--hourly", help="Path to historical hourly patient-count CSV.")
    parser.add_argument("--forecast", help="Path to Member 2's forecast CSV.")
    args = parser.parse_args()

    historical = load_hourly_data(args.hourly)
    thresholds = calculate_thresholds(historical["patient_count"])
    forecast = load_forecast_data(file_path=args.forecast)

    if forecast is None:
        raise FileNotFoundError(
            "Member 2's forecast CSV was not found. Add it to data/ or provide --forecast PATH."
        )

    result = apply_classification(
        forecast, "predicted",
        thresholds["low_threshold"], thresholds["high_threshold"]
    )

    if "upper_bound" in result.columns:
        result["upper_bound_category"] = apply_classification(
            result, "upper_bound",
            thresholds["low_threshold"], thresholds["high_threshold"]
        )["demand_category"]
        result["potential_busy_warning"] = (
            (result["demand_category"] != "High") &
            (result["upper_bound_category"] == "High")
        )
    else:
        result["upper_bound_category"] = "Not available"
        result["potential_busy_warning"] = False

    result["peak_hour"] = result["demand_category"].eq("High")
    result["alert"] = result.apply(
        lambda row: "HIGH DEMAND" if row["peak_hour"]
        else ("POTENTIAL BUSY HOUR" if row["potential_busy_warning"] else "No alert"),
        axis=1
    )

    output = OUTPUT_DIR / "peak_hour_alerts.csv"
    result.to_csv(output, index=False)

    print("\nPEAK-HOUR SUMMARY")
    print(f"Forecast hours analysed: {len(result)}")
    print(f"High-demand hours: {int(result['peak_hour'].sum())}")
    print(f"Potential busy-hour warnings: {int(result['potential_busy_warning'].sum())}")
    print("\nHighest predicted hours:")
    print(result.nlargest(10, "predicted")[["datetime", "predicted", "demand_category", "alert"]].to_string(index=False))
    print(f"\nSaved: {output}")

if __name__ == "__main__":
    main()
