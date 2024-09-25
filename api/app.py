from models import *
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flasgger import Swagger, swag_from
import pika,logging
import json,secrets
from hashlib import md5
logging.basicConfig(filename='events.log', level=logging.INFO, format='%(message)s')
app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)
credentials = pika.PlainCredentials(confs['APP']['rabbituser'],confs['APP']['rabbitpassword'])
f= open("/var/log/eventlogs.log","a+")
def log_event(message):
    
    f.write(f"{datetime.datetime.now()} :{message}\n")
def queue_event(event,trackid):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=confs["APP"]["rabbitmq"],
                                                                   port=5672,
                                                                   virtual_host='/',
                                                                   credentials=credentials
                                                                   ))
    event["trackid"]=trackid
    channel = connection.channel()
    channel.queue_declare(queue='event_queue')
    channel.basic_publish(exchange='', routing_key='event_queue', body=json.dumps(event))
    connection.close()
    
    log_event(f'TrackID {event["trackid"]} queued')
    
#queue_event('{"message":"test"}')
class EventResource(Resource):
    @swag_from({
        'responses': {
            200: {
                'description': 'Event queued successfully',
                'examples': {
                    'application/json': {
                        'message': 'Event queued successfully'
                    }
                }
            },
            400: {
                'description': 'Invalid input'
            }
        }
    })
    def post(self):
        """
        Queue a new event
        ---
        tags:
          - Event
        parameters:
          - in: body
            name: body
            required: true
            schema:
              id: Event
              required:
                - eventid
                - eventtype
                - source
                - metadata
                - user
              properties:
                eventid:
                  type: string
                eventtype:
                  type: string
                source:
                  type: string
                user:
                  type: string
                metadata:
                  type: object

        """
        event = request.get_json()
        trackseed=f"{datetime.datetime.now()}_{secrets.token_hex(8)}_{event['source']}"
        tid=md5(trackseed.encode()).hexdigest()
        log_event(f'api_request from {event["source"]} TID:{tid}')
        try:
          queue_event(event,tid)
        except Exception as ex:
            print(f"Problem with Queue service:: {str(ex)}")
        return jsonify({'message': 'Event queued successfully','trackid':str(tid)})

    def get(self):
        """
        Retrieve events from the database
        ---
        tags:
          - Event
        parameters:
          - in: query
            name: eventid
            type: string
            user: string
            required: false
            description: ID of the event to retrieve
          - in: query
            name: eventtype
            type: string
            required: false
            description: Type of the event to retrieve
          - in: query
            name: source
            type: string
            required: false
            description: Source of the event to retrieve
          - in: query
            name: metadata
            type: string
            required: false
            description: Metadata JSON string (key-value pair)
        """
        query = Event.select()
        
        # Filtering by eventid
        eventid = request.args.get('eventid')
        if eventid:
            query = query.where(Event.eventid == eventid)

        # Filtering by eventtype
        eventtype = request.args.get('eventtype')
        if eventtype:
            query = query.where(Event.eventtype == eventtype)

        # Filtering by source
        source = request.args.get('source')
        if source:
            query = query.where(Event.source == source)
        user = request.args.get('user')
        if user:
            query = query.where(Event.user == user)
        # Filtering by metadata (expects JSON key-value pair)
        metadata = request.args.get('metadata')
        if metadata:
            try:
                metadata_dict = json.loads(metadata)
                for key, value in metadata_dict.items():
                    query = query.where(Event.metadata[key] == value)
            except (json.JSONDecodeError, KeyError) as e:
                return jsonify({'message': f'Invalid metadata format: {e}'}), 400

        events =query.execute()
        
        # If no events found, return 404
        if not events:
            return jsonify({'message': 'No events found'}), 404

        # Format the results
        events_list = [{
            'eventid': event.eventid,
            'eventtype': event.eventtype,
            'source': event.source,
            'occured_at': event.occured_at.isoformat(),
            'metadata': event.metadata
        } for event in events]
        
        return jsonify(events_list)
api.add_resource(EventResource, '/event')
#app.run(host='0.0.0.0')
#queue_event('{"message":"test"}')