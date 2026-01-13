# Linear Regression Analysis: Ecommerce Customer Spending

This project analyzes customer data from an Ecommerce company to understand what factors most significantly influence the **Yearly Amount Spent** by customers. We used a Linear Regression model to find relationships between customer behavior and their spending habits.

##  Evaluation & Insights

After training the model and evaluating the data, here are the key takeaways:

*   **Length of Membership** is the strongest driver of spending. The longer a customer stays, the more they spend.
*   **Time on App** has a significant positive impact on spending.
*   **Avg. Session Length** also contributes positively but to a lesser extent.
*   **Time on Website** has a negligible effect on spending compared to the mobile app.

### What Problems Can Machine Learning Solve?
ML is great when:
1. **The rules are too complex** (e.g., recognizing faces)
2. **The rules keep changing** (e.g., social media trends)
3. **You have lots of data** with patterns

#### Common Applications:
- **Prediction:** Will this customer buy?
- **Classification:** Is this email spam?
- **Recommendation:** Netflix movie suggestions
- **Detection:** Fraud detection

### The 3 Main Types of Machine Learning
1. **Supervised Learning** (Most Common)
   - You have labeled data (answers are known)
   - *Example:* Predicting house prices using past sales
2. **Unsupervised Learning**
   - No labels, finding hidden patterns
   - *Example:* Grouping customers by shopping behavior
3. **Reinforcement Learning**
   - Learn by trial and error
   - *Example:* Teaching a robot to walk

## 2. Organizing a Project with CRISP-DM

**CRISP-DM** (Cross-Industry Standard Process for Data Mining) is the checklist for running a successful ML project.

Think of it like **Cooking a Meal** :

1. **Business Understanding** ("What are we hungry for?")
   - Define the goal.
   - *Example:* "We need to reduce customer churn."

2. **Data Understanding** ("Check the fridge")
   - What ingredients (data) do we have?
   - Is the data good quality?

3. **Data Preparation** ("Chopping & Washing") 
   - **Crucial Step:** This takes 80% of the time!
   - Cleaning data, fixing missing values, and formatting.

4. **Modeling** ("Cooking") 
   - Select the cooking method (algorithm).
   - Train the model.

5. **Evaluation** ("Taste Test") 
   - Does it taste good? Does the model solve the problem?
   - If not, go back to step 1 or 3!

6. **Deployment** ("Serving the Meal") 
   - Put the model into the real world for people to use.

## 3. Training & Selecting Models

**Training a Model**.

Imagine you want to teach a computer to predict **House Prices** based on their **Size** (sq ft).

### 1. The Setup (X and y)
- **X (Features):** The data used to predict. (e.g., Size, Number of Rooms)
- **y (Target):** What we want to predict. (e.g., Price)

### 2. Choosing an Algorithm
Think of algorithms as different "tools" to solve the problem:

| Algorithm | Analogy | Best For |
|:--- |:--- |:--- |
| **Linear Regression** | Drawing a straight line through points | Predicting numbers (e.g., Price, Temperature) |
| **Logistic Regression** | Drawing a line to separate two groups | Yes/No questions (e.g., Spam vs Not Spam) |
| **Decision Trees** | A game of "20 Questions" | Complex rules (e.g., "Is it raining?" -> "Yes" -> "Take Umbrella") |

### 3. "Fitting" the Model
This is when the computer actually **learns**.
- command: `model.fit(X, y)`
- It looks at the **X** (size) and **y** (price) and tries to find the math formula that connects them.

## 4. Performing Model Validation

This is the final critical step.

**The Golden Rule of ML:**
> *"Never test your model on the same data you used to train it."*

Why? Because the model will just "memorize" the answers instead of learning the rules. This is called **Overfitting**. (Like a student who memorizes the answers to the practice test but fails the real exam).

### How to Validate Correctly:
We split our data into 3 parts:

1. **Training Set (60%)** ??
   - Used to train the model. ("Study Material")

2. **Validation Set (20%)** ??
   - Used to tune settings and compare models. ("Practice Exam")
   - *Example:* Testing if "Decision Tree" is better than "Linear Regression".

3. **Test Set (20%)** ??
   - Held back until the very end. ("Final Exam")
   - Used to simulate how the model will perform in the real world.
