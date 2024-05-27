import streamlit as st
from pycaret.regression import load_model, predict_model
import base64
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Load the dataset
file_path = 'Houses_data_cleaned.csv'  # Adjust the path to your dataset
data = pd.read_csv(file_path)

# Load materials dataset
materials_file_path = 'new materials v1.0.xlsx'  # Adjust the path to your materials dataset
materials = pd.read_excel(materials_file_path)

# Constants for normalization (these should be based on your dataset or domain knowledge)
MAX_COOLING_LOAD = 50.36  # Example value, replace with actual max value if available
MIN_COOLING_LOAD = 42.31    # Example value, replace with actual min value if available
MAX_HEATING_LOAD = 1.80   # Example value, replace with actual max value if available
MIN_HEATING_LOAD = 0.29    # Example value, replace with actual min value if available

# Function to add a background image with a dark overlay
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{encoded_string.decode()});
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5); /* Adjust the alpha value to control darkness */
            z-index: -1;
        }}
        .horizontal-values {{
            display: flex;
            justify-content: space-around;
            padding: 10px;
        }}
        .value-box {{
            background-color: rgba(255, 255, 255, 0.8);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            width: 30%;
        }}
        .cooling {{
            color: darkblue;
        }}
        .heating {{
            color: darkred;
        }}
        .total {{
            color: darkgreen;
        }}
        .efficiency {{
            color: darkorange;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Function to load models
def load_model_pycaret(file_path):
    try:
        model = load_model(file_path)
        return model
    except Exception as e:
        st.error(f"Error loading the model: {e}")
        return None

# Function to calculate form factor and area
def calculate_form_factor_and_area(length, width, height):
    if length == 0 or width == 0 or height == 0:
        return 0, 0  # Avoid division by zero by returning 0 for area and form factor
    area = 10.764*length * 10.764*width
    volume = 10.764*length *10.764* width *10.764* height
    surface_area = 2 * (10.764*length *10.764* width +10.764* length *10.764* height +10.764* width *10.764* height)
    form_factor = volume / surface_area
    return area, form_factor

# Function to get user inputs from sidebar
def get_user_inputs():
    st.sidebar.header("House Specifications")
    
    length = st.sidebar.number_input('House Length (m):', min_value=0.1, value=1.0)
    width = st.sidebar.number_input('House Width (m):', min_value=0.1, value=1.0)
    height = st.sidebar.number_input('House Height (m):', min_value=0.1, value=1.0)

    area, form_factor = calculate_form_factor_and_area(length, width, height)

    if area == 0 or form_factor == 0:
        st.sidebar.error("Length, Width, and Height must be greater than zero to calculate Area and Form Factor.")
        return None

    shape = st.sidebar.radio("Choose House Shape", ["BOX Shape", "U Shape", "L Shape", "O Shape"], horizontal=True)
    orientation = st.sidebar.radio("Choose House Orientation", ["North", "East", "West", "South", "North East", "North West", "South East", "South West"], horizontal=True)
    windows_ratio = st.sidebar.slider("Choose Windows Ratio (%)", min_value=10, max_value=40, step=10)

    if shape not in ["L Shape", "U Shape"]:
        skylight_ratio = st.sidebar.slider("Choose Skylight Ratio (%)", min_value=10, max_value=40, step=10)
        skylight_ratio_num = skylight_ratio / 100
    else:
        skylight_ratio_num = 0

    shape_features = {
        'Shape_Box': 1 if shape == "BOX Shape" else 0,
        'Shape_L': 1 if shape == "L Shape" else 0,
        'Shape_O': 1 if shape == "O Shape" else 0,
        'Shape_U': 1 if shape == "U Shape" else 0
    }

    orientation_degrees = {
        "North": 0, "East": 90, "West": 270, "South": 180,
        "North East": 45, "North West": 315, "South East": 135, "South West": 255
    }
    orientation_deg = orientation_degrees[orientation]
    windows_ratio_num = windows_ratio / 100

    return {
        'Width': width,
        'Length': length,
        'Height': height,
        'Area': area, 
        'Window_Ratio': windows_ratio_num, 
        'Skylight_Ratio': skylight_ratio_num, 
        'Orientation': orientation_deg,
        'Form_Factor': form_factor,
        **shape_features
    }

# Function to calculate house efficiency based on cooling and heating loads using max and min normalization
def calculate_house_efficiency(cooling_load, heating_load):
    normalized_cooling_load = (cooling_load - MIN_COOLING_LOAD) / (MAX_COOLING_LOAD - MIN_COOLING_LOAD)
    normalized_heating_load = (heating_load - MIN_HEATING_LOAD) / (MAX_HEATING_LOAD - MIN_HEATING_LOAD)
    efficiency = 100 * (1 - (0.9 * normalized_cooling_load + 0.1 * normalized_heating_load))
    Loss = (100-(max(min(efficiency, 100), 0)))  # Ensure efficiency is between 0 and 100
    return Loss


# Function to recommend materials based on house efficiency and loads
def recommend_materials(house_efficiency, cooling_load, heating_load):
    if house_efficiency > 80:
        # Return the two most effective materials for consistency
        best_materials = materials.nlargest(2, 'Effectiveness_per')
        return best_materials.iloc[0], best_materials.iloc[1]

    type_insulated = "Cooling" if heating_load > cooling_load else "Heating"
    
    if house_efficiency < 30:
        effectiveness_range = (90, 100)
    elif 30 <= house_efficiency <= 65:
        effectiveness_range = (81, 90)
    else:
        effectiveness_range = (70, 80)
    
    # Filter materials
    suitable_materials = materials[
        (materials['Effectiveness_per'] >= effectiveness_range[0]) &
        (materials['Effectiveness_per'] <= effectiveness_range[1]) &
        (materials['Type_Insulated'] == type_insulated)
    ]

    if not suitable_materials.empty:
        best_material = suitable_materials.loc[suitable_materials['Effectiveness_per'].idxmax()]
        best_cost_material = suitable_materials.loc[suitable_materials['Installation_Cost_$_sqft'].idxmin()]
        return best_material, best_cost_material
    else:
        return None, None


# Function to calculate installation cost based on house shape
def calculate_installation_cost(height, length, width, shape, material_cost_per_sqft):
    if shape == 'Box':
        wall_areas = [height * length, height * width] * 2
    elif shape == 'L':
        wall_areas = [height * length, height * width, height * (length / 2), height * (width / 2)]
    elif shape == 'O':
        wall_areas = [height * length, height * width] * 4
    elif shape == 'U':
        wall_areas = [height * length] * 2 + [height * width] * 2 + [height * (length / 2)] * 4
    
    total_wall_area = sum(wall_areas)
    installation_cost = total_wall_area * material_cost_per_sqft
    return installation_cost

# Main Streamlit app function
def main():
    add_bg_from_local('House.jpg')

    cooling_model_path = 'tuned_model_cooling_LGB_FINAL'
    heating_model_path = 'tuned_model_heating_LGB_FINAL'

    cooling_model = load_model_pycaret(cooling_model_path)
    heating_model = load_model_pycaret(heating_model_path)

    st.markdown(
        "<h1 style='text-align: center; font-size: 60px;'>Build It Right</h1>", 
        unsafe_allow_html=True
    )

    st.markdown(
        "<h2 style='text-align: center;'>Energy Efficient Home Design</h2>", 
        unsafe_allow_html=True
    )

    input_data = get_user_inputs()

    if input_data is not None:
        st.header("Results")
        if st.button("Build it"):
            input_df = pd.DataFrame([input_data])

            if cooling_model and heating_model:
                cooling_prediction = predict_model(cooling_model, data=input_df)
                heating_prediction = predict_model(heating_model, data=input_df)

                cooling_load = cooling_prediction['prediction_label'][0]
                heating_load = heating_prediction['prediction_label'][0]
                total_energy = cooling_load + heating_load

                house_efficiency = calculate_house_efficiency(cooling_load, heating_load)

                st.markdown(
                    f"""
                    <div class="horizontal-values">
                        <div class="value-box cooling">
                            <h3>Cooling Load</h3>
                            <p>{cooling_load:.2f} kWh</p>
                        </div>
                        <div class="value-box heating">
                            <h3>Heating Load</h3>
                            <p>{heating_load:.2f} kWh</p>
                        </div>
                        <div class="value-box total">
                            <h3>Total Energy</h3>
                            <p>{total_energy:.2f} kWh</p>
                        </div>
                        <div class="value-box efficiency">
                            <h3>House Loss</h3>
                            <p>{house_efficiency:.2f} %</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                recommended_materials = recommend_materials(house_efficiency, cooling_load, heating_load)

                # Handle the case where only one material is recommended
                if isinstance(recommended_materials, tuple):
                    best_material, best_cost_material = recommended_materials

                    # Calculate installation costs for the best material and the best cost material
                    height, length, width = input_data['Height'], input_data['Length'], input_data['Width']
                    shape = 'Box' if input_data['Shape_Box'] else 'L' if input_data['Shape_L'] else 'O' if input_data['Shape_O'] else 'U'

                    best_material_cost = calculate_installation_cost(height, length, width, shape, best_material['Installation_Cost_$_sqft'])
                    best_cost_material_cost = calculate_installation_cost(height, length, width, shape, best_cost_material['Installation_Cost_$_sqft'])

                    st.write(f"**Best Material: {best_material['Material']}**, Installation Cost: ${best_material_cost:.2f}")
                    st.write(f"**Best Cost Material: {best_cost_material['Material']}**, Installation Cost: ${best_cost_material_cost:.2f}")
                else:
                    best_material = recommended_materials

                    # Calculate installation cost for the single best material
                    height, length, width = input_data['Height'], input_data['Length'], input_data['Width']
                    shape = 'Box' if input_data['Shape_Box'] else 'L' if input_data['Shape_L'] else 'O' if input_data['Shape_O'] else 'U'

                    best_material_cost = calculate_installation_cost(height, length, width, shape, best_material['Installation_Cost_$_sqft'])

                    st.write(f"**Recommended Material: {best_material['Material']}**, Installation Cost: ${best_material_cost:.2f}")

                # Creating and displaying the area chart with specified colors
                chart_data = pd.DataFrame({
                    "cooling load": np.random.randn(20),
                    "heating load": np.random.randn(20),
                    "total load": np.random.randn(20)
                })

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data["cooling load"], fill='tozeroy', name='Cooling Load', line=dict(color='blue')))
                fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data["heating load"], fill='tozeroy', name='Heating Load', line=dict(color='red')))
                fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data["total load"], fill='tozeroy', name='Total Load', line=dict(color='green')))

                st.plotly_chart(fig)

                with st.expander("See Explanation of Results"):
                    st.write('''
                        - The **Cooling Load** represents the amount of energy required to cool your house. A higher value indicates a higher energy requirement for cooling, which means higher energy consumption and potentially higher costs.
                        - If the Cooling Load is between 45.33 and 47.34 kWh, it indicates average energy consumption for cooling.

                        - The **Heating Load** represents the amount of energy required to heat your house. A higher value indicates a higher energy requirement for heating, which means higher energy consumption and potentially higher costs.
                        - If the Heating Load is between 0.86 and 1.24 kWh, it indicates average energy consumption for heating.
                        
                        - The **Total Energy Consumption** is the sum of the cooling and heating loads, representing the overall energy required to maintain a comfortable temperature in your house.
                        
                        - The **House Efficiency** is calculated based on normalized cooling and heating loads using max and min values. A higher efficiency percentage indicates a more energy-efficient house.
                    ''')

            else:
                st.error("Failed to make predictions. Please check the model files.")

if __name__ == "__main__":
    main()
