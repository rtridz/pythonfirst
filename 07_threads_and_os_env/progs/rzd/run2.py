#!/usr/bin/env python3

import json
import os
import datetime
import asyncio

from aiotg import Bot, Chat
from rzd.aiorzd import RzdFetcher, UpstreamError
from rzd.config import QUERY_REGEXP_LIST
from rzd.helper import logger, QueryString, NotifyExceptions

os.environ.setdefault('BOT_CONFIG', 'rzd/config.json')

with open(os.environ['BOT_CONFIG']) as cfg:
    config = json.load(cfg)

bot = Bot(config['API_TOKEN'], name=config['BOT_NAME'])




def multibot(command, default=False):
    def decorator(fn):
        for r in QUERY_REGEXP_LIST:
            fn = bot.command(r'/%s@%s\s+%s' % (command, bot.name, r))(fn)
            fn = bot.command(r'/%s\s+%s' % (command, r))(fn)
            if default:
                fn = bot.command(r'@%s\s+%s' % (bot.name, r))(fn)

        return fn
    return decorator




async def get_trains(fetcher: RzdFetcher, query: QueryString):
    while True:
        try:
            trains = await fetcher.trains(
                query.city_from,
                query.city_to,
                query.time_range,
            )
            break
        except UpstreamError:
            await asyncio.sleep(0.5)
            continue

    filtered_trains = RzdFetcher.filter_trains(trains, query.types_filter)

    if query.max_price:
        filtered_trains = filter(lambda t: any(
            s for s in t.seats.values()
            if s.price < query.max_price and (
                not query.min_tickets or s.quantity >= query.min_tickets
            )
        ), trains)

    return list(filtered_trains), trains


@multibot('notify')
async def notify(chat: Chat, match):
    user = await chat.get_chat_member(chat.sender["id"])
    logger.info('notify {}'.format(user['result']['user']))

    async with NotifyExceptions(chat) as notifier:
        query = QueryString(match)
    if notifier.exception:
        return

    fetcher = RzdFetcher()
    async with NotifyExceptions(chat) as notifier:
        city_from = (await fetcher.get_city_autocomplete(query.city_from))['n']
        city_to = (await fetcher.get_city_autocomplete(query.city_to))['n']
    if notifier.exception:
        return

    msg = """Буду искать по запросу {} -> {}, с {} по {}{}{}{}""".format(
        city_from,
        city_to,
        query.time_range.start,
        query.time_range.end,
        ' не дороже {} рублей'.format(query.max_price)
        if query.max_price else '',
        ' только {}'.format(",".join(query.types_filter))
        if query.types_filter else '',
        ' не меньше {} мест в одном поезде'.format(query.min_tickets)
        if query.min_tickets else '',
    )
    await chat.send_text(msg)
    start_time = datetime.datetime.now()
    last_notify = start_time

    async with NotifyExceptions(chat):
        while True:
            filtered_trains, all_trains = await get_trains(fetcher, query)
            if filtered_trains:
                answer = 'Найдено: \n'
                for train in filtered_trains[0:30]:
                    answer += \
                        '<b>{date}</b>\n' \
                        '<i>{num} {title}</i>\n' \
                        '{seats}\n\n'.format(
                            date=train.departure_time,
                            num=train.number,
                            title=train.title,
                            seats="\n".join(
                                " - %s" % s for s in train.seats.values()
                            ),
                        )
                if len(filtered_trains) > 30:
                    answer += 'Есть ещё поезда, сократите диапазон дат... '

                await chat.send_text(answer, parse_mode='HTML')
                break
            else:
                logger.info('sleep for 30 sec')
                await asyncio.sleep(30)

            now = datetime.datetime.now()
            if (now - start_time).seconds > 86400:
                await chat.send_text('Ничего не нашёл. Прекращаю работу.')
                break
            elif (now - last_notify).seconds > 3600:
                last_notify = now
                await chat.send_text('Всё ещё нет билетов. Ищу...')


@multibot('search', default=True)
async def search(chat: Chat, match):
    user = await chat.get_chat_member(chat.sender["id"])
    logger.info('search;{};{}'.format(user['result']['user'], match.group(0)))
    await chat.send_text('Ищу билеты...')

    async with NotifyExceptions(chat) as notifier:
        query = QueryString(match)
    if notifier.exception:
        return

    filtered_trains, all_trains = await get_trains(RzdFetcher(), query)

    if not filtered_trains:
        if all_trains:
            answer = 'По запросу поездов нет, но есть более дорогие'
        else:
            answer = 'По вашему запросу поездов нет'
    else:
        answer = 'Найдено: \n'
        for train in filtered_trains[0:30]:
            answer += \
                '<b>{date}</b>\n' \
                '<i>{num} {title}</i>\n' \
                '{seats}\n\n'.format(
                    date=train.departure_time,
                    num=train.number,
                    title=train.title,
                    seats="\n".join(
                        " - %s" % s for s in train.seats.values()
                    ),
                )
        if len(filtered_trains) > 30:
            answer += 'Есть ещё поезда, сократите диапазон дат... '

    await chat.send_text(answer, parse_mode='HTML')


@bot.default
def default(chat: Chat, match):
    logger.warning('Not matched request: {}'.format(match))
    return chat.send_text('Не понял...')


@bot.command("(/start|/?help)")
def usage(chat: Chat, match):
    demo_date = datetime.date.today() + datetime.timedelta(days=30)
    logger.info('Start request: {}'.format(match))
    text = """
Привет! Я умею искать билеты на поезд.
Как спросить у меня список билетов:
/search москва, спб, 4.{month:02d} 20:00 - 5.{month} 03:00
    """.format(month=demo_date.month)
    return chat.send_text(text)


if __name__ == '__main__':
    logger.setLevel(logger.INFO)
    logger.warning('Start RZD telegram bot...')
    bot.run()