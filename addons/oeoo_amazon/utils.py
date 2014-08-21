# -*- coding: utf-8 -*-

from datetime import datetime,timedelta
import time

def calcCreatedAfter(last_import_time):
    if not last_import_time:
        today = datetime.now()
        DD = timedelta(days=30)
        earlier = today - DD
        earlier_str = earlier.strftime("%Y-%m-%dT%H:%M:%S")
        createdAfter = earlier_str+'Z'
    else:
        last_import_time=last_import_time.split(' ')[0]+' 00:00:00'
        db_import_time = time.strptime(last_import_time, "%Y-%m-%d %H:%M:%S")
        db_import_time = time.strftime("%Y-%m-%dT%H:%M:%S",db_import_time)
        createdAfter = time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime(time.mktime(time.strptime(db_import_time,"%Y-%m-%dT%H:%M:%S"))))
        createdAfter = str(createdAfter)+'Z'
    return createdAfter