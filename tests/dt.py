import time
import datetime

from datetime import timedelta

if __name__ == "__main__":
    print(time.time())
    # time.sleep()
    dt = datetime.datetime.now()
    print(dt.time(), dt.timestamp())
    
    xx = datetime.datetime.fromtimestamp(dt.timestamp())
    print(xx)
    xx += timedelta(days=15)
    print(xx)
    
    print(xx.timetuple())
    