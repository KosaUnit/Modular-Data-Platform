from confluent_kafka import Consumer
import json

conf = {
    'bootstrap.servers': 'localhost:9092',
    "group.id": "order-tracker",
    "auto.offset.reset": "earliest"
    }

consumer = Consumer(conf)

consumer.subscribe(["orders"])

print("Consumer is runing and subscriber to orders.")

while True:
    msg = consumer.poll(timeout=1.0) # your polling the data 
    if msg is None: 
        continue
    if msg.error():
        print(f"Error {msg.error()}")
        continue

    value = msg.value().decode("utf-8")
    order = json.loads(value)

    print(f"Order received: {order}")

    ## You want to add clean disconection from the kafka broker 