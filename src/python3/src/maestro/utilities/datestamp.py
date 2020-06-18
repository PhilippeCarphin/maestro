import copy
import math
import os.path
from datetime import datetime, timedelta

def get_day_of_week(datestamp):
    """
    Given a string datestamp like 2020040100 returns the day of week, where Sunday is 0
    """
    assert len(datestamp) >= 8 and datestamp.isdigit()
    year=int(datestamp[:4])
    month=int(datestamp[4:6])
    day=int(datestamp[6:8])
    
    python_dow=datetime(year, month, day).weekday()
    
    "python monday=0, maestro sunday=0, convert"
    return (python_dow+1)%7

def dashify_datestamp(datestamp):
    """
    Given:
        2020010112
    returns:
        2020-01-01-12
    """
    
    result=""
    while datestamp:
        a=2 if result else 4
        if result:
            result+="-"
        result+=datestamp[:a]
        datestamp=datestamp[a:]
    return result

def get_latest_yyyymmddhh_from_experiment_path(path):
    """
    Try to guess the latest datestamp run for this experiment.
    If it cannot find any, returns ""
    """
    latest=path+"/listings/latest/"
    if not os.path.isdir(latest):
        return ""
    
    logs=os.listdir(latest)
    datestamps=[]
    for log in logs:
        split=log.split(".")
        if len(split)>=3 and len(split[1])==14 and split[1].isdigit():
            datestamps.append(split[1][:10])
    
    if not datestamps:
        return ""
    
    return sorted(datestamps)[-1]

def get_yyyymmddhh(days_offset=0,hours_offset=0,hour_interval=12):
    "Returns the datestamp string for now, optional offsets."

    dt=datetime.now()+timedelta(days=days_offset,hours=hours_offset)
    month=str(dt.month).zfill(2)
    day=str(dt.day).zfill(2)
    hour=math.floor(dt.hour/hour_interval)*hour_interval
    hour=str(hour).zfill(2)

    return "%s%s%s%s"%(dt.year,month,day,hour)

def get_all_datestamps_from_tasks(tasks):
    "returns a sorted list of all datestamps from the tasks dictionary"
    all_dates=set()
    for task_name in tasks:
        for datestamp in tasks[task_name]:
            all_dates.add(datestamp)
    return sorted(list(all_dates))

def get_datetime(yyyymmddhh_string):
    a=yyyymmddhh_string
    assert len(a)==10
    y=a[:4]
    m=a[4:6]
    d=a[6:8]
    h=a[8:]
    return datetime(year=int(y),month=int(m),day=int(d),hour=int(h))

def get_datestamps(start_date,end_date,hour_intervals=("00","12")):
    cursor=get_datetime(start_date)
    end_dt=get_datetime(end_date)
    datestamps=[]
    while cursor<=end_dt:
        day_cursor=copy.copy(cursor)
        for hour_interval in hour_intervals:
            interval=int(hour_interval)
            day_cursor=cursor+timedelta(hours=interval)
            
            day=str(day_cursor.day).zfill(2)
            month=str(day_cursor.month).zfill(2)
            hour=str(day_cursor.hour).zfill(2)
            datestamp="%s%s%s%s"%(day_cursor.year,month,day,hour)
            datestamps.append(datestamp)
            
        cursor+=timedelta(hours=24)
    return datestamps