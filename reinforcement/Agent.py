import random
from datetime import datetime, timedelta
import time
from Account import Account
from dotenv import load_dotenv


def str_time_prop(start, end, time_format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(time_format, time.localtime(ptime))


def random_date(start, end, prop):
    return str_time_prop(start, end, '%m/%d/%Y %I:%M %p', prop)


period = random.randint(10, 30)
random_start_date = random_date(
    "1/1/2015 1:30 PM", "8/1/2022 4:50 AM", random.random())
START_DATE = datetime.strptime(random_start_date.split(
    " ")[0], "%m/%d/%Y").strftime("%Y-%m-%dT%H:%M:%SZ")
END_DATE = (datetime.strptime(START_DATE, "%Y-%m-%dT%H:%M:%SZ") -
            timedelta(days=period)).strftime("%Y-%m-%dT%H:%M:%SZ")

load_dotenv()
myAccount = Account(
    key="PAPER_API_KEY", secretKey="PAPER_API_KEY_SECRET", endpoint="PAPER_API_ENDPOINT"
)
