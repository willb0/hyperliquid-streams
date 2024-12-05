import time
from matplotlib import pyplot as plt
import plost
import streamlit as st
import pandas as pd
import plotly.express as px
from collections import deque
import threading
import json
from mqtt_listener import start_mqtt_listener
from arroyo_utils import get_arroyo_pipelines, create_arroyo_pipeline, create_arroyo_source

# Initialize global variables
data_queue = deque(maxlen=300)  # Maintain a 30-second window (6 * 5-second intervals)
added_data = False
data_lock = threading.Lock()

# Function to add new data to the queue
def add_data(new_data):
    global added_data
    with data_lock:
        data_queue.append(new_data)
        added_data = True


tab1, tab2 = st.tabs(['Dashboard','Create Pipeline'])

with tab2:
    st.header("Create a new pipeline")
    token = st.text_input('Enter the token',value='ETH')
    butt = st.button('Create Pipeline')
    if butt:
        create_arroyo_source(token)
        create_arroyo_pipeline(token)
        st.write('Pipeline created successfully! select it in the dashboard.')


with tab1:
    st.title("Real-Time Order Book Metrics")
    st.write("Displaying a running 30-second window of MQTT events.")

    # Start MQTT Listener in a separate thread
    thread = None

    # Streamlit app loop
    input_box = st.selectbox("Choose a pipeline",get_arroyo_pipelines())
    if thread is not None:
        thread.stop()
    placeholder = st.empty()
    if input_box:
        thread = threading.Thread(target=start_mqtt_listener, args=(add_data,input_box.split(' ')[0]), daemon=True)
        thread.start()
        df = pd.DataFrame(columns=["start_time", "avg_buy_vol", "avg_sell_vol", "avg_ob_pressure"])
        pause_button = st.button("Pause")
        while True:
            with data_lock:
                if added_data:
                    df = pd.DataFrame(data_queue, columns=["start_time", "avg_buy_vol", "avg_sell_vol", "avg_ob_pressure"])
                    added_data = False
            with placeholder.container():
                st.markdown("### First Chart")
                fig = plost.line_chart(
                    df, y="avg_ob_pressure", x="start_time"
                )
                st.write(fig)
                    
                st.markdown("### Second Chart")
                fig2 = plost.hist(data=df, x="avg_buy_vol")
                st.write(fig2)

                fig3 = plost.line_chart(
                    df, y=("avg_buy_vol","avg_sell_vol"), x="start_time"
                )
                
                fig3 = plost.xy_hist(
                    df, x="avg_buy_vol",y='avg_sell_vol'
                )
            time.sleep(1)  # Refresh every second

    
    
