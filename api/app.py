from models import *
import requests
from flask import Flask, request, jsonify,url_for,render_template
from flask_restful import Api, Resource
from flasgger import Swagger, swag_from
import pika,logging
import json,secrets
from flask_wtf.csrf import CSRFProtect, validate_csrf, CSRFError
from hashlib import md5,sha384
from collections import defaultdict
logging.basicConfig(filename='events.log', level=logging.INFO, format='%(message)s')
app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)
app.secret_key=str(confs['APP']['APPKEY'])
#csrf = CSRFProtect()
credentials = pika.PlainCredentials(confs['APP']['rabbituser'],confs['APP']['rabbitpassword'])

API_LOG_FILE="/var/log/eventlogs.log"
DB_LOG_FILE="/var/log/worker_eventlogs.log"

def log_event(message):
    f= open(API_LOG_FILE,"a+")
    f.write(f"{datetime.datetime.now()} *{message}\n")
    f.close()
def parse_timestamp(line):
    """Extract timestamp from the log line and return as a datetime object."""
    if len(line) <2:
        return None
    try:
        timestamp_str = line.split('*')[0].strip()
        return datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
    except Exception as ecx:
        print(ecx)
        return None
def read_recent_lines(file_path, time_threshold=datetime.datetime.now() - datetime.timedelta(hours=24)):
    """Read lines from the log file that are within the last 24 hours."""
    recent_lines = []
    with open(file_path, 'r') as file:
        for line in file:
            timestamp = parse_timestamp(line)
            
            if timestamp and timestamp > time_threshold:
                recent_lines.append(line)
    return recent_lines

def fetch_Sale_View_data(lasthours=24):
        """sample response : {
            "saleevents": [],
            "productviewevents": [],
            "visitevents": []
        }
"""
        sale_event_types = [event.strip() for event in str(confs['events']['sale_event_types']).split(',')]
        productview_types = [event.strip() for event in str(confs['events']['productview_types']).split(',')]
        visit_types = [event.strip() for event in str(confs['events']['visit_types']).split(',')]
        return Event.fetch_events_by_type_last_h(sale_event_types,productview_types,visit_types,lasthours)



def group_sales_by_day(query_result):
    """query_result must selected using peewee"""
    sales_by_day = defaultdict(float)
    for event in query_result:
        event_date = event.occured_at.date()  # Get the date part of the occured_at timestamp
        if str(event.eventtype) in [event.strip() for event in str(confs['events']['sale_event_types']).split(',')]:  
            amount = event.metadata.get('amount', 0)  
            sales_by_day[str(event_date)] += float(amount)  
    return dict(sales_by_day)

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
    log_event(f'TrackID {event["trackid"]} queued')
    connection.close()
    
    
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
                - eventtype
                - source
                - metadata
                - user
              properties:
                eventid:
                  type: Autofield
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
            type: int
            required: false
            description: generated automatically
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
            name: user
            type: string
            required: true
            description: consider 'anonymous' if it is unknown
          - in: query
            name: metadata
            type: string
            required: false
            description: Metadata JSON string (key-value pair)
        """
        query = Event.select().limit(20000).order_by(Event.occured_at.desc())
        
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

def read_log_file(file_path, last_line_number=0):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        return lines[last_line_number:], len(lines)

@app.route('/track_counts')
def counts():
    return jsonify (Event.get_eventcount_lasthours())

@app.route('/track-status')
def track_status():
    api_lines = read_recent_lines(API_LOG_FILE)
    db_lines = read_recent_lines(DB_LOG_FILE)
    queuedcount=0
    storedcount=0
    requestscount=0
    qids=set()#trackids in queue
    sids=set()#trackids in DB
    eventsbysource=Event.count_events_by_source()
    
    # Update the status dictionary
    for line in api_lines:
        if "queued" in line:
            trackid = line.split()[-2]
            qids.add(trackid)
            queuedcount+=1
        if "api_request" in line:
            requestscount+=1
            
        
    for line in db_lines:
        if "stored" in line:
            trackid = line.split()[-4]
            storedcount+=1
            sids.add(trackid)
            
    inqueue=qids.difference(sids)
    # Prepare the response
    queued_trackids = {"inqueue": inqueue}
    data = {
        
        "stored_count": storedcount,
        "queued_count": queuedcount,
        "inqueue_count":len(inqueue),
        "inqueue_items":list(inqueue),
        "counts":eventsbysource,
        
    }

    return jsonify(data)


@app.route('/manualinsert', methods=['POST'])
def create_manual_event():
    TARGET_ENDPOINT=confs['APP']['BASEURL']+"/event"
    
    # Get form data
    eventtype = request.form.get('eventtype')
    source = request.form.get('source')
    user = request.form.get('user', 'anonymous')  # Default to 'anonymous'
    
    # Get and parse metadata
    metadata = request.form.get('metadata')
    if metadata:
        try:
            metadata = json.loads(metadata)
        except ValueError:
            return jsonify({"error": "Invalid metadata format"}), 400
    else:
        metadata = {}
    payload = {
        "eventtype": eventtype,
        "source": source,
        "user": user,
        "metadata": metadata
    }

    # Send POST request to the target endpoint
    try:
        response = requests.post(TARGET_ENDPOINT, json=payload)
        response.raise_for_status()  # Raise an error for bad responses

        # Return the response from the target endpoint
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/panel")
def panel():
    countbysource=Event.count_events_by_source()
    saleview_data=fetch_Sale_View_data()
    #counted_data={x:len(saleview_data[x]) for x in saleview_data.keys()} 
    lastmonthdata=Event.getlast30days_events()
    _monthsum=sum(int(event.metadata.get('amount', 0)) for event in lastmonthdata)
    grouped_data=group_sales_by_day(lastmonthdata)
    userscount=Event.get_data_count_by_user([event.strip() for event in str(confs['events']['sale_event_types']).split(',')])
    return render_template("index.html",eventscount=countbysource,
                           sumevents=int(sum(countbysource.values())),
                           saleviewdata={x:len(saleview_data[x]) if type(saleview_data[x]) is not int else 0 for x in saleview_data.keys()},
                           salesamount= saleview_data['saleamount'],
                           saleinmonth=_monthsum,
                           monthlydata_key=list(grouped_data.keys()),
                           monthlydata_values=list(grouped_data.values()),
                           customers=int(userscount[1]),
                           overalusers=int(userscount[0]),
                           anonymousevents=int(userscount[2]),
                           conversionrate=int(userscount[1])//int(userscount[0])*100)
@app.route("/dataview/<platform>")
def viewplatform(platform):
    query = Event.select().where(Event.source==platform).limit(40000).order_by(Event.occured_at.desc())
    events =query.execute()
    """events_list = [{
            'eventid': event.eventid,
            'eventtype': event.eventtype,
            'source': event.source,
            'occured_at': event.occured_at.isoformat(),
            'metadata': event.metadata
        } for event in events]"""
    return render_template('dataview.html',events=events,eventscount=Event.count_events_by_source())
#app.run(debug=True,host='0.0.0.0',port='4433')
#queue_event('{"message":"test"}')
