import random,json,string,requests
def post_event(payload):
    try:
        response = requests.post(TARGET_ENDPOINT="http://194.146.123.166:4433/event", json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        print("POSTED")
        # Return the response from the target endpoint
        return str(response.json())
    except requests.exceptions.RequestException as e:
        return f"ERROR: {str(e)}"
def generate_random_event():
    # Predefined lists of event types and sources
    event_types = ['order', 'action', 'entrance', 'exit', 'click', 'purchase']
    sources = ['web', 'mobile', 'email', 'ad', 'social_media', 'direct']

    # Generate a random eventtype and source
    eventtype = random.choice(event_types)
    source = random.choice(sources)

    # Generate a random username or default to 'anonymous'
    user = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

    # Randomly decide the number of metadata key-value pairs (could be 0 or more)
    metadata = {}
    num_metadata_items = random.randint(0, 10)
    
    for _ in range(num_metadata_items):
        key = ''.join(random.choices(string.ascii_lowercase, k=5))
        value = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        metadata[key] = value

    # Create the event dictionary
    event = {
        'eventtype': eventtype,
        'source': source,
        'user': user,
        'metadata': json.dumps(metadata)  # Ensure metadata is properly formatted as a JSON string
    }

    return event
def send_batch_events(number:int=10):
    for item in range(number):
        print(post_event(generate_random_event()))