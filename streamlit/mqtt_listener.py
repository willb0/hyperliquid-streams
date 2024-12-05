import json
import paho.mqtt.client as mqtt

def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        userdata(payload)  # Pass new data to the callback
    except Exception as e:
        print(f"Error processing message: {e}")

def start_mqtt_listener(callback, token):
    client = mqtt.Client(userdata=callback)
    client.on_message = on_message
    client.connect("mosquitto", 1883)  # Adjust MQTT broker/port if necessary
    client.subscribe(f"events-{token}")
    client.loop_forever()
