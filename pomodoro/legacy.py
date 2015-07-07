from django.db import connections

import collections
import time


NSTIMEINTERVAL = 978307200


class PomodoroBucket(object):
    @classmethod
    def midnight(cls, datetime):
        return time.mktime(
            datetime.replace(
                hour=0, minute=0, second=0, microsecond=0
            ).timetuple()
        ) - NSTIMEINTERVAL

    @classmethod
    def get(cls, database, start, minutes):
        # Assuming start is midnight, add a day to get the end
        end = start + 24 * 60 * 60
        c = connections[database].cursor()
        c.execute('SELECT Z_PK, cast(ZWHEN as integer), ZDURATIONMINUTES, ZNAME FROM ZPOMODOROS WHERE ZWHEN > %s AND ZWHEN < %s ORDER BY ZWHEN DESC', [start, end])

        buckets = collections.defaultdict(int)
        buckets['Unknown'] = minutes
        for zpk, zwhen, zminutes, zname in c.fetchall():
            buckets[zname] += zminutes
            buckets['Unknown'] -= zminutes
        return sorted(buckets.items(), key=lambda x: x[1], reverse=True)
