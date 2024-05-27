import streamlit as st # type: ignore
from pycaret.regression import load_model, predict_model # type: ignore
import base64
import pandas as pd # type: ignore
import numpy as np # type: ignore
import plotly.graph_objects as go # type: ignore
import matplotlib.pyplot as plt # type: ignore

# Load the dataset
file_path = '/Users/Ash/Desktop/capstone-project/Houses_data_cleaned.csv'  # Adjust the path to your dataset
data = pd.read_csv(file_path)

# Load materials dataset
materials_file_path = '/Users/Ash/Desktop/capstone-project/new materials v1.0.xlsx'  # Adjust the path to your materials dataset
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
        </style>
        """,
        unsafe_allow_html=True
    )

#  Function to load models
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
    area = length * width
    volume = length * width * height
    surface_area = 2 * (length * width + length * height + width * height)
    form_factor = volume / surface_area
    return area, form_factor


 #Function to get user inputs from sidebar
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


def recommend_materials(house_efficiency, cooling_load, heating_load):
    type_insulated = "Cooling" if heating_load > cooling_load else "Heating"
    
    if house_efficiency <= 30:
        effectiveness_range = (90, 100)
    elif 30 < house_efficiency <= 65:
        effectiveness_range = (80, 90)
    else:
        effectiveness_range = (70, 80)
    
    # Filter materials within the effectiveness range and matching the insulation type
    suitable_materials = materials[
        (materials['Effectiveness_per'] >= effectiveness_range[0]) &
        (materials['Effectiveness_per'] < effectiveness_range[1]) &
        (materials['Type_Insulated'] == type_insulated)
    ]

    if len(suitable_materials) >= 2:
        # Select the two most effective materials
        best_materials = suitable_materials.nlargest(2, 'Effectiveness_per')
        best_material = best_materials.iloc[0]
        best_cost_material = suitable_materials.loc[suitable_materials['Installation_Cost_$_sqm'].idxmin()]
    else:
        best_material = None
        best_cost_material = None
    
    return best_material, best_cost_material

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

def calculate_maintenance_cost(height, length, width, shape, material_maintenance_cost_per_sqm):
    if shape == 'Box':
        wall_areas = [height * length, height * width] * 2
    elif shape == 'L':
        wall_areas = [height * length, height * width, height * (length / 2), height * (width / 2)]
    elif shape == 'O':
        wall_areas = [height * length, height * width] * 4
    elif shape == 'U':
        wall_areas = [height * length] * 2 + [height * width] * 2 + [height * (length / 2)] * 4
    
    total_wall_area = sum(wall_areas)
    maintenance_cost = total_wall_area * material_maintenance_cost_per_sqm
    return maintenance_cost



def plot_maintenance_costs(height, length, width, shape, materials):
    years = range(1, 11)
    plt.figure(figsize=(10, 6))
    
    for material in materials:
        material_name = material['Material']
        maintenance_cost_per_sqm = material['Maintenance_Cost_$_sqm']
        annual_maintenance_cost = calculate_maintenance_cost(height, length, width, shape, maintenance_cost_per_sqm)
        
        costs = [annual_maintenance_cost * year for year in years]
        
        plt.plot(years, costs, marker='o', linestyle='-', label=f"{material_name} (Cost per sqm: ${maintenance_cost_per_sqm:.2f})")

    plt.xlabel('Years')
    plt.ylabel('Total Maintenance Cost ($)')
    plt.title('Maintenance Cost Over Time for Different Materials')
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)
    plt.clf()  # Clear the figure to avoid overlapping plots



    
            
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
                            <h3>Total Load</h3>
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

                best_material, best_cost_material = recommend_materials(house_efficiency, cooling_load, heating_load)

                if best_material is not None and best_cost_material is not None:
                    height, length, width = input_data['Height'], input_data['Length'], input_data['Width']
                    shape = 'Box' if input_data['Shape_Box'] else 'L' if input_data['Shape_L'] else 'O' if input_data['Shape_O'] else 'U'

                    best_material_cost = calculate_installation_cost(height, length, width, shape, best_material['Installation_Cost_$_sqm'])
                    best_cost_material_cost = calculate_installation_cost(height, length, width, shape, best_cost_material['Installation_Cost_$_sqm'])
                    
                    # Display best material information
                    tabs = st.tabs(["Best Material", "Best Cost Material"])
                    
                    with tabs[0]:
                        st.subheader("Best Material efficiency Details")
                        st.markdown(f"**Material:** {best_material['Material']}")
                        st.markdown(f"**Installation Cost:** ${best_material_cost:.2f}")
                        st.markdown(f"**Applications:** {best_material['Applications']}")
                        st.markdown(f"**Additional Info:** {best_material['Additional_info']}")
                        st.markdown(f"**Installation Time:** {best_material['Installation_Time']}")
                        st.markdown(f"**Lifespan:** {best_material['Lifespan']} years")

                        best_material_table = pd.DataFrame({
                            'Metric': ['Installation Cost', 'Maintenance Cost'],
                            'Value': [best_material_cost, best_material['Maintenance_Cost_$_sqm'] * height * width]
                        })
                        st.table(best_material_table)

                    with tabs[1]:
                        st.subheader("Best Material Cost Details")
                        st.markdown(f"**Material:** {best_cost_material['Material']}")
                        st.markdown(f"**Installation Cost:** ${best_cost_material_cost:.2f}")
                        st.markdown(f"**Applications:** {best_cost_material['Applications']}")
                        st.markdown(f"**Additional Info:** {best_cost_material['Additional_info']}")
                        st.markdown(f"**Installation Time:** {best_cost_material['Installation_Time']}")
                        st.markdown(f"**Lifespan:** {best_cost_material['Lifespan']} years")

                        best_cost_material_table = pd.DataFrame({
                            'Metric': ['Installation Cost', 'Maintenance Cost'],
                            'Value': [best_cost_material_cost, best_cost_material['Maintenance_Cost_$_sqm'] * height * width]
                        })
                        st.table(best_cost_material_table)

                    st.write("### Maintenance Cost Over Time")
                    materials_to_plot = [best_material, best_cost_material]
                    plot_maintenance_costs(height, length, width, shape, materials_to_plot)

                else:
                    st.warning("No suitable materials found for the given efficiency range.")
                

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
                        
                         - The **House Efficiency** is calculated based on normalized cooling and heating loads using max and min values. A higher efficiency percentage indicates a more energy-efficient house.                    ''')
                   

            else:
                st.error("Failed to make predictions. Please check the model files.")

if __name__ == "__main__":
    main()
    
    
  
    