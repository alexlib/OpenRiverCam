import requests
import pika
import traceback
import os
import json

# Callback function for each process task that is queued.
def process(ch, method, properties, body):
    try:
        taskInput = json.loads(body.decode("utf-8"))
        print('Process task of type %s' % taskInput['type'])

        # Example request to API (only used for posting/updating information).
        r = requests.get('http://portal/api/sites')

        # Acknowledge queue item at end of task.
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print('Processing failed with error: %s' % str(e))
        traceback.print_tb(e.__traceback__)

connection = pika.BlockingConnection(pika.URLParameters(os.getenv('AMQP_CONNECTION_STRING')))
channel = connection.channel()
channel.queue_declare(queue='processing')
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='processing', on_message_callback=process)

try:
    print('Start listening for processing tasks in queue.')
    channel.start_consuming()
except Exception as e:
    print('Reboot service due to error: %s' % str(e))
    channel.stop_consuming()
    connection.close()
    traceback.print_tb(e.__traceback__)