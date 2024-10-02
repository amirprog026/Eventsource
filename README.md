"# Eventsource" 
This project based on FLASK microframework which can collect  all events and unified them in an standard format:
Monitoring panel: http://serveraddress/panel
APIDOC: http://serveraddress/apidocs (using flasgger)
APIendpoint http://serveraddress/event (GET,POST)

POST REQUEST BODY SAMPLE_ New Event:
{
  "eventtype": "purchase",
  "metadata": {"test":"10000"},
  "source": "test3",
  "user": "test3"
}
GET EVENT SAMPLE:
http://serveraddress/event?source=test1