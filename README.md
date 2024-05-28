# ![Build It Right](images/logo.png) Build It Right! (!ابنيها صح)

Welcome to **Build It Right**, an application designed to help you improve your energy efficiency. This tool allows you to input various parameters related to your house design and provides recommendations to improve energy efficiency based on predicted cooling and heating loads.

## Installation

Clone the repo and install the requirements:

```bash
git clone https://github.com/os69os/Build-it-right.git  # clone
cd Build-it-right
pip install -r requirements.txt  # install
```

To Run the streamlit app use this python command:

```python
streamlit run interface.py
```

## Features

- Input house dimensions and design features
- Predict cooling and heating loads using pre-trained PyCaret regression models
- Provide recommendations to improve energy efficiency
- Visualize energy loads and total energy consumption

## Problem Statement

Energy efficiency in buildings is crucial for reducing environmental impact and operational costs. Predicting energy loads and providing actionable recommendations can significantly enhance the design and functionality of buildings.

## Project Scope and Objectives

The project aims to develop a predictive model that analyzes various building parameters to forecast heating and cooling loads. The objectives include:
- Building and validating multiple predictive models
- Selecting the best-performing model
- Integrating the model into an application that provides energy efficiency recommendations

## Solution Outline

### Overview of the Solution
The solution involves using a combination of traditional regression models and automated machine learning (AutoML) to predict energy loads. PyCaret is utilized for its comprehensive AutoML capabilities, streamlining the modeling process. We chose this approach due to its efficiency in handling diverse datasets and producing accurate predictions.

### Issues Faced and Improvements
- **Data Quality:** Missing values in 'Skylight_Ratio' were filled with zeros, and categorical variables were converted into dummy variables.
- **Outliers:** Handled using Box-Cox transformation and capping.
- **Data Relevance:** The dataset used was not related to Saudi Arabia, which may affect the applicability of the predictions to buildings in that region.
- **Model Selection:** Extensive hyperparameter tuning and model comparison ensured optimal performance.

## Model Section

### Models Tried
- Linear Regression
- Polynomial Regression
- Decision Tree
- Random Forest
- Gradient Boosting
- Support Vector Regression (SVR)
- XGBoost
- LightGBM (final model)

### Baseline Model
The initial model was a simple Linear Regression, which provided a baseline performance to improve upon.

### Model Improvement
Improvements were made by:
- Applying robust feature scaling
- Conducting extensive hyperparameter tuning
- Using ensemble methods like Random Forest and Gradient Boosting
- Leveraging AutoML with PyCaret for automated model optimization

### Final Model Architecture
The final model architecture for both heating and cooling load predictions is LightGBM, chosen for its high performance and efficiency.

## Dataset

### Description
This dataset, sourced from a private source in Singapore, includes 15,357 entries with 17 columns describing various building characteristics and energy loads. Special thanks to Dr. Asma Alshargabi and Abdulbasid Almhady for providing the data.

Additionally, we have collected a material dataset detailing the effectiveness percentages, applications, costs, and other characteristics of various insulation materials.

### Key Details

- Total Entries: The dataset contains 15357 entries, each representing a building.
- Columns: There are 17 columns in the dataset:
  - Width: building Width.
  - Length: building Length.
  - Height: building Height.
  - Orientation: the orientation of the building is measured at an angle that rotates clockwise from the north.
  - Window_Ratio: the percentage of windows in the building.
  - Skylight_Ratio: the percentage of the light penetration from upper canopy above the open space.
  - Area: building area.
  - Court_Length: Court Length.
  - Court_Width: Width of the court.
  - Form_Factor: A calculated value representing the shape of the house, considering its dimensions.
  - Surface_Volume_Ratio: The ratio of the house's surface area to its volume, indicating compactness.
  - Cooling_Load: The cooling load required to maintain a comfortable indoor temperature.
  - Heating_Load: The heating load required to maintain a comfortable indoor temperature.
  - Total_Load: The total energy load (cooling + heating) required to maintain a comfortable indoor temperature, represented as a float value.
  - Shape_Box: the building shape.
  - Shape_L: the building shape.
  - Shape_O: the building shape.
  - Shape_U: the building shape.
    
### Feature Engineering
- One-hot encoding for categorical variables
- Handling missing values and outliers
- Creating new features like 'Form_Factor' and 'Surface_Volume_Ratio'

### Issues and Augmentation
- Missing values were imputed
- No significant data augmentation was necessary

## Training and Validation

### Final Model Performance
The LightGBM model showed superior performance in predicting both heating and cooling loads.

### Evaluation Metrics
- Mean Squared Error (MSE)
- Root Mean Squared Error (RMSE)
- Mean Absolute Error (MAE)
- R-squared (R2)

These metrics were chosen for their ability to provide a comprehensive understanding of the model's accuracy and reliability.

## Demo

### Final Product
**Build It Right** provides an interface for users to input building parameters and receive detailed predictions and recommendations for improving energy efficiency. Visualizations help users understand energy loads and consumption patterns.

## Future Work

### Data Expansion
Collect more data to improve the accuracy and reliability of predictions.

### Future Enhancements
- Allow location input for tailored recommendations on house shape, orientation, and materials.
- Incorporate environmental impact data to recommend the most sustainable materials.

By leveraging data-driven insights and advanced predictive modeling, **Build It Right** empowers users to make informed decisions towards sustainable building practices.
