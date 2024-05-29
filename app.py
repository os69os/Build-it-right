import streamlit as st  # type: ignore
import base64
import pandas as pd  # type: ignore
from models import (
    load_model_pycaret, calculate_form_factor_and_area, calculate_house_efficiency,
    recommend_materials, calculate_installation_cost, plot_maintenance_costs,
    MAX_COOLING_LOAD, MIN_COOLING_LOAD, MAX_HEATING_LOAD, MIN_HEATING_LOAD, data, materials
)
from pycaret.regression import predict_model  # type: ignore

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
            z-index: -1 ;
        }}
        .horizontal-values {{
            display: flex;
            justify-content: space-around;
            padding: 10px;
        }}
        .value-box {{
            text-align: center;
            margin: -10px;

        }}
        .cooling {{
            color: #ADE3ED;
            font-size: 24px;
            font-weight: bold;
        }}
        .heating {{
            color: #E46F6F;
            font-size: 24px;
            font-weight: bold;
        }}
        .total {{
            color: #8BD490;
            font-size: 24px;
            font-weight: bold;
        }}
        .efficiency {{
            color: #FFEDA5;
            font-size: 24px;
            font-weight: bold;
        }}
        .value {{
            font-size: 29px;
            font-weight: bold;
            margin-top: 0px;
        }}
        .table-container {{
            color:#F6F1F1;
            padding: 20px;
            border-radius: 10px;
        }}
        /* Custom CSS for expander and table */
        .st-expander .st-expander-content p {{
            color: #F6F1F1;
        }}
        .st-expander .st-expander-header p {{
            color: #F6F1F1;
        }}
        .st-dataframe, .st-table {{
            color: #F6F1F1;
        }}
        /* Tooltip styling */
        .tooltip {{
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background-color: black;
            color: white;
            padding: 5px;
            border-radius: 5px;
            font-size: 14px;
            visibility: hidden;
            opacity: 0;
            transition: opacity 0.3s;
            white-space: nowrap;
        }}
        .value-box:hover .tooltip {{
            visibility: visible;
            opacity: 1;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Function to get user inputs from sidebar
def get_user_inputs():
    st.sidebar.image("logo2-removebg.png", use_column_width=True) 
    st.sidebar.markdown("<h2 style='text-align: center;'>House Specifications</h2>", unsafe_allow_html=True)
    st.sidebar.markdown(
    """
    <style>
    .stNumberInput > div > div > input {
        background-color: #ADE3ED ;
        color: white;
    }
    </style>
    """, 
    unsafe_allow_html=True
)
    length = st.sidebar.number_input('House Length (m):', min_value=0.1, value=1.0)
    width = st.sidebar.number_input('House Width (m):', min_value=0.1, value=1.0)
    height = st.sidebar.number_input('House Height (m):', min_value=0.1, value=1.0)

    area, form_factor = calculate_form_factor_and_area(length, width, height)

    if area == 0 or form_factor == 0:
        st.sidebar.error("Length, Width, and Height must be greater than zero to calculate Area and Form Factor.")
        return None

    shape = st.sidebar.radio("Choose House Shape", ["BOX Shape", "U Shape", "L Shape", "O Shape"], horizontal=True)
    orientation = st.sidebar.radio("Choose House Orientation", ["North", "East", "West", "South", "North East", "North West", "South East", "South West"], horizontal=True)
    windows_ratio = st.sidebar.slider("Choose Windows Ratio (%)", min_value=10, max_value=40, step=1)

    if shape not in ["L Shape", "U Shape"]:
        skylight_ratio = st.sidebar.slider("Choose Skylight Ratio (%)", min_value=10, max_value=40, step=1)
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

def main():
    add_bg_from_local('House.jpg')

    cooling_model_path = 'tuned_model_cooling_LGB_FINAL'
    heating_model_path = 'tuned_model_heating_LGB_FINAL'

    cooling_model = load_model_pycaret(cooling_model_path)
    heating_model = load_model_pycaret(heating_model_path)
    
    st.markdown(
        "<h1 style='text-align: center; font-size: 60px; color: #F6F1F1;'>Build It Right</h1>"
, 
        unsafe_allow_html=True
    )
    

    st.markdown(
        "<h2 style='text-align: center;color: #F6F1F1'>Energy Efficient Home Design</h2>"
        "<hr style='width: 100%; margin-bottom: 70px; margin-top: 15px; border: 0.5px solid #F6F1F1;'>", 
        unsafe_allow_html=True
    )

    input_data = get_user_inputs()

    if input_data is not None:
        if st.sidebar.button("Build it"):
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
                            <h3 style="color: #F6F1F1;">Cooling Load</h3>
                            <p class="value">{cooling_load:.2f}kWh</p>
                            <div class="tooltip">The amount of heat energy that must be removed <br>to maintain indoor comfort in hot weather.</div>
                        </div>
                        <div class="value-box heating">
                            <h3 style="color: #F6F1F1;">Heating Load</h3>
                            <p class="value">{heating_load:.2f}kWh</p>
                            <div class="tooltip">The amount of heat energy needed <br>to maintain indoor comfort in cold weather.</div>
                        </div>
                        <div class="value-box total">
                            <h3 style="color: #F6F1F1;">Total Load</h3>
                            <p class="value">{total_energy:.2f}kWh</p>
                            <div class="tooltip">The combined heating and cooling energy <br>required to maintain indoor comfort throughout the year.</div>
                        </div>
                        <div class="value-box efficiency">
                            <h3 style="color: #F6F1F1;">House Rating</h3>
                            <p class="value">{house_efficiency:.2f} %</p>
                            <div class="tooltip">A measure of a house's energy performance <br>based on calculated heating and cooling loads.</div>
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
                    st.markdown("<h3 style='font-size: 24px; color: #F6F1F1;'>Recommended Materials :</h3>", unsafe_allow_html=True)

                    # Display best material information
                    with st.expander("The Result", expanded=True):
                        comparison_table = pd.DataFrame({
                            'Metric': ['Material', 'Installation Cost ($)', 'Applications', 'Additional Info', 'Installation Time', 'Lifespan (years)'],
                            'Best Efficiency Material': [
                                best_material['Material'], 
                                f"{best_material_cost:.2f}", 
                                best_material['Applications'], 
                                best_material['Additional_info'], 
                                best_material['Installation_Time'], 
                                best_material['Lifespan']
                            ],
                            'Best Cost Material)': [
                                best_cost_material['Material'], 
                                f"{best_cost_material_cost:.2f}", 
                                best_cost_material['Applications'], 
                                best_cost_material['Additional_info'], 
                                best_cost_material['Installation_Time'], 
                                best_cost_material['Lifespan']
                            ]
                        })

                        # Function to color the text
                        def color_text(val):
                            return 'color: #F6F1F1'

                        styled_table = comparison_table.style.hide(axis='index').applymap(color_text).set_table_styles(
                            [{'selector': 'thead th', 'props': [('color', '#F6F1F1')]}]
                        )

                        # st.table(styled_table)
                        st.markdown(styled_table.to_html(), unsafe_allow_html=True)

                    st.markdown("<h3 style='font-size: 24px; color: #F6F1F1;'>Maintenance Cost Over Time</h3>", unsafe_allow_html=True)
                    materials_to_plot = [best_material, best_cost_material]
                    plot_maintenance_costs(height, length, width, shape, materials_to_plot)

                else:
                    st.warning("No suitable materials found for the given efficiency range.")
                
            else:
                st.error("Failed to make predictions. Please check the model files.")



if __name__ == "__main__":
    main()
