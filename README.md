# Car Price Prediction

This project presents a comprehensive regression analysis aimed at predicting vehicle prices based on various attributes. The study utilizes a dataset of automobile listings to investigate the relationship between independent variables such as vehicle age, mileage, horsepower, and brand, and the dependent variable, price. The primary objective is to develop and evaluate a Linear Regression model implemented from first principles.

## Methodology

The analysis follows a structured workflow:

1.  **Data Acquisition and Preprocessing:**
    -   Ingestion of the raw dataset.
    -   Data cleaning procedures, including handling missing values, standardizing string formats, and type conversion.
    -   Detection and treatment of outliers to ensure model robustness.

2.  **Feature Engineering:**
    -   Transformation of raw features into numerical inputs suitable for regression analysis.
    -   Derivation of new variables, such as `Vehicle Age` from model years.
    -   Extraction of quantitative metrics like `Horsepower` from unstructured text fields.

3.  **Model Implementation:**
    -   Development of a Linear Regression algorithm from scratch to demonstrate an understanding of the underlying mathematical principles.
    -   Utilization of the Normal Equation and/or Gradient Descent for parameter estimation.

4.  **Evaluation:**
    -   Assessment of model performance using quantitative metrics, specifically Root Mean Squared Error (RMSE).
    -   Visual analysis of predicted versus actual prices to assess goodness of fit.

## Preliminary Findings

Initial exploratory data analysis suggests significant correlations between price and several key features:

*   **Vehicle Age:** Demonstrates a negative correlation with price, consistent with depreciation trends.
*   **Mileage:** Shows an inverse relationship with value, indicating higher usage correlates with lower market prices.
*   **Performance Metrics:** attributes such as horsepower appear to have a positive influence on vehicle valuation.



## Tools and Technologies

The analysis utilizes the Python programming language and the following scientific computing libraries:
*   **Pandas:** For data manipulation and analysis.
*   **NumPy:** For numerical computing and matrix operations.
*   **Matplotlib/Seaborn:** For data visualization.
