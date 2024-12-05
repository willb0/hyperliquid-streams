import json
import requests

ws_source = json.load(open('create_source_pipeline.json'))
query_source = json.load(open('create_query_pipeline.json'))
def create_arroyo_source(token: str):

    body = ws_source.copy()
    subscription_string = json.dumps({"method": "subscribe", "subscription": {"type": "l2Book", "coin": token}})
    body['config']['subscription_messages'] = [subscription_string]
    body['name'] = token.upper()
    
    response = requests.post('http://arroyo:5115/api/v1/connection_tables', json=body)
    assert response.status_code == 200, f'Error creating source with {response.status_code}: {response.text}'

    return response.json()
def create_arroyo_pipeline(token: str):
    body = query_source.copy()
    query_string = "create table mqtt_sink (\n) with (\n    connector = 'mqtt',\n    url = 'mqtt://mosquitto:1883',\n    type = 'sink',\n    format = 'json',\n    topic = 'events-{}'\n);\nINSERT INTO mqtt_sink \nwith pre as (\n    select \n        json_get(value,'data','time') as ts,\n        buy_sum(value) as buy_sum,\n        sell_sum(value) as sell_sum\n    from {}\n),\npost as (\nselect \n    tumble(interval '1 seconds') over (order by ts asc) as time,\n    avg(buy_sum) as avg_buy_vol,\n    avg(sell_sum) as avg_sell_vol,\n    avg(buy_sum/sell_sum) as avg_ob_pressure\nfrom pre\ngroup by time)\n\nselect \n    get_field(time,'start') as start_time,\n    avg_buy_vol,\n    avg_sell_vol,\n    avg_ob_pressure\nfrom\n    post\n".format(token.upper(),token.upper())
    body['query'] = query_string
    body['name'] = f'{token.upper()} pipeline'
    response = requests.post('http://arroyo:5115/api/v1/pipelines', json=body)
    assert response.status_code == 200, f'Error creating pipeline with {response.status_code}: {response.text}'
    return response.json()

def get_arroyo_pipelines():
    response = requests.get('http://arroyo:5115/api/v1/pipelines')
    assert response.status_code == 200, f'Error getting pipelines with {response.status_code}: {response.text}'
    return [r['name'] for r in response.json()['data'] where r['actionText'] != 'Failed']
