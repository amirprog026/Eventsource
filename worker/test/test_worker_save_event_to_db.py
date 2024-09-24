import unittest 

from peewee import MySQLDatabase 
from datetime import datetime
from worker import save_event_to_db, Event ,db

class Testsave_event_to_db(unittest.TestCase):

    def test_save_event(self):
        event = {
            'eventid': '12345',
            'eventtype': 'user_signup',
            'source': 'web',
            'metadata': {'user_id': 'user_1'},
            'user': 'test_user'
        }
        save_event_to_db(event)
        saved_event = Event.get(Event.eventid == '12345')
        self.assertEqual(saved_event.eventtype, 'user_signup')
        self.assertEqual(saved_event.source, 'web')
        self.assertEqual(saved_event.metadata, {'user_id': 'user_1'})
        self.assertEqual(saved_event.user, 'test_user') 


    def test_save_event_without_user(self):
        event = {
            'eventid': 'test_event_1',
            'eventtype': 'test_type',
            'source': 'test_source',
            'user': '',
            'metadata': {}
        }
        save_event_to_db(event)
        saved_event = Event.get(Event.eventid == 'test_event_1')
        self.assertEqual(saved_event.user, 'anonymous')
        self.assertEqual(saved_event.eventtype, 'test_type')
        self.assertEqual(saved_event.source, 'test_source')
        self.assertEqual(saved_event.metadata, {}) 


    def setUp(self):
        self.event = {
            'eventid': '1',
            'eventtype': 'test_event',
            'source': 'unit_test',
            'metadata': {'key': 'value'},
            'user': 'test_user'
        }

    def test_save_event(self):
        save_event_to_db(self.event)
        saved_event = Event.get(Event.eventid == self.event['eventid'])
        self.assertEqual(saved_event.eventtype, self.event['eventtype'])
        self.assertEqual(saved_event.source, self.event['source'])
        self.assertEqual(saved_event.metadata, self.event['metadata'])
        self.assertEqual(saved_event.user, self.event['user']) 


    def setUp(self):
        db.connect()
        db.create_tables([Event], safe=True)

    def tearDown(self):
        db.drop_tables([Event])

    def test_save_event(self):
        event = {
            'eventid': 'unique_event_1',
            'eventtype': 'type_a',
            'source': 'source_a',
            'metadata': {'key': 'value'},
            'user': 'user_a'
        }
        save_event_to_db(event)
        saved_event = Event.get(Event.eventid == 'unique_event_1')
        self.assertEqual(saved_event.eventtype, 'type_a')
        self.assertEqual(saved_event.source, 'source_a')
        self.assertEqual(saved_event.metadata, {'key': 'value'})
        self.assertEqual(saved_event.user, 'user_a') 


    def test_save_event(self):
        event = {
            'eventid': '1',
            'eventtype': 'test_event',
            'source': 'test_source',
            'user': 'test_user',
            'metadata': {'key': 'value'},
            'occured_at': datetime.now()
        }
        save_event_to_db(event)
        saved_event = Event.get(Event.eventid == '1')
        self.assertEqual(saved_event.eventtype, 'test_event')
        self.assertEqual(saved_event.source, 'test_source')
        self.assertEqual(saved_event.user, 'test_user')
        self.assertEqual(saved_event.metadata, {'key': 'value'}) 


    def test_save_event(self):
        event = {
            'eventid': '123',
            'eventtype': 'test_event',
            'source': 'unit_test',
            'user': 'test_user',
            'metadata': {'key': 'value'}
        }
        save_event_to_db(event)
        saved_event = Event.get(Event.eventid == '123')
        self.assertEqual(saved_event.eventtype, 'test_event')
        self.assertEqual(saved_event.source, 'unit_test')
        self.assertEqual(saved_event.user, 'test_user')
        self.assertEqual(saved_event.metadata, {'key': 'value'}) 


    def test_missing_eventtype(self):
        event = {
            'eventid': '12345',
            'eventtype': '',  # Missing eventtype
            'source': 'test_source',
            'metadata': {},
            'user': 'test_user'
        }
        with self.assertRaises(Exception):
            save_event_to_db(event)
 


    def setUp(self):
        self.event = {
            'eventid': '12345',
            'eventtype': 'test_event',
            'source': '',
            'metadata': {},
            'user': 'test_user'
        }

    def test_missing_source(self):
        save_event_to_db(self.event)
        saved_event = Event.get(Event.eventid == '12345')
        self.assertEqual(saved_event.source, '')

    def tearDown(self):
        Event.delete().where(Event.eventid == '12345').execute() 


    def setUp(self):
        self.event = {
            'eventid': '12345',
            'eventtype': 'test_event',
            'source': 'test_source',
            'metadata': None,
            'user': 'test_user'
        }

    def test_save_event_with_null_metadata(self):
        save_event_to_db(self.event)
        saved_event = Event.get(Event.eventid == self.event['eventid'])
        self.assertIsNone(saved_event.metadata)

    def tearDown(self):
        Event.delete().where(Event.eventid == self.event['eventid']).execute() 


    def setUp(self):
        db.connect()
        db.create_tables([Event], safe=True)

    def tearDown(self):
        db.drop_tables([Event])

    def test_empty_user_defaults_to_anonymous(self):
        event = {
            'eventid': 'test_event_1',
            'eventtype': 'test_type',
            'source': 'test_source',
            'user': '',
            'metadata': {}
        }
        save_event_to_db(event)
        saved_event = Event.get(Event.eventid == 'test_event_1')
        self.assertEqual(saved_event.user, 'anonymous')


     


    def setUp(self):
        self.large_metadata = {'key': 'value' * 10000}  # Large metadata object
        self.event = {
            'eventid': 'test_event_1',
            'eventtype': 'test_type',
            'source': 'test_source',
            'metadata': self.large_metadata,
            'user': 'test_user'
        }

    def test_save_event_with_large_metadata(self):
        save_event_to_db(self.event)
        saved_event = Event.get(Event.eventid == self.event['eventid'])
        self.assertEqual(saved_event.eventid, self.event['eventid'])
        self.assertEqual(saved_event.metadata, self.large_metadata) 


    def test_save_event_with_special_characters_in_user(self):
        event = {
            'eventid': 'event_123',
            'eventtype': 'user_action',
            'source': 'web',
            'user': 'user!@#$%^&*()',
            'metadata': {'key': 'value'}
        }
        save_event_to_db(event)
        saved_event = Event.get(Event.eventid == 'event_123')
        self.assertEqual(saved_event.user, 'user!@#$%^&*()')
        self.assertEqual(saved_event.eventtype, 'user_action')
        self.assertEqual(saved_event.source, 'web')
        self.assertEqual(saved_event.metadata, {'key': 'value'}) 


