# Predicting Peak Consultation Hours in Hospital OPDs 
Healthcare project for analysing and forecasting hourly hospital OPD patient demand.

The main objective is to understand patient arrival patterns, predict future patient demand, identify busy periods, which will help in better hospital resource planning.

## 1. Dataset Description

The project uses the **HospitalOPD** dataset published on Mendeley Data.

Dataset description:
- **Records:** 62,422 patient-event records
- **Observation period:** April 2024 – April 2026
- **Activities:** Appointment, Consultation, Laboratory, Imaging and Pharmacy
- **Privacy:** The dataset description states that patient identifiers are anonymized.

**Dataset source:**  
https://data.mendeley.com/public-api/zip/j2hd2239dr/download/1

## 2. Project Objectives

1. Analyse historical OPD patient arrival patterns.
2. Identify peak patient arrival hours and busy days.
3. Prepare hourly patient-arrival counts.
4. Develop machine learning and time-series forecasting models.
5. Evaluate model performance using MAE and RMSE.
6. Estimate prediction intervals and evaluate their coverage.
7. Support hospital workload planning.

## 3. Data Processing

The dataset is processed to prepare it for analysis and forecasting.

The planned processing steps include:

- Checking missing values and duplicate records.
- Converting timestamp columns into datetime format.
- Extracting date, hour, weekday and month.
- Aggregating patient arrivals into hourly counts.
- Checking unusual timestamps and inconsistent records.

## 4. Forecasting Models

The models are compared:

- **Same Hour Last Week:** Uses patient arrivals from the same hour in the previous week.
- **Three-Week Average:** Calculates the average arrivals from the corresponding hours of the previous three weeks.
- **SARIMAX:** A statistical time-series forecasting model.
- **Random Forest:** A machine learning model that combines predictions from multiple decision trees.

## 5. Model Evaluation

The forecasting models are evaluated using:

- **MAE (Mean Absolute Error):** Measures the average absolute difference between actual and predicted patient counts.
- **RMSE (Root Mean Squared Error):** Measures prediction error while giving more weight to larger errors.
- **Prediction Interval Coverage:** Measures the percentage of actual patient counts falling inside the predicted lower and upper limits.

Random Forest achieved the lowest MAE and RMSE among the compared models and was selected as the preferred forecasting model.

## 6. Prediction Intervals

Prediction intervals represent a possible range around the predicted patient count.

For Random Forest, the lower and upper limits are calculated using the 5th and 95th percentiles of calibration-period prediction errors, separately for each hour of the day.

The observed coverage was:

- Random Forest: 80.1%
- SARIMAX: 89.1%

SARIMAX achieved coverage closer to the nominal 90% target.

## 7. Demand Classification
The predicted hourly patient counts were classified into three demand categories using the first and third quartiles.

Q1 (25th percentile): 2 patients

Q3 (75th percentile): 16 patients

| Category | Patient Count per Hour |
|---|---:|
| Low Demand | 0–2 |
| Normal Demand | >2–16 |
| High Demand | >16 |

These classification rules were applied to 672 forecasted hours.

## 8. Key Findings

The demand classification produced the following results:

| Demand Category | Number of Hours | Percentage |
|---|---:|---:|
| Low Demand | 276 | 41.1% |
| Normal Demand | 292 | 43.5% |
| High Demand | 104 | 15.5% |
| **Total** | **672** | **100%** |

### Additional Findings

| Finding | Result |
|---|---|
| High-Demand Hours | 104 hours |
| Additional Potential Busy-Hour Warnings | 122 hours |
| Highest Predicted Patient Arrival | 38.87 patients |
| Date of Highest Predicted Arrival | 16 March 2026 |
| Time of Highest Predicted Arrival | 06:00 |

**Note:** The 122 additional potential busy-hour warnings identified using prediction intervals are separate from the 104 hours classified as High Demand.

## 9. Dashboard (in Streamlit)
<img width="1912" height="867" alt="image" src="https://github.com/user-attachments/assets/dd1b8fcb-bde3-4edd-b94c-8d9f33b0b262" />

Streamlit link: https://opd-peak-hour-prediction-babpcreismecqjf7jsjie5.streamlit.app/

## 10. Conclusion

In this it uses machine learning and statistical forecasting methods to predict hourly patient arrivals in hospital OPDs. Random Forest performed best in terms of MAE and RMSE, while SARIMAX achieved prediction-interval coverage closer to the 90% target.

Demand classification makes the predictions easier to understand by identifying Low, Normal, and High Demand periods. The dashboard helps hospital administrators plan staffing and resources during busy hours.

## 11. Limitations and Future Improvements

Forecast accuracy depends on the quality and availability of historical data.

Unexpected events may cause sudden changes in patient arrivals.

Prediction intervals do not guarantee that actual patient counts will fall within the predicted range.

Future work can include more recent data and additional factors that influence patient arrivals.

The forecasting models can be improved through further tuning and evaluation.

## 12. Tools and Technologies

Python

Pandas

NumPy

Scikit-learn

Statsmodels

Matplotlib

Jupyter Notebook

Dashboard

## 13. Project Outputs
The project produces hourly patient arrival forecasts, prediction intervals, demand categories and peak-hour warnings. These outputs support the monitoring and planning of patient demand in hospital OPDs.

