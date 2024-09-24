import unittest ,json

from app import queue_event 

from unittest.mock import patch, MagicMock 

class Testqueue_event(unittest.TestCase):

    @patch('pika.BlockingConnection')
    def test_valid_event_queued(self, mock_connection):
        mock_channel = mock_connection.return_value.channel.return_value
        event = {'message': 'test'}
        queue_event(event)
        mock_channel.basic_publish.assert_called_once_with(
            exchange='',
            routing_key='event_queue',
            body=json.dumps(event)
        ) 


    @patch('pika.BlockingConnection')
    def test_queue_event_success(self, mock_connection):
        mock_channel = MagicMock()
        mock_connection.return_value.channel.return_value = mock_channel
        event = {'eventid': '123', 'eventtype': 'test', 'source': 'unit_test', 'user': 'tester', 'metadata': {}}
        queue_event(event)
        mock_channel.basic_publish.assert_called_once_with(exchange='', routing_key='event_queue', body=json.dumps(event))
        mock_connection.return_value.close.assert_called_once() 


    @patch('pika.BlockingConnection')
    def test_queue_event_success(self, mock_connection):
        mock_channel = MagicMock()
        mock_connection.return_value.channel.return_value = mock_channel
        event = {'eventid': '123', 'eventtype': 'typeA', 'source': 'sourceA', 'user': 'userA', 'metadata': {}}
        queue_event(event)
        mock_channel.basic_publish.assert_called_once_with(exchange='', routing_key='event_queue', body=json.dumps(event))
        mock_connection.return_value.close.assert_called_once() 


    @patch('pika.BlockingConnection')
    def test_valid_event_added_to_queue(self, mock_connection):
        mock_channel = MagicMock()
        mock_connection.return_value.channel.return_value = mock_channel
        event = {'eventid': '1', 'eventtype': 'test', 'source': 'unit_test', 'metadata': {}, 'user': 'tester'}
        queue_event(event)
        mock_channel.basic_publish.assert_called_once_with(exchange='', routing_key='event_queue', body=json.dumps(event))
        mock_connection.return_value.close.assert_called_once() 


    @patch('pika.BlockingConnection')
    def test_queue_event(self, mock_connection):
        mock_channel = mock_connection.return_value.channel.return_value
        event = {'eventid': '1', 'eventtype': 'test', 'source': 'unit_test', 'user': 'test_user', 'metadata': {}}
        queue_event(event)
        mock_channel.queue_declare.assert_called_once_with(queue='event_queue')
        mock_channel.basic_publish.assert_called_once_with(exchange='', routing_key='event_queue', body=json.dumps(event)) 


    @patch('pika.BlockingConnection')
    def test_queue_event_success(self, mock_connection):
        mock_channel = MagicMock()
        mock_connection.return_value.channel.return_value = mock_channel
        event = {'eventid': '1', 'eventtype': 'type1', 'source': 'source1', 'user': 'user1', 'metadata': {}}
        queue_event(event)
        mock_channel.basic_publish.assert_called_once_with(
            exchange='',
            routing_key='event_queue',
            body=json.dumps(event)
        ) 


