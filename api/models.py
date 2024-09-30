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
    def get_eventcount_lasthours(hours=24):
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(hours=hours)
        query = (Event
                .select(fn.DATE_TRUNC('hour', Event.occured_at).alias('hour'), fn.COUNT(Event.eventid).alias('count'))
                .where(Event.occured_at.between(yesterday, now))
                .group_by(fn.DATE_TRUNC('hour', Event.occured_at))
                .order_by(fn.DATE_TRUNC('hour', Event.occured_at)))

        finalresult={}
        for result in query:
            finalresult[result.hour]=result.count
        return finalresult
    @classmethod
    def get_eventcount_lasthours_classified(classify_by="source"):
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(hours=24)
        classify_column = Event.source if classify_by == "source" else Event.eventtype
        query = (Event
                .select(fn.DATE_TRUNC('hour', Event.occured_at).alias('hour'),
                        classify_column.alias(classify_by),  # Alias the column by its name
                        fn.COUNT(Event.eventid).alias('count'))
                .where(Event.occured_at.between(yesterday, now))
                .group_by(fn.DATE_TRUNC('hour', Event.occured_at), classify_column)
                .order_by(fn.DATE_TRUNC('hour', Event.occured_at)))
        finalresult={}
        for result in query:
            finalresult[result.hour]={str(classify_by.capitalize()): getattr(result, classify_by), "Count": result.count}
        return finalresult
    @classmethod
    def count_events_by_source()->dict:
        query = (Event
                .select(Event.source, fn.COUNT(Event.eventid).alias('count'))
                .group_by(Event.source)
                .order_by(fn.COUNT(Event.eventid).desc()))  # Order by count in descending order

        finalresult= {}
        for result in query:
            finalresult[result.source]= result.count
        return finalresult
    class Meta:
        database = db

db.connect()
db.create_tables([Event],safe=True)
