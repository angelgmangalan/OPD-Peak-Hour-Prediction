# Predicting Peak Consultation Hours in Hospital OPDs 
Healthcare project for analysing and forecasting hourly hospital OPD patient demand.

The main objective is to understand patient arrival patterns, predict future patient demand, identify busy periods, which will help in better hospital resource planning.

## 2. Dataset Description

The project uses the **HospitalOPD** dataset published on Mendeley Data.

Dataset description:
- **Records:** 62,422 patient-event records
- **Observation period:** April 2024 – April 2026
- **Activities:** Appointment, Consultation, Laboratory, Imaging and Pharmacy
- **Privacy:** The dataset description states that patient identifiers are anonymized.

**Dataset source:**  
https://data.mendeley.com/public-api/zip/j2hd2239dr/download/1

## 3. Project Objectives

1. Analyse historical OPD patient arrival patterns.
2. Identify peak patient arrival hours and busy days.
3. Prepare hourly patient-arrival counts.
4. Develop machine learning and time-series forecasting models.
5. Evaluate model performance using MAE and RMSE.
6. Estimate prediction intervals and evaluate their coverage.
7. Support hospital workload planning.

## 4. Data Processing

The dataset is processed to prepare it for analysis and forecasting.

The planned processing steps include:

- Checking missing values and duplicate records.
- Converting timestamp columns into datetime format.
- Extracting date, hour, weekday and month.
- Aggregating patient arrivals into hourly counts.
- Checking unusual timestamps and inconsistent records.

## 5. Forecasting Models

The models are compared:

- **Same Hour Last Week:** Uses patient arrivals from the same hour in the previous week.
- **Three-Week Average:** Calculates the average arrivals from the corresponding hours of the previous three weeks.
- **SARIMAX:** A statistical time-series forecasting model.
- **Random Forest:** A machine learning model that combines predictions from multiple decision trees.

## 6. Model Evaluation

The forecasting models are evaluated using:

- **MAE (Mean Absolute Error):** Measures the average absolute difference between actual and predicted patient counts.
- **RMSE (Root Mean Squared Error):** Measures prediction error while giving more weight to larger errors.
- **Prediction Interval Coverage:** Measures the percentage of actual patient counts falling inside the predicted lower and upper limits.

Random Forest achieved the lowest MAE and RMSE among the compared models and was selected as the preferred forecasting model.

## 7. Prediction Intervals

Prediction intervals represent a possible range around the predicted patient count.

For Random Forest, the lower and upper limits are calculated using the 5th and 95th percentiles of calibration-period prediction errors, separately for each hour of the day.

The observed coverage was:

- Random Forest: 80.1%
- SARIMAX: 89.1%

SARIMAX achieved coverage closer to the nominal 90% target.

## 8. Limitations

- It not confirms that the dataset is real or synthetic data.
- Unusual appointment times and timestamp patterns require further investigation.
- Forecasting performance depends on the quality and completeness of historical records.
- Predicted patient arrivals are estimates and may differ from actual hospital demand.
- To get better results can also include other models as well

## 9. Tools and Technologies

- Python
- Pandas
- NumPy
- Matplotlib
- Scikit-learn
- Statsmodels
- Jupyter Notebook

## 10. Expected Outcome

The project aims to provide OPD patient arrival patterns and forecast hourly patient demand. These predictions may help healthcare facilities plan staffing, manage workloads and allocate resources more effectively.

## 11. Dashboard (in Streamlit)
<img width="1912" height="867" alt="image" src="https://github.com/user-attachments/assets/dd1b8fcb-bde3-4edd-b94c-8d9f33b0b262" />

Streamlit link: https://opd-peak-hour-prediction-babpcreismecqjf7jsjie5.streamlit.app/
