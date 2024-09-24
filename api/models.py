from peewee import Model, CharField, DateTimeField, MySQLDatabase,TextField
import datetime,configparser,json
confs=configparser.ConfigParser()
confs.read('C:\\Users\\FLW\\Desktop\\event_sourceservice\\api\\config.ini')




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
    host=confs["DATABASE"]['directserver'] if dirctaccess else confs["database"]['maxscaleserver'],
    port=int(confs["DATABASE"]["directport"] if dirctaccess else confs["database"]['maxscaleport'])
)
    return db

db=make_connection()
# Assuming MaxScale is running on 'maxscale_host' and listens on port 3306

class Event(Model):
    eventid = CharField(primary_key=True)
    eventtype = CharField() #order,action,entrance,...
    source = CharField()
    user=CharField(max_length=90,default="anonymous")
    occured_at = DateTimeField(default=datetime.datetime.now)
    metadata = JSONField()

    class Meta:
        database = db

db.connect()
db.create_tables([Event],safe=True)
