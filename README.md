# **DATA MANIPULATION AND ANALYSIS**
# **CAR PRICE PREDICTION**
# **DATE: 22TH DECEMBER, 2025**

**ABOUT DATASET**
The dataset contains 4,009 entries, each representing a unique vehicle listing. It includes 12 features that provide insights into various aspects of vehicles:
**Brand & Model**: Specifies the manufacturer and model of the vehicle.
**Model Year**: Indicates the year of manufacture, useful for analyzing depreciation and technological features.
**Mileage**: Represents the distance the vehicle has traveled, an important metric for assessing wear and tear.
**Fuel Type**: Indicates the type of fuel the vehicle uses, such as gasoline, diesel, electric, or hybrid.
**Engine Type**: Details the engine specifications, providing insights into performance and efficiency.
**Transmission**: Shows the type of transmission (automatic, manual, or other variants).
**Exterior & Interior Colors**: Represents the vehicle's aesthetic characteristics.
**Accident History**: Records whether the vehicle has been involved in accidents or sustained damage, important for evaluating its condition and resale value.
**Clean Title**: Indicates whether the vehicle has a clean title, which affects resale value and legal status.
**Price**: The listed price of the vehicle, used as the target variable for prediction.

**DATA PREPROCESSING**
Upon initial exploration, several data quality issues were identified:
1. **Column Names & Consistency**: Some column names and entries were inconsistent in formatting. These needs to be standardized for uniformity. For instance, the column milage will be corrected to mileage.

2. **Data Types**:
•	The price column was stored as an object due to the presence of the dollar sign  and commas. It will converted to a float after removing non-numeric characters.
•	The mileage column will be converted from object to float, with units "mi." removed.

3. **Missing Values**:
•	The clean_title column contained null values. Since all non-null entries were "Yes," it is reasonable to impute missing values as "No."
•	Other columns with missing values include fuel_type (170 missing) and accident (113 missing). These can be handled as follows:
•	Categorical columns (fuel_type, accident): Impute using the or introduce a new category such as "Unknown".
•	Numerical columns (if any were missing): Impute using the median to reduce the effect of extreme values.

**EXPLORING THE BRAND COLUMN**
I found that the brand column contained several niche manufacturers (like Plymouth, Maybach, Suzuki and Smart) that appeared only once or twice in the dataset. To prevent the model from overfitting to these extremely rare cases, I applied a frequency threshold of 20. Any brand appearing fewer than 20 times was grouped into a generic "Other" category. This grouping ensures that our machine learning model focuses on the general relationship between brand and price for the majority of the market, rather than memorizing individual outliers.

**EXPLORING THE MODEL COLUMN**
I noticed the model column had nearly 2,000 unique values which is way too many for a dataset of this size. The issue was that it included specific trim levels (like "Palisade SEL" vs. "Palisade Limited") instead of just the car name. To fix this and help our model find better patterns, I simplified them into just their base model names and grouped the really rare ones into an "Other" category.


