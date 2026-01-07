# Linear Regression Analysis: Ecommerce Customer Spending

This project analyzes customer data from an Ecommerce company to understand what factors most significantly influence the **Yearly Amount Spent** by customers. We used a Linear Regression model to find relationships between customer behavior and their spending habits.

##  Evaluation & Insights

After training the model and evaluating the data, here are the key takeaways:

*   **Length of Membership** is the strongest driver of spending. The longer a customer stays, the more they spend.
*   **Time on App** has a significant positive impact on spending.
*   **Avg. Session Length** also contributes positively but to a lesser extent.
*   **Time on Website** has a negligible effect on spending compared to the mobile app.

## Recommendations

Based on the data, the company should focus its efforts on:
1.  **Mobile App Experience:** Since time on the app correlates strongly with spending, investing in the app's features and usability is crucial.
2.  **Customer Retention:** Strategies to increase membership length (loyalty programs, exclusive percs) will yield the highest return on investment.
3.  **Website Strategy:** The website currently doesn't drive spending as much as the app. It might need a redesign or a shift in strategy to match the app's engagement.

##  Model Performance
The model predicts customer spending with a Root Mean Square Error (RMSE) of approximately **10.19**, indicating a reasonably accurate fit for the data. The residuals are normally distributed, validating the model's reliability.