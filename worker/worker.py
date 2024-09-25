from peewee import Model, CharField, DateTimeField, MySQLDatabase,TextField,AutoField
import datetime,configparser
import pika
import json
confs=configparser.ConfigParser()
confs.read("configs.ini")
credentials = pika.PlainCredentials(confs['app']['rabbituser'],confs['app']['rabbitpassword'])

# Database setup
dirctaccess= "yes" in confs["DATABASE"]["direct"]
db = MySQLDatabase(
    str(confs["DATABASE"]["dbname"]),  # Database name
    user=str(confs["DATABASE"]["username"]),
    password=str(confs["DATABASE"]["password"]),
    host=confs["DATABASE"]['directserver'] if dirctaccess else confs["DATABASE"]['maxscale'],
    port=int(confs["DATABASE"]["directport"] if dirctaccess else confs["DATABASE"]['maxscale_port'])
)
f= open("/var/log/worker_eventlogs.log","a+")
def log_event(message):
    
    f.write(f"{datetime.datetime.now()} :{message}\n")


class JSONField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)

class Event(Model):
    eventid=AutoField(primary_key=True)
    eventtype = CharField()
    source = CharField()
    user=CharField(max_length=90,default="anonymous")
    occured_at = DateTimeField(default=datetime.datetime.now)
    metadata = JSONField()

    class Meta:
        database = db

db.connect()
#db.create_tables([Event])

def save_event_to_db(event):
    event=dict(event)
    try:
        newevent=Event.create(
            
            eventtype=event['eventtype'],
            source=event['source'],
            metadata=event['metadata'],
            user=event['user'] if event['user'] else "anonymous"
        )
        log_event(f" trackid {event['trackid']} stored in DB")
        print(f"Event {newevent.eventid} saved successfully.")
    except Exception as e:
        print(f"Failed to save event {newevent.eventid} TID:{event['trackid']}: {e}")

def consume_from_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=confs["app"]["rabbitmq"],
                                                                   port=5672,
                                                                   virtual_host='/',
                                                                   credentials=credentials
                                                                   ))
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
