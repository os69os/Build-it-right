# Build It Right! (!ابنيها صح)

Welcome to **Build It Right**, an application designed to help you improve your energy efficiency. This tool allows you to input various parameters related to your house design and provides recommendations to improve energy efficiency based on predicted cooling and heating loads.

## Installation

Clone repo and install requirements.txt

```bash
git clone https://github.com/os69os/Build-it-right.git  # clone
cd Build-it-right
pip install -r requirements.txt  # install
```

## Features

- Input house dimensions and design features
- Predict cooling and heating loads using pre-trained PyCaret regression models
- Provide recommendations to improve energy efficiency
- Visualize energy loads and total energy consumption

# Dataset overview

the dataset was collected from Singapore 

## Key Details:

- Total Entries: The dataset contains 15357 entries, each representing a building.
- Columns: There are 17 columns in the dataset:
  - Width: building Width
  - Length: building Length
  - Height: building Height
  - Orientation: the orientation of the building is measured at an angle that rotates clockwise from the north
  - Window_Ratio: the percentage of windows in the building
  - Skylight_Ratio: the percentage of the light penetration from upper canopy above the open space
  - Area: building area
  - Court_Length: Court Length
  - Court_Width: Width of the court
  - Form_Factor: shape of the building block as a 3D block
  - Surface_Volume_Ratio: An adjective that reflects the shape of a building block
  - Cooling_Load: the load required during a year for cooling
  - Heating_Load:	the load required during a year for heating
  - Shape_Box: the building shape
  - Shape_L: the building shape
  - Shape_O: the building shape
  - Shape_U: the building shape

# Model Overview

1. **Introduction:**
   The model aims to analyze housing data to predict heating and cooling loads. It employs various machine learning techniques to achieve this.

2. **Data Preprocessing:**
   - The model imports necessary libraries (`pandas`, `numpy`, `seaborn`, `matplotlib.pyplot`) and reads the housing data from a CSV file into a Pandas DataFrame.
   - Initial exploration of the dataset is performed with methods like `head()`, `shape`, `describe()`, and `info()` to understand its structure and contents.
   - Unnecessary columns like 'Unnamed: 0', 'Image', 'ThreeD', and others are dropped from the DataFrame.
   - Missing values in the 'Skylight_Ratio' column are filled with zeros.
   - Categorical variables like 'Shape' are converted into dummy variables using one-hot encoding.
   - Outliers in numeric features are detected and handled using techniques like Box-Cox transformation and capping.

3. **Exploratory Data Analysis (EDA):**
   - Correlation analysis is performed using a heatmap to understand the relationships between variables.

4. **Feature Scaling:**
   - Robust scaling is applied to features using `RobustScaler` from scikit-learn to handle varying ranges and outliers.

5. **Predictive Models:**
   - For predicting Total Load, various regression models including Linear Regression, Polynomial Regression, Decision Tree, Random Forest, Gradient Boosting, SVR, and XGBoost are trained and evaluated.
   - Learning curves are plotted to visualize model performance and identify potential issues like overfitting or underfitting.
   - Hyperparameter tuning is performed for Random Forest, Gradient Boosting, and XGBoost using techniques like GridSearchCV and RandomizedSearchCV.

6. **Model Evaluation and Selection:**
   - Models are evaluated based on metrics like Mean Squared Error (MSE), Root Mean Squared Error (RMSE), Mean Absolute Error (MAE), R-squared (R2), and Adjusted R-squared.
   - The best-performing models are saved for future use.

7. **AutoML (Automated Machine Learning):**
   - PyCaret library is used for automating the machine learning workflow for predicting Heating Load and Cooling Load separately.
   - Models are compared, tuned, and finalized using PyCaret's functionalities.
   - The final models are saved for both Heating Load and Cooling Load prediction tasks.

8. **Learning Curves:**
   - Learning curves are plotted to visualize the performance of the finalized models for both Heating Load and Cooling Load prediction.

9. **Model Saving and Loading:**
   - The finalized models are saved as pickle files for future use.
   - The saved models are loaded to verify their correctness.

# Conclusion

The **Build It Right** application presents a comprehensive approach to improving energy efficiency in buildings through predictive modeling and recommendations. By leveraging housing data, the application predicts heating and cooling loads using various machine learning techniques. 

The dataset, sourced from Singapore, provides key insights into building characteristics and energy consumption patterns. With 14 informative columns, including dimensions, orientation, and load requirements, it offers a robust foundation for analysis.

The model overview outlines a structured methodology, from data preprocessing to model evaluation and selection. Notably, the incorporation of exploratory data analysis, feature scaling, and predictive modeling techniques ensures a holistic understanding and accurate predictions of energy loads.

Furthermore, the application demonstrates versatility through the utilization of both traditional regression models and automated machine learning (AutoML) with PyCaret. This approach not only enhances prediction accuracy but also streamlines the modeling process, making it accessible to users with varying levels of expertise.

Overall, **Build It Right** stands as a valuable tool for individuals and organizations seeking to optimize energy efficiency in building design and operation. Through data-driven insights and actionable recommendations, it empowers users to make informed decisions towards sustainable and eco-friendly practices.
