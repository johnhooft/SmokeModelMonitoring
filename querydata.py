import sage_data_client
from datetime import datetime, timedelta
from smokeclass import smoke
import ast
import signal
import time

def min_only(timestamp):
    # Truncate the timestamp to the hour and minute components
    return timestamp.replace(second = 0, microsecond = 0, nanosecond = 0)

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Sage client data query took too long.")

def getdata(time_start, time_end, plugin, node):
    # Set the timeout value in seconds (10 seconds in this case)
    timeout = 10

    # Set the signal handler for the timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    try:
        # Get the current time in ISO format
        current_time = datetime.utcnow() - timedelta(minutes=time_start)

        # Calculate the time from 15 minutes ago
        time_n_minutes_ago = datetime.utcnow() - timedelta(minutes=time_end)
        time_n_minutes_ago_iso = time_n_minutes_ago.isoformat()

        # Query data from Sage
        df = sage_data_client.query(
            start=time_n_minutes_ago_iso,
            end=current_time, 
            filter={
                "plugin": plugin,
                "vsn": node
            }
        )

    except TimeoutException:
        # Handle the timeout exception here, for example, log an error message
        print("Sage client data query took too long.")
        return None, None
    
    finally:
        # Disable the alarm after the query, whether it succeeded or not
        signal.alarm(0)

    smokearray = []
    # Sort data and compile smoke probs, and images into one data point.
    for i in range(len(df)):
        time = min_only(df.iloc[i, 0])
        val = df.iloc[i, 2]

        if len(smokearray)!=0:
            for item in smokearray:
                if item.timestamp == time: 
                    s = item
                    break
                else: s = smoke(time)
        else: s = smoke(time)

        if 'https' in val:
            if 'previous' in val:
                s.imageprev = val
            elif 'current' in val:
                s.imagecurr = val
            elif 'next' in val:
                s.imagenext = val
        
        else:
            val2d = ast.literal_eval(val)
            val2d = [inner_list[0] for inner_list in val2d[0]]
            s.prob = val2d

        smokearray.append(s)

    for item in smokearray:
        if not item.prob: smokearray.remove(item)

    return smokearray, df

