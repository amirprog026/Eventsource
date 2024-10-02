"# Eventsource" 
This project based on FLASK microframework which can collect  all events and unified them in an standard format:<br>
Monitoring panel: http://serveraddress/panel<br>
APIDOC: http://serveraddress/apidocs (using flasgger)<br>
APIendpoint http://serveraddress/event (GET,POST)<br>

POST REQUEST BODY SAMPLE_ New Event:<br>
{
  "eventtype": "purchase",
  "metadata": {"test":"10000"},
  "source": "test3",
  "user": "test3"
}
GET EVENT SAMPLE:<br>
http://serveraddress/event?source=test1<br>