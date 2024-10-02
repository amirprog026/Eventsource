# Date: 2024-10-2
# Author: Generated by GoCodeo.

import unittest ,datetime

from peewee import MySQLDatabase 
from models import Event

class TestEvent(unittest.TestCase):

    def test_create_event(self):
        event = Event.create(eventtype='order', source='web', user='test_user', metadata={'key': 'value'})
        self.assertIsNotNone(event.eventid)
        self.assertEqual(event.eventtype, 'order')
        self.assertEqual(event.source, 'web')
        self.assertEqual(event.user, 'test_user')
        self.assertEqual(event.metadata, {'key': 'value'}) 


    def test_get_eventcount_lasthours(self):
        # Setup: Create test events in the database
        Event.create(eventtype='action', source='source1', user='user1', occured_at=datetime.datetime.now() - datetime.timedelta(hours=1))
        Event.create(eventtype='action', source='source2', user='user2', occured_at=datetime.datetime.now() - datetime.timedelta(hours=2))
        Event.create(eventtype='action', source='source1', user='user3', occured_at=datetime.datetime.now() - datetime.timedelta(hours=3))
        
        # Execute: Call the method to get event count for the last 24 hours
        result = Event.get_eventcount_lasthours(24)
        
        # Verify: Check if the result matches the expected count
        self.assertEqual(result, {'2023-10-03 14:00:00': 1, '2023-10-03 13:00:00': 1, '2023-10-03 12:00:00': 1})
        
        # Cleanup: Remove test events
        Event.delete().execute() 


    def test_fetch_events_by_type_last_h(self):
        # Setup: Create sample events in the database
        Event.create(eventtype='sale', source='source1', user='user1', metadata={'amount': 100})
        Event.create(eventtype='product_view', source='source2', user='user2', metadata={})
        Event.create(eventtype='visit', source='source3', user='user3', metadata={})

        # Define event types
        sale_event_types = ['sale']
        productview_types = ['product_view']
        visit_types = ['visit']

        # Act: Fetch events
        result = Event.fetch_events_by_type_last_h(sale_event_types, productview_types, visit_types)

        # Assert: Check if the fetched events match the expected output
        self.assertEqual(len(result['saleevents']), 1)
        self.assertEqual(len(result['productviewevents']), 1)
        self.assertEqual(len(result['visitevents']), 1)
        self.assertEqual(result['saleamount'], 100)


     


    def test_event_count_classified_by_source(self):
        # Setup: Create test events
        Event.create(eventtype='action', source='source1')
        Event.create(eventtype='action', source='source2')
        Event.create(eventtype='order', source='source1')
        Event.create(eventtype='order', source='source1')
        Event.create(eventtype='action', source='source1')

        # Act: Get event counts classified by source
        result = Event.count_events_by_source(lasthours=24)

        # Assert: Check the counts are correct
        self.assertEqual(result['source1'], 3)
        self.assertEqual(result['source2'], 1) 


    def test_get_data_count_by_user(self):
        # Arrange
        Event.create(user='user1', eventtype='purchase', metadata={})
        Event.create(user='anonymous', eventtype='view', metadata={})
        Event.create(user='user2', eventtype='purchase', metadata={})

        # Act
        total_users, users_with_purchase_events, anonymous_events = Event.get_data_count_by_user(['purchase'])

        # Assert
        self.assertEqual(total_users, 3)
        self.assertEqual(users_with_purchase_events, 2)
        self.assertEqual(anonymous_events, 1) 


    def test_get_last_30_days_events(self):
        # Setup: Create sample events
        Event.create(eventtype='action', source='source1', user='user1', metadata={'key': 'value'})
        Event.create(eventtype='order', source='source2', user='user2', metadata={'key': 'value'})
        
        # Act: Retrieve events from the last 30 days
        events = Event.get_last_30_days_events()
        
        # Assert: Check if events are ordered by occurrence date
        self.assertTrue(all(events[i].occured_at <= events[i + 1].occured_at for i in range(len(events) - 1)))
        
        # Cleanup: Delete created events
        Event.delete().execute() 


if __name__ == '__main__':
    unittest.main()