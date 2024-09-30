from peewee import Model, CharField, DateTimeField, MySQLDatabase,TextField,AutoField,fn
import datetime,configparser,json
confs=configparser.ConfigParser()
confs.read('config.ini')

class JSONField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)
def make_connection():
    dbname=confs["DATABASE"]["dbname"]
    username=confs["DATABASE"]["username"]
    password=confs["DATABASE"]["password"]
    dirctaccess= "yes" in confs["DATABASE"]["direct"]
    
    db = MySQLDatabase(
    str(dbname),  # Database name
    user=username,
    password=password,
    host=confs["DATABASE"]['directserver'] if dirctaccess else confs["DATABASE"]['maxscale'],
    port=int(confs["DATABASE"]["directport"] if dirctaccess else confs["DATABASE"]['maxscale_port'])
)
    return db

db=make_connection()




class Event(Model):
    eventid = AutoField(primary_key=True)
    eventtype = CharField() #order,action,entrance,...
    source = CharField()
    user=CharField(max_length=90,default="anonymous")
    occured_at = DateTimeField(default=datetime.datetime.now)
    metadata = JSONField()
    @classmethod
    def get_eventcount_lasthours(self,lasthours=24):
        now = datetime.datetime.now()
        
        yesterday = now - datetime.timedelta(hours=int(lasthours))
        query = (Event
                .select(fn.DATE_FORMAT(Event.occured_at, '%Y-%m-%d %H:00:00').alias('hour'),
                        fn.COUNT(Event.eventid).alias('count'))
                .where(Event.occured_at.between(yesterday, now))
                .group_by(fn.DATE_FORMAT(Event.occured_at, '%Y-%m-%d %H:00:00'))
                .order_by(fn.DATE_FORMAT(Event.occured_at, '%Y-%m-%d %H:00:00')))

        finalresult={}
        for result in query:
            finalresult[str(result.hour)]=result.count
        return finalresult
    @classmethod
    def get_eventcount_lasthours_classified(self,classify_by="source"):
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(hours=24)
        classify_column = Event.source if classify_by == "source" else Event.eventtype
        query = (Event
                .select(fn.DATE_FORMAT(Event.occured_at, '%Y-%m-%d %H:00:00').alias('hour'),
                        classify_column.alias(classify_by),  # Alias the column by its name
                        fn.COUNT(Event.eventid).alias('count'))
                .where(Event.occured_at.between(yesterday, now))
                .group_by(fn.DATE_FORMAT(Event.occured_at, '%Y-%m-%d %H:00:00'), classify_column)
                .order_by(fn.DATE_FORMAT(Event.occured_at, '%Y-%m-%d %H:00:00')))

        finalresult={}
        for result in query:
            finalresult[str(result.hour)]={str(classify_by.capitalize()): getattr(result, classify_by), "Count": result.count}
        return finalresult
    @classmethod
    def count_events_by_source(self,lasthours=24)->dict:
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(hours=lasthours)

        query = (Event
                .select(Event.source, fn.COUNT(Event.eventid).alias('count'))
                .where(Event.occured_at.between(yesterday, now))  # Select only events from the last 24 hours
                .group_by(Event.source)
                .order_by(fn.COUNT(Event.eventid).desc())) 

        finalresult= {}
        for result in query:
            finalresult[result.source]= result.count
        return finalresult
    @classmethod
    def fetch_events_by_type_last_h(self,sale_event_types,productview_types,visit_types,lasthours=24):
        # Load the config file
      



        # Get the current time and 24 hours ago
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(hours=lasthours)

        # Initialize an empty dictionary to store results
        event_dict = {
            "saleevents": [],
            "productviewevents": [],
            "visitevents": []
        }

        
        sale_events_query = Event.select().where(
            (Event.eventtype.in_(sale_event_types)) &
            (Event.occured_at.between(yesterday, now))
        )
        event_dict['saleevents'] = list(sale_events_query.dicts())

       
        productview_events_query = Event.select().where(
            (Event.eventtype.in_(productview_types)) &
            (Event.occured_at.between(yesterday, now))
        )
        event_dict['productviewevents'] = list(productview_events_query.dicts())

     
        visit_events_query = Event.select().where(
            (Event.eventtype.in_(visit_types)) &
            (Event.occured_at.between(yesterday, now))
        )
        event_dict['visitevents'] = list(visit_events_query.dicts())

        return event_dict
    class Meta:
        database = db

db.connect()
db.create_tables([Event],safe=True)
