"""
Demo program for fetching trains info
"""

import asyncio
import datetime
from rzd.aiorzd import RzdFetcher, TimeRange

async def main():
    tomorrow = datetime.date.today()
    after_tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    delta_mounth = 2
    fetcher = RzdFetcher()
    timerange = TimeRange(
            datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, datetime.datetime.now().time().hour, datetime.datetime.now().time().minute),
            datetime.datetime(after_tomorrow.year, after_tomorrow.month+delta_mounth, after_tomorrow.day, 23, 59),
        )

    # print(timerange)

    trains = await fetcher.trains(
        'МОСКВА',
        'САНКТ-ПЕТЕРБУРГ',
        timerange
    )

    #
    # for train in trains:
    #     print(train)

    # trains = RzdFetcher.filter_trains(trains, ['Плацкартный', 'Купе'])
    # for train in filter(
    #         lambda t: any(s for s in t.seats.values()
    #                       # if s.price < 2000
    #                       ),
    #         trains,
    # ):
    #     print(train)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
