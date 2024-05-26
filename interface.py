import streamlit as st
from pycaret.regression import load_model, predict_model
import base64
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Load the dataset
file_path = 'Houses_data.csv'  # Adjust the path to your dataset
data = pd.read_csv(file_path)

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
    area = length * width
    volume = length * width * height
    surface_area = 2 * (length * width + length * height + width * height)
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

# Function to recommend materials based on loads
def recommend_materials(cooling_load, heating_load):
    recommendations = []
    if cooling_load > 45.33:  # 75th percentile
        recommendations.append("Use reflective roof coatings to reduce heat absorption.")
    if heating_load > 1.24:  # 75th percentile
        recommendations.append("Consider using high-quality wall insulation to retain heat.")
    if cooling_load <= 45.33 and heating_load <= 1.24:
        recommendations.append("Your house design is efficient. Maintain good ventilation and consider using energy-efficient windows.")
    return recommendations

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
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                recommendations = recommend_materials(cooling_load, heating_load)
                if recommendations:
                    st.write("**Recommendations for Improving Energy Efficiency:**")
                    for rec in recommendations:
                        st.write(f"- {rec}")

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
                    ''')

            else:
                st.error("Failed to make predictions. Please check the model files.")

if __name__ == "__main__":
    main()
