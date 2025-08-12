import json
import os
from flask import Flask, request
from kafka import KafkaProducer, KafkaConsumer
from threading import Thread

app = Flask(__name__)

# Конфигурация из переменных окружения
PORT = os.environ['PORT']
KAFKA_BROKERS = os.environ['KAFKA_BROKERS']
GROUP_ID = 'main-group'

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',
    retries=3
)


def create_consumer(topic):
    return KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BROKERS,
        auto_offset_reset='earliest',
        group_id=GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')))


def consume_messages(topic):
    print(f"Starting to consume messages from topic '{topic}'...")

    consumer = create_consumer(topic)

    try:
        for msg in consumer:
            print(f'New message: [ topic: {topic}, value: {msg.value} ]')
    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        consumer.close()


@app.route('/api/events/health', methods=['GET'])
def healthcheck():
    return {"status": True}


@app.route('/api/events/<type>', methods=['POST'])
def createEvent(type):
    data = request.get_json()
    print(f'event type: {type}, body: {data}')
    producer.send(f'{type}-events', value=data)
    return {"status": 'success'}, 201


if __name__ == "__main__":
    Thread(target=lambda: consume_messages('user-events')).start()
    Thread(target=lambda: consume_messages('payment-events')).start()
    Thread(target=lambda: consume_messages('movie-events')).start()
    app.run(host='0.0.0.0', port=PORT, debug=True)
