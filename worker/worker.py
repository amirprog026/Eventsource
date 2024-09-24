from peewee import Model, CharField, DateTimeField, MySQLDatabase,TextField
import datetime,configparser
import pika
import json
confs=configparser.ConfigParser()
configs=confs.read()
# Database setup
db = MySQLDatabase('events.db')

class JSONField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)

class Event(Model):
    eventid = CharField(primary_key=True)
    eventtype = CharField()
    source = CharField()
    user=CharField(max_length=90,default="anonymous")
    occured_at = DateTimeField(default=datetime.datetime.now)
    metadata = JSONField()

    class Meta:
        database = db

db.connect()
db.create_tables([Event])

def save_event_to_db(event):
    try:
        Event.create(
            eventid=event['eventid'],
            eventtype=event['eventtype'],
            source=event['source'],
            metadata=event['metadata'],
            user=event['user'] if event['user'] else "anonymous"
        )
        print(f"Event {event['eventid']} saved successfully.")
    except Exception as e:
        print(f"Failed to save event {event['eventid']}: {e}")

def consume_from_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='event_queue')

    def callback(ch, method, properties, body):
        event = json.loads(body)
        save_event_to_db(event)

    channel.basic_consume(queue='event_queue', on_message_callback=callback, auto_ack=True)
    print('Waiting for events to process.')
    channel.start_consuming()

if __name__ == "__main__":
    consume_from_queue()
