import datetime

import logging
import re

from rzd.aiorzd import TimeRange
from rzd.config import shortcuts


class TooLongPeriod(Exception):
    pass


logger = logging.getLogger('aiorzd_bot')

class QueryString:
    def __init__(self, match):
        d = {v: k for k, vs in shortcuts.items() for v in vs}
        from_city = match.group('from').strip()
        to_city = match.group('to').strip()
        self.city_from = d.get(from_city, from_city)
        self.city_to = d.get(to_city, to_city)

        # TODO: filtering by wagon type
        max_price = None
        try:
            when = match.group('when').strip()
            if '<' in when:
                when, max_price = when.split('<')
                max_price, min_tickets = self.parse_max_price(max_price)
            else:
                when, min_tickets = self.parse_max_price(when)
        except ValueError:
            when = None
            min_tickets = None

        self.max_price = None
        if max_price and max_price.strip():
            try:
                self.max_price = int(max_price.strip())
            except ValueError:
                pass

        self.time_range = self.parse_when(when.strip())
        self.min_tickets = min_tickets
        self.types_filter = None

    @staticmethod
    def parse_max_price(max_price):
        if '#' in max_price:
            max_price, required_tickets = max_price.split('#')
            return max_price.strip(), int(required_tickets.strip())
        return max_price, None

    @staticmethod
    def parse_when(s):
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0,
                                                microsecond=0)

        if not s:
            now = datetime.datetime.now()
            return TimeRange(now, now + datetime.timedelta(days=1))
        r = re.match(
            r'0?(\d+)[./]0?(\d+)\s+0?(\d+):0?(\d+)'
            r'\s*[-–]\s*'
            r'0?(\d+)[./]0?(\d+)\s+0?(\d+):0?(\d+)',
            s,
        )
        if r:
            start = datetime.datetime(
                today.year,
                int(r.group(2)),
                int(r.group(1)),
                int(r.group(3)),
                int(r.group(4)),
            )
            end = datetime.datetime(
                today.year,
                int(r.group(6)),
                int(r.group(5)),
                int(r.group(7)),
                int(r.group(8)),
            )
            if start < today:
                start = start.replace(year=today.year + 1)
                end = end.replace(year=today.year + 1)
                if (end - start).days > 7:
                    raise TooLongPeriod('Too long period, use at max 7 days')
            return TimeRange(start, end)
        r = re.match(r'0?(\d+)(?:\s*[-–]\s*(\d+))?', s)
        if r:
            start = datetime.datetime(
                today.year,
                today.month,
                int(r.group(1)),
                0,
                0,
            )

            if start < today:
                if today.month == 12:
                    start = start.replace(month=1, year=start.year + 1)
                else:
                    start = start.replace(month=today.month + 1)

            end = start.replace(hour=23, minute=59)
            if r.group(2) is not None:
                end = end.replace(
                    day=int(r.group(2))
                )
            if end < start:
                if start.month == 12:
                    end = end.replace(month=1, year=end.year + 1)
                else:
                    end = end.replace(month=end.month + 1)

            if abs((end - start).days) > 7:
                raise TooLongPeriod('Too long period, use at max 7 days')
            return TimeRange(start, end)

        logger.error('Cannot parse date range "%s"', s)
        raise ValueError('Не понял диапазон дат...')

class NotifyExceptions:
    def __init__(self, chat):
        self.chat = chat
        self.exception = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.exception = exc_val
            await self.chat.send_text("Ошибка: %s" % str(exc_val))
            logger.error('Exception: %s', repr(exc_val))

