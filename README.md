# Predicting Customer Churn 
The goal was simple: **Build a model to predict churn, but more importantly, understand the *story* behind the data.**
Here is how I went about it, what I found, and the results I got!

---

## 1. What I Did (The Process)
*   **Data Cleaning:** I started by tidying things up. I standardized column names (made them all lowercase and snake_case for sanity) and fixed some annoying missing values in the `TotalCharges` column (turns out blank spaces aren't numbers!).
*   **Exploratory Data Analysis (EDA):** This was the fun part. I went through the columns one by one—literally!—to see what was going on. I visualized everything from `Gender` and `Tenure`to `PaymentMethod`.
    *   *Cool Find:* I realized that people with **Month-to-Month contracts** and **Fiber Optic internet** were way more likely to leave. 
    *   *Another one:* New customers (low tenure) are the most fragile. If they stick around for a year, they are usually loyal for good.
*   **Feature Engineering:** Machines don't understand words like "Yes" or "No", so I converted all the text data into numbers (0s and 1s). I also used **One-Hot Encoding** for things like Payment Method to make sure the model treated them fairly.
*   **Scaling:** Since `Tenure` (0-70 months) and `MonthlyCharges` ($20-$120) had totally different ranges, I scaled them to be between 0 and 1 so the model wouldn't get confused.

## 2. Building the Model 

I chose **Logistic Regression** for this task. Why? Because it's interpretable! It doesn't just say "Churn" or "No Churn"; it gives me a *probability* (e.g., "There's an 80% chance this person leaves"). This is super useful for business decisions.

I split the data: **80% for training** (teaching the model) and **20% for testing** (checking if it actually works).

## 3. The Results

*   **Accuracy:** **82.19%**
    *  Overall, my model guessed correctly 8 out of 10 times. Not bad
    
*   **ROC AUC Score:** **0.8615 (or 86%)**
    *  This is the real star of the show. An AUC of 0.86 is considered **excellent**. It means if you pick a random churner and a random loyal customer, my model has an **86% chance** of correctly ranking the churner higher. It's really good at distinguishing between the two groups.

*   **The Confusion Matrix:**
    *   I correctly identified **222** people who were going to leave (True Positives).
    *   I correctly identified **892** happy customers who stayed (True Negatives).
    *   The model is pretty balanced and doesn't just guess "No Churn" for everyone.

## 4. Key Takeaways

If I were presenting this to the marketing team, here is what I'd say:
1.  **Watch out for Fiber Optic users:** They are paying more, but they are leaving faster. Maybe the service quality isn't matching the price?
2.  **Lock them in:** Month-to-month contracts are dangerous. We should incentivize 1-year or 2-year deals.
3.  **The first few months are critical:** Most churn happens early. We need a better onboarding process for new users.

---

