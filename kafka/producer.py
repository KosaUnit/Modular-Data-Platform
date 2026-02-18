from confluent_kafka import Producer
import uuid
import json

producer_config = {
    "bootstrap.servers": "localhost:9092"
}

producer = Producer(producer_config) # connect to kafka

def delivery_report(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivery succeeded: {msg.value().decode("utf-8")}")
        print(f"topic={msg.topic()}, partition={msg.partition()}, offset={msg.offset()}")
        print(dir(msg))


order = {
    "orderd_id": str(uuid.uuid4()), 
    "user": "Pyszne",
    "item": "Pizza",
    "quantity": 11
}

event = json.dumps(order).encode("utf-8") # change json format into string and encode inot byte format

producer.produce(
    topic="orders", 
    value=event,
    callback=delivery_report)


producer.flush()