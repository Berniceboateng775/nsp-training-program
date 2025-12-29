### **DATA MANIPULATION AND ANALYSIS**
### **CAR PRICE PREDICTION**
### **DATE: 22TH DECEMBER, 2025**

### **ABOUT DATASET**
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

### **DATA PREPROCESSING**
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

### **EXPLORING THE BRAND COLUMN**
I found that the brand column contained several niche manufacturers (like Plymouth, Maybach, Suzuki and Smart) that appeared only once or twice in the dataset. To prevent the model from overfitting to these extremely rare cases, I applied a frequency threshold of 20. Any brand appearing fewer than 20 times was grouped into a generic "Other" category. This grouping ensures that our machine learning model focuses on the general relationship between brand and price for the majority of the market, rather than memorizing individual outliers.

### **EXPLORING THE MODEL COLUMN**
I noticed the model column had nearly 2,000 unique values which is way too many for a dataset of this size. The issue was that it included specific trim levels (like "Palisade SEL" vs. "Palisade Limited") instead of just the car name. To fix this and help our model find better patterns, I simplified them into just their base model names and grouped the really rare ones into an "Other" category.

### **EXPLORING THE MODEL YEAR COLUMN**
When I looked at the stats for the model_year column, everything appeared pretty normal. The cars range from 1974 to 2024, with an average model year around 2015. Since these numbers made sense and there weren't any outliers (like a car from the year 1800 or 2050), I decided not to touch this column for now. 

### **EXPLORING THE MILEAGE COLUMN**
The mileage column needed a bit more work. First, I noticed the spelling was slightly off ("milage"), so I renamed it to mileage to be correct. The values were stored as text strings with "mi." and commas (e.g "51,000 mi."), which meant I couldn't do any math on them. I wrote a quick function to strip out those characters and converted the whole column into integers.
Once I had the raw numbers, I checked for outliers using the IQR (Interquartile Range) method. I found about 69 cars with unusually high mileage that didn't fit the general pattern of the data. To keep my model accurate, I removed these extreme cases, which trimmed the dataset down slightly but left me with a much cleaner set of 3,940 cars.

### **EXPLORING THE FUEL TYPE COLUMN**
The fuel_type column had a mix of useful categories and some garbage data. I found values like –, not supported, and NaN (missing) mixed in with standard types like Gasoline, Hybrid, and E85 Flex Fuel.
I standardized this by converting all the meaningless placeholders (–, not supported) into true missing values (NaN). Since I couldn't just leave holes in the data, I filled these missing spots with the mode (the most common fuel type), which was Gasoline. This kept the dataset complete without throwing away valuable rows.

### **EXPLORING THE ENGINE COLUMN**
The engine column contained mixed text data (e.g., "3.8L V6 24V GDI DOHC"). I extracted three key features from this text: Horsepower (HP), Displacement (Litres), and Cylinders.
I noticed that while many rows were missing HP or Liters, some were also missing the Cylinder count. I decided to tackle the Cylinders first by filling any missing values with the mode (the most common cylinder count).
Once every car had a valid Cylinder count, I used that to fill the missing Horsepower and Liters. For example, if a car was a V6, I filled its missing HP with the average HP of all other V6 cars. Because I had already filled the Cylinders column, this method worked for every single row, leaving me with a complete, clean dataset and no missing values.

### **EXPLORING THE TRANSMISSION COLUMN**
I created a mapping function using keywords to bucket these into four distinct categories:

**Automatic:** (Standard automatics, A/T)
**Manual:** (Stick shifts, M/T)
**CVT:** (Continuously Variable Transmissions)
**Dual Clutch:** (High-performance automated manuals like DCT/PDK)
This reduced the dimensionality from 61 unique strings down to just 4 clean categories, making it much easier for the machine learning model to interpret. Non-standard values with negligible counts (like "Other") were merged into the majority class (Automatic) to ensure data stability.

### **EXPLORING THE EXTERIOR AND INTERIOR COLOR COLUMN**
The columns exterior_color and interior_color were filled with many different colours
I standardized these into simple base colors. It scanned each name for specific keywords:

**Black:** Covered everything from "Obsidian" to "Ebony" to "Midnight."
**White:** Caught "Alpine," "Fuji," "Pearl," etc.
**Silver/Gray:** Combined "Metallic," "Steel," "Granite," etc.
And so on for Blue, Red, Green, etc.

### **EXPLORING THE ACCIDENT COLUMN**
The accident column originally contained long, descriptive strings like "At least 1 accident or damage reported."
I simplified this into a clean binary category:

**Accident:** For any car with a reported history of damage.
None: For cars with "None reported."
For missing values, I assumed "no news is good news" and filled them with "None," as it's the standard industry practice to assume a clean title unless flagged otherwise. This left me with a clear split: about 75% of the cars have a clean history (None), while about 25% have at least one reported accident.

### **EXPLORING THE CLEAN TITLE COLUMN**
The clean_title column was mostly filled with "Yes," but had a significant number of missing values . 
Therefore, I treated this as a binary feature:
I assumed that any missing value meant the title was not clean (or at least not verified).
I filled the NaN values with "No".

### **EXPLORING THE PRICE COLUMN (THE TARGET)**
Finally, I cleaned the target variable, price. It was stored as text with currency symbols (e.g., "$54,598"). I stripped the dollar signs and commas and converted the entire column to integers.
Since this is what we want to predict, it was crucial to remove extreme outliers that could skew the model. I used the IQR method again to define a "reasonable price range" and removed the few extreme high-end outliers. This left me with a stable, cleaner dataset ready for training.

## **CAR PRICE VISUALIZATION**
### **VISUALIZING THE PRICE DISTRIBUTION**
I plotted a histogram to see how the car prices were spread out.
**Findings:** The majority of cars are in the affordable to mid-range bracket (roughly $15,000 to $45,000).
**Insight:** There is a long tail of more expensive cars leading up to our $98,000 limit, but they are much rarer. This confirms that our cleaner dataset represents the "common market" well.

### **CORRELATION HEATMAP (WHAT DRIVES THE PRICE?)**
I checked which numbers matter most.
**Horsepower & Year:** These had the strongest positive link. meaning newer and more powerful cars cost significantly more.
**Mileage:** This had a strong negative link. meaning The more miles a car has, the less it’s worth. I confirmed online and its true 
![alt text](<Screenshot 2025-12-29 114734.png>)

### **CATEGORICAL ANALYSIS (Comparing Groups)**
I used boxplots to see how different features change the price tag.
**Brand vs Price:** Porsche was the clear winner, with the highest median price (around $50k) and a huge range. Land Rover and Mercedes-Benz followed. Interestingly, Toyota and Ford are much more affordable but have many outliers (expensive special models).
**Transmission:** Automatic and Dual Clutch cars have the highest median prices (around $30k+), likely because modern luxury cars use these. Manual cars are surprisingly competitive but have a wider spread, while CVTs are the cheapest option on average.
**Fuel Type:** Plug-in Hybrids and Diesel engines are the most expensive categories given their efficiency and durability. E85 Flex Fuel cars are significantly cheaper than everything else.
