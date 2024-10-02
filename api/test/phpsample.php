<?php

require_once __DIR__ . '/vendor/autoload.php';

use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

function queue_event($event, $trackid) {
    // RabbitMQ connection details
    $host = '4.2.1.4';        // RabbitMQ server address
    $port = 5672;             // RabbitMQ port
    $vhost = '/';             // Virtual host
    $user = 'guest';          // RabbitMQ username
    $password = 'guest';      // RabbitMQ password

    // Create the connection to RabbitMQ
    $connection = new AMQPStreamConnection($host, $port, $user, $password, $vhost);
    $channel = $connection->channel();

    // Set the trackid in the event array
    $event['trackid'] = $trackid;

    // Declare the queue where the event will be published
    $channel->queue_declare('event_queue', false, true, false, false);

    // Encode the event as JSON
    $messageBody = json_encode($event);

    // Create an AMQP message with the event
    $message = new AMQPMessage($messageBody, [
        'delivery_mode' => AMQPMessage::DELIVERY_MODE_PERSISTENT
    ]);

    // Publish the message to the RabbitMQ queue
    $channel->basic_publish($message, '', 'event_queue');

    // Optionally log the event (uncomment to enable logging)
    // error_log("TrackID {$event['trackid']} queued");

    // Close the channel and connection
    $channel->close();
    $connection->close();
}

// Generate a random trackid (equivalent to secrets.token_hex(12) in Python)
function generate_trackid($length = 12) {
    return bin2hex(random_bytes($length));
}

// Check if the script is handling a POST request
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Read the POST body (which contains the event data)
    $event = json_decode(file_get_contents('php://input'), true);

    // Generate a trackid
    $trackid = generate_trackid();

    // Queue the event
    queue_event($event, $trackid);

    // Send a success response
    echo json_encode(['status' => 'success', 'trackid' => $trackid]);
} else {
    // Send a failure response for non-POST requests
    echo json_encode(['status' => 'error', 'message' => 'Invalid request method']);
}
