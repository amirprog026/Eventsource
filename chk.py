import datetime 
def parse_timestamp(line):
    """Extract timestamp from the log line and return as a datetime object."""
    try:
        timestamp_str = line.split('*')[0].strip()
        print(timestamp_str)
        return datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
    except Exception as ecx:
        print(ecx)
        return None
def read_recent_lines(file_path, time_threshold=datetime.datetime.now() - datetime.timedelta(hours=24)):
    """Read lines from the log file that are within the last 24 hours."""
    recent_lines = []
    with open(file_path, 'r') as file:
        for line in file:
            timestamp = parse_timestamp(line)
            
            if timestamp and timestamp > time_threshold:
                recent_lines.append(line)
                print(line.split()[-4])
    return recent_lines

print(read_recent_lines("/var/log/worker_eventlogs.log"))