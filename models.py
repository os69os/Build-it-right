from pycaret.regression import load_model, predict_model  # type: ignore
import pandas as pd  # type: ignore

# Constants for normalization (these should be based on your dataset or domain knowledge)
MAX_COOLING_LOAD = 50.36  # Example value, replace with actual max value if available
MIN_COOLING_LOAD = 42.31  # Example value, replace with actual min value if available
MAX_HEATING_LOAD = 1.80  # Example value, replace with actual max value if available
MIN_HEATING_LOAD = 0.29  # Example value, replace with actual min value if available

# Load the dataset
file_path = 'Houses_data_cleaned.csv'  # Adjust the path to your dataset
data = pd.read_csv(file_path)

# Load materials dataset
materials_file_path = 'new materials v1.0.xlsx'  # Adjust the path to your materials dataset
materials = pd.read_excel(materials_file_path)

# Function to load models
def load_model_pycaret(file_path):
    try:
        model = load_model(file_path)
        return model
    except Exception as e:
        print(f"Error loading the model: {e}")
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

def calculate_installation_cost(height, length, width, shape, material_cost_per_sqm):
    if shape == 'Box':
        wall_areas = [height * length, height * width] * 2
    elif shape == 'L':
        wall_areas = [height * length, height * width, height * (length / 2), height * (width / 2)]
    elif shape == 'O':
        wall_areas = [height * length, height * width] * 4
    elif shape == 'U':
        wall_areas = [height * length] * 2 + [height * width] * 2 + [height * (length / 2)] * 4
    
    total_wall_area = sum(wall_areas)
    installation_cost = int(total_wall_area * material_cost_per_sqm)
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
    import plotly.graph_objects as go
    import streamlit as st  # type: ignore

    years = list(range(1, 11))
    data = []
    
    for material in materials:
        material_name = material['Material']
        maintenance_cost_per_sqm = material['Maintenance_Cost_$_sqm']
        annual_maintenance_cost = calculate_maintenance_cost(height, length, width, shape, maintenance_cost_per_sqm)
        
        costs = [annual_maintenance_cost * year for year in years]
        data.append({
            'Year': years,
            'Cost': costs,
            'Material': material_name
        })

    df = pd.DataFrame({
        'Year': [item for sublist in [d['Year'] for d in data] for item in sublist],
        'Total Maintenance Cost ($)': [item for sublist in [d['Cost'] for d in data] for item in sublist],
        'Material': [item for sublist in [[d['Material']] * 10 for d in data] for item in sublist]
    })

    fig = go.Figure()

    for material in df['Material'].unique():
        material_df = df[df['Material'] == material]
        fig.add_trace(go.Scatter(x=material_df['Year'], y=material_df['Total Maintenance Cost ($)'],
                                 mode='lines+markers', name=material,
                                 line=dict(width=2)))

    fig.update_layout(
      title={
            'text': 'Maintenance Cost Over Time for Different Materials',
            'font': dict(color='black')  # Set the title font color to black
        },
        xaxis_title='Years',
        yaxis_title='Total Maintenance Cost ($)',
        template='plotly_white',  # Ensure we're using a light theme
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),  # Set the font color to black
        xaxis=dict(
            title=dict(font=dict(color='black')),
            tickfont=dict(color='black')
        ),
        yaxis=dict(
            title=dict(font=dict(color='black')),
            tickfont=dict(color='black')
        ) ,
        legend=dict(
            font=dict(color='black')  # Set legend text color to black
        )
    )
    st.plotly_chart(fig)
