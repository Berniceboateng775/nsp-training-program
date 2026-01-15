# Car Price Prediction

This project presents a comprehensive regression analysis aimed at predicting vehicle prices based on various attributes. The study utilizes a dataset of automobile listings to investigate the relationship between independent variables such as vehicle age, mileage, horsepower, and brand, and the dependent variable, price. The primary objective is to develop and evaluate a Linear Regression model implemented from first principles.

## Methodology

The analysis follows a structured workflow:

1.  **Data Acquisition and Preprocessing:**
    -   Ingestion of the raw dataset.
    -   Data cleaning procedures, including handling missing values, standardizing string formats, and type conversion.
    -   One-hot encoding of categorical variables (`brand`, `fuel_type`, `transmission`) and label encoding of binary features (`accident`, `clean_title`).

2.  **Feature Engineering:**
    -   Transformation of raw features into numerical inputs suitable for regression analysis.
    -   Derivation of new variables, such as `Vehicle Age` from model years.
    -   Feature Selection based on correlation analysis.

3.  **Model Implementation:**
    -   Development of a Linear Regression algorithm from scratch to demonstrate an understanding of the underlying mathematical principles.
    -   Utilization of the Normal Equation ($(X^T X)^{-1} X^T y$) for precise parameter estimation.

4.  **Evaluation:**
    -   Assessment of model performance using quantitative metrics: Root Mean Squared Error (RMSE), Mean Absolute Error (MAE), and Coefficient of Determination ($R^2$).
    -   Visual analysis of predicted versus actual prices to assess goodness of fit.

## Results & Evaluation

The Linear Regression model, trained on features such as mileage, vehicle age, horsepower, and encoded categorical attributes, yielded the following performance metrics on the validation dataset:

*   **Coefficient of Determination ($R^2$):** **0.8161**
    *   *Interpretation:* The model explains approximately 81.6% of the variance in the target variable (price), indicating a strong predictive capability.
*   **Root Mean Squared Error (RMSE):** **0.3144**
    *   *Interpretation:* On the log-transformed price scale, the deviation is approximately 0.31. This suggests the model's predictions are generally consistent with actual market values.
*   **Mean Absolute Error (MAE):** **0.2325**
    *   *Interpretation:* The average magnitude of errors in the predictions roughly corresponds to a 23% difference from the actual values when converted back from the logarithmic scale.

### Feature Importance Analysis

Correlation analysis prior to training highlighted the most significant determinants of vehicle price:

1.  **Horsepower (HP):** Exhibited the strongest positive correlation, confirming that performance is a primary driver of value.
2.  **Vehicle Age & Mileage:** Both demonstrated strong negative correlations, quantitatively verifying the impact of depreciation and wear.
3.  **Specific Brands:** Encoded features for luxury brands (e.g., Porsche) showed positive correlations, while mass-market equivalents showed neutral or negative tendencies.
4.  **Accident History:** The presence of reported accidents (`accident_encoded`) showed a clear negative impact on valuation.

## Tools and Technologies

The analysis utilizes the Python programming language and the following scientific computing libraries:
*   **Pandas:** For data manipulation and analysis.
*   **NumPy:** For numerical computing and matrix operations.
*   **Matplotlib/Seaborn:** For data visualization.
