# Build It Right

Welcome to **Build It Right**, an application designed to help you improve your energy efficiency. This tool allows you to input various parameters related to your house design and provides recommendations to improve energy efficiency based on predicted cooling and heating loads.

## Features

- Input house dimensions and design features
- Predict cooling and heating loads using pre-trained PyCaret regression models
- Provide recommendations to improve energy efficiency
- Visualize energy loads and total energy consumption

# Dataset overview

the dataset was collected from Singapore 

## Key Details:

- Total Entries: The dataset contains 15357 entries, each representing a building.
- Columns: There are 14 columns in the dataset:
  - Width: building Width
  - Length: building Length
  - Height: building Height
  - Orientation: the orientation of the building is measured at an angle that rotates clockwise from the north
  - Window_Ratio: the percentage of windows in the building
  - Skylight_Ratio: the percentage of the light penetration from upper canopy above the open space
  - Area: building area
  - Form_Factor: shape of the building block as a 3D block
  - Cooling_Load: the load required during a year for cooling
  - Heating_Load:	the load required during a year for heating
  - Shape_Box: the building shape
  - Shape_L: the building shape
  - Shape_O: the building shape
  - Shape_U: the building shape

## Installation

Clone repo and install requirements.txt

```bash
git clone https://github.com/os69os/T5-capstone.git  # clone
cd T5-capstone
pip install -r requirements.txt  # install
```
