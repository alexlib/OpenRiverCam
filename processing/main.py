import requests
import pika
import traceback
import os
import json
import tasks
import log

logger = log.start_logger(True, False)

# Callback function for each process task that is queued.
def process(ch, method, properties, body):
    try:
        taskInput = json.loads(body.decode("utf-8"))
        task_name = taskInput["type"]
        kwargs = taskInput["kwargs"]
        if hasattr(tasks, task_name):
            task = getattr(tasks, task_name)
            logger.info("Process task of type %s" % taskInput["type"])
            logger.debug(f"kwargs: {kwargs}")
            try:
                task(**kwargs, logger=logger)
                logger.info(f"Task {task_name} was successful")
                r = 200
            except BaseException as e:
                logger.error(f"{task_name} failed with error {e}")
                requests.post("http://portal/api/processing/error/%s" % taskInput['kwargs']['movie']['id'], json.dumps({"message": e}))
                r = 500

        # # Example request to API (only used for posting/updating information).
        # r = requests.get('http://portal/api/sites')
        #
        # # Example upload file to S3.
        # s3 = boto3.resource('s3',
        #                     endpoint_url='http://storage:9000',
        #                     aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
        #                     aws_secret_access_key=os.getenv('S3_ACCESS_SECRET'),
        #                     config=boto3.session.Config(signature_version='s3v4')
        #                     )
        #
        # # Create bucket if it doesn't exist yet.
        # if s3.Bucket('test-bucket') not in s3.buckets.all():
        #     s3.create_bucket(Bucket='test-bucket')
        #
        # uploadTestFile = io.BytesIO()
        # # Seek beginning of in-memory file before storing.
        # uploadTestFile.seek(0)
        # s3.Object('test-bucket', 'test.jpg').put(Body=uploadTestFile)
        #
        # # Example download file from S3.
        # downloadTestFile = io.BytesIO()
        # s3.Object('test-bucket', 'test.jpg').download_fileobj(downloadTestFile)
        #
        # Acknowledge queue item at end of task.
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print("Processing failed with error: %s" % str(e))
        traceback.print_tb(e.__traceback__)


connection = pika.BlockingConnection(
    pika.URLParameters(os.getenv("AMQP_CONNECTION_STRING"))
)
channel = connection.channel()
channel.queue_declare(queue="processing")
# Process a single task at a time.
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="processing", on_message_callback=process)

try:
    print("Start listening for processing tasks in queue.")
    channel.start_consuming()
except Exception as e:
    print("Reboot service due to error: %s" % str(e))
    channel.stop_consuming()
    connection.close()
    traceback.print_tb(e.__traceback__)
