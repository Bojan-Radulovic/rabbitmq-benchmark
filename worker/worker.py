import json
from datetime import datetime
import pika
from pymongo import MongoClient
import time

mongo_client = MongoClient('mongodb://mongodb:27017/')

db = mongo_client['calendar_app_database']

def connect_to_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', 5672))
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Error connecting to RabbitMQ: {e}")
            connection = None
        if connection is not None:
            print("Connected to RabbitMQ successfully!")
            break
        else:
            print("Retrying in 5 seconds...")
            time.sleep(5)
    return connection

connection = connect_to_rabbitmq()
channel = connection.channel()
channel.queue_declare(queue='to_write', durable=True)
channel.queue_declare(queue='to_read', durable=True)

def write_callback(ch, method, props, body):
    try:
        message_data = json.loads(body)

        user_id = message_data.get('user_id')
        date = message_data.get('date')
        event_text = message_data.get('event_text')
        sleep_time = message_data.get('sleep_time')

        time.sleep(sleep_time)

        event_document = {
            'user_id': user_id,
            'date': date,
            'event_text': event_text,
            'time_inserted': datetime.now().strftime('%d-%m-%y %H:%M:%S'),
        }

        db['events'].insert_one(event_document)

        print(f"Event data written to MongoDB: {event_document}")

        response = event_document
        response['_id'] = str(response['_id'])
        print("My response is ", response)
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=json.dumps(response)
        )

    except Exception as e:
        print(f"Error processing message: {e}")
        response = "ERROR"
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=str(response)
        )

    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

def read_all_data_from_mongodb():
    try:
        all_events = list(db['events'].find())

        for event in all_events:
            event['_id'] = str(event['_id'])

        return all_events
    except Exception as e:
        print(f"Error reading data from MongoDB: {e}")
        return None

def read_callback(ch, method, props, body):
    try:
        all_events = read_all_data_from_mongodb()

        response = all_events if all_events is not None else "ERROR"
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=json.dumps(response)
        )

    except Exception as e:
        print(f"Error processing message: {e}")
        response = "ERROR"
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=str(response)
        )

    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='to_write', on_message_callback=write_callback)
channel.basic_consume(queue='to_read', on_message_callback=read_callback)

print("Worker is waiting for messages. To exit press Ctrl+C")
channel.start_consuming()
