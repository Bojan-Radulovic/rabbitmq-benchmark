import json
import subprocess
import time
import uuid

from faker import Faker
from flask import Flask, render_template, request
import pika

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

class RpcClient(object):

    def __init__(self, queue_name):
        self.connection = connect_to_rabbitmq()

        self.channel = self.connection.channel()

        self.to_queue = self.channel.queue_declare(queue=queue_name, durable=True)

        self.queue_name = queue_name

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, message):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(message))
        self.connection.process_data_events(time_limit=None)
        self.connection.close()
        return self.response

def get_queue_consumer_count(queue_name):
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    queue_info = channel.queue_declare(queue=queue_name, passive=True)
    consumer_count = queue_info.method.consumer_count
    connection.close()
    return consumer_count
    
connect_to_rabbitmq()
fake = Faker()
client_id = str(uuid.uuid4())
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/write-database')
def write_database_page():
    sleep_time = float(request.args.get('sleep_time', 0))
    writeRpcClient = RpcClient('to_write')
    inserted_data = []
    message = {
        'user_id': fake.random_int(min=1, max=1000),
        'date': fake.date_this_decade().strftime('%d-%m-%Y'),
        'event_text': fake.text(max_nb_chars=20),
        'sleep_time': sleep_time,
    }
    response = writeRpcClient.call(message)
    response_message = json.loads(response)
    print("I have gotten response ", response_message)
    inserted_data.append(response_message)

    return render_template('index.html', inserted_data=inserted_data)

@app.route('/read-database')
def read_database_page():
    writeRpcClient = RpcClient('to_read')
    response = writeRpcClient.call('')
    response_message = json.loads(response)
    return render_template('index.html', database_data=response_message)

@app.route('/ab-benchmark')
def ab_benchmark():
    worker_count = get_queue_consumer_count("to_write")
    host = request.host
    sleep_time = float(request.args.get('sleep_time', 1))
    url = f"http://{host}/write-database?sleep_time={sleep_time}"
    concurrency = request.args.get('concurrency', default=5, type=int)
    requests = request.args.get('requests', default=100, type=int)

    command = f"ab -c {concurrency} -n {requests} -l {url}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    print(result.stdout)

    return render_template('index.html', ab_result={"command": command, "sleep_time": sleep_time, "worker_count": worker_count, "result": result.stdout})

if __name__ == '__main__':
    app.run(debug=True)
