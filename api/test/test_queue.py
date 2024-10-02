import pika,json,secrets
credentials = pika.PlainCredentials("event2","amiraa74")
def queue_event(event,trackid):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="194.146.123.166",
                                                                   port=5672,
                                                                   virtual_host='/',
                                                                   credentials=credentials
                                                                   ))
    event["trackid"]=trackid
    channel = connection.channel()
    channel.queue_declare(queue='event_queue')
    channel.basic_publish(exchange='', routing_key='event_queue', body=json.dumps(event))
    #log_event(f'TrackID {event["trackid"]} queued')
    connection.close()

queue_event({
    
  "eventtype": "t",
  "metadata": {"test":"10000"},
  "source": "test11",
  "user": "t3"
},secrets.token_hex(12))