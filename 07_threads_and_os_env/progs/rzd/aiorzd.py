#!/usr/bin/env python3

import asyncio
import datetime
import json
import logging
from collections import OrderedDict
from inspect import stack
from typing import Iterable
import aiohttp


def __func__():
    """ Returns current function name """
    return stack()[1][3]


def _loads(s, *args, **kwargs):
    return json.loads(s, *args, object_pairs_hook=OrderedDict, **kwargs)


class WrongQuery(Exception):
    pass


class CaptchaRequired(Exception):
    pass


class NoStation(RuntimeError):
    pass


class UpstreamError(RuntimeError):
    """
    {"result": "OK", "TransferSearchMode": "MANUAL",
         "timestamp": "31.12.2016 03:34:59.488", "flFPKRoundBonus": false,
         "tp": [{"state": "Trains", "expressErr": true, "msgList": [{
            "message": "Невозможно установить соединение с АСУ «Экспресс-3». "
                       "Пожалуйста, попробуйте выполнить запрос позже",
            "addInfo": "code: UNABLE_TO_CONNECT(402)",
            "errType": "ERROR"}],
                 "from": "ВЕЛЬСК", "where": "САНКТ-ПЕТЕРБУРГ",
                 "date": "05.01.2017", "fromCode": 2010020,
                 "whereCode": 2004000, "list": []}], "discounts": {},
         "tipFlags": {"Ukr": 0}}


    <H1>SRVE0255E: A WebGroup/Virtual Host to handle /timetable/public/ru has
    not been defined.</H1><BR><H3>SRVE0255E: A WebGroup/Virtual Host to handle
    pass.rzd.ru:80 has not been defined.</H3><BR>
    <I>IBM WebSphere Application Server</I>
    """
    pass


class TimeRange:
    def __init__(self, start: datetime.datetime, end: datetime.datetime):
        self.start = start
        self.end = end

    def __str__(self):
        return "{} - {}".format(
            self.start.isoformat(),
            self.end.isoformat(),
        )


class Place:
    types = ['Плацкартный', 'Купе', 'Общий', 'Сидячий', 'Люкс', 'Мягкий', 'Бизнес класс',
             'Вагон - бистро', 'Первый класс', 'СВ', 'Сидячий', 'Эконом', 'Эконом +']


    # seat, platzkart, coupe, lux, soft = range(5)
    def __init__(self, typ: str=None, quantity: int=0, price: float=None):
        self.type = typ
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return "%s : %s (%.2f)" % (self.type, self.quantity, self.price)


class Train:
    def __init__(self, number: int=0, title: str='',
                 departure_time: datetime.datetime=None,
                 arrival_time: datetime.datetime=None,
                 elreg: bool=False):
        self.number = number
        self.title = title
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.elreg = elreg
        self.seats = OrderedDict()

    def __str__(self):
        seats = ", ".join([str(s) for s in self.seats.values()])
        return "(%s) %s [%s] %s : [%s]" % (
            self.number,
            self.title,
            self.departure_time,
            '*E*' if self.elreg else '',
            seats)


class RzdRequest:
    session_counter = 1

    def __init__(self, src_code: str, dst_code: str, date: datetime.date,
                 time_range: str=None):
        self.request_id = None
        self.session = self.__class__.session_counter
        self.src_code = src_code
        self.dst_code = dst_code
        self.date = date
        self.time = ('0-24' if time_range is None else time_range)
        self.result = None
        self.counter = 0

        self.__class__.session_counter += 1

    def __repr__(self):
        return "{}->{} {} {}".format(
            self.src_code,
            self.dst_code,
            self.date,
            self.time,
        )

    @staticmethod
    def get_instances_from_range(
            src_сode: str,
            dst_сode: str,
            time_range: TimeRange) -> Iterable['RzdRequest']:
        """
        Generate list or requests for each day in time range
        """

        dt = time_range.start

        end_hour = time_range.end.hour
        if time_range.end.minute:
            end_hour += 1

        if time_range.start.date() == time_range.end.date():
            time = "{}-{}".format(time_range.start.hour, end_hour)
            result = [
                RzdRequest(src_сode, dst_сode, dt.date(), time)
            ]
        else:
            time = "{}-{}".format(time_range.start.hour, '24')
            result = [
                RzdRequest(src_сode, dst_сode, dt.date(), time)
            ]
            dt += datetime.timedelta(days=1)
            while dt.date() < time_range.end.date():
                time = "{}-{}".format('0', '24')
                result.append(
                    RzdRequest(src_сode, dst_сode, dt.date(), time)
                )
                dt += datetime.timedelta(days=1)
            time = "{}-{}".format('0', end_hour)
            result.append(
                RzdRequest(src_сode, dst_сode, dt.date(), time)
            )
        return result


class RzdFetcher:
    site_url = 'https://pass.rzd.ru'
    request_url = '/timetable/public/ru'
    suggest_url = '/suggester'

    def __init__(self):
        self.wait_tries = 20
        self.session = aiohttp.ClientSession()
        logging.debug(
            " (%s.%s) : %s" % (self.__class__.__name__, __func__(), 'start'))

    def __del__(self):
        self.session.close()

    @staticmethod
    def filter_trains(trains: Iterable[Train],
                      types: Iterable[str]) \
            -> Iterable[Train]:
        if not types:
            return trains

        result = []
        for train in trains:
            train_done = False
            for seat in train.seats.values():
                if train_done:
                    break
                if seat.type in types:
                    result.append(train)
                    train_done = True
        return result

    async def _do_autocomplete_request(self, text: str) -> dict:
        url = "{}{}".format(
            self.site_url,
            self.suggest_url,
        )
        params = {
            'stationNamePart': text.upper(),
            'lang': 'ru',
            'lat': '0',
            'compactMode': 'y',
        }
        async with self.session.get(url, params=params) as r:
            try:
                response = await r.json(loads=_loads)
            except json.JSONDecodeError:
                raise UpstreamError("Decode error: {}".format(
                    await r.text()
                ))
            else:
                if not response:
                    raise NoStation("Station not found: {}".format(text))
                return response

    async def get_city_autocomplete(self, name: str) -> dict:
        error = None
        for _ in range(10):
            try:
                response = await self._do_autocomplete_request(name)
            except UpstreamError as e:
                error = e
                await asyncio.sleep(0.5)
            else:
                break
        else:
            raise UpstreamError(error)

        search_name = name.upper()
        result = next((x for x in response if x['n'] == search_name), None)
        if not result:
            result = next((
                x for x in response if x['n'].startswith(search_name)
            ), None)
            if not result:
                raise NoStation("Station not found: {}".format(name))

        return result

    async def get_city_code(self, name: str) -> str:
        return (await self.get_city_autocomplete(name))['c']

    @staticmethod
    def _parse_trains_list(trains_json: dict):
        trains = list()
        for t in trains_json['tp'][0]['list']:
            train = Train()
            train.number = t['number']
            train.title = "%s - %s" % (t['route0'], t['route1'])
            train.departure_time = datetime.datetime.strptime(
                t['time0'] + ' ' + t['date0'], "%H:%M %d.%m.%Y")
            train.arrival_time = datetime.datetime.strptime(
                t['time1'] + ' ' + t['date1'], "%H:%M %d.%m.%Y")
            train.elreg = t['elReg']

            for s in t['cars']:
                price = float(s['tariff'])
                train.seats[s['type']] = Place(
                    typ=s['typeLoc'],
                    quantity=int(s['freeSeats']),
                    price=price,
                )

            trains.append(train)

        return trains

    async def send_query(self, rzd_req: RzdRequest):
        # send search form
        logging.debug(
            " (%s.%s) : %s" % (
                self.__class__.__name__,
                __func__(),
                'search ...',
            )
        )
        post_params = {
            'checkSeats': '1',
            'dir': '0',
            'tfl': '3',
            'dt0': rzd_req.date.strftime('%d.%m.%Y'),
            'code0': str(rzd_req.src_code),
            'code1': str(rzd_req.dst_code),
            'ti0': rzd_req.time
        }
        if rzd_req.request_id is not None:
            post_params['rid'] = rzd_req.request_id

        trains_url = '%s%s%s' % (
            self.site_url,
            self.request_url,
            '?layer_id=5827',
        )

        result = None
        try:
            for _ in range(10):
                async with self.session.post(trains_url, data=post_params) as r:
                    result = await r.text()
                    try:
                        response = _loads(result)
                    except json.JSONDecodeError:
                        await asyncio.sleep(0.5)
                    else:
                        break
            else:
                raise UpstreamError("Decode error: {}".format(
                    result
                ))

        except ValueError:
            raise WrongQuery(
                'Error answer. Wrong date or complex query.\n%s' % result
            )

        if response.get('error'):
            # TODO Parse error messages
            raise CaptchaRequired(response.get('error'))

        tp = response.get('tp', [])
        if tp and tp[0]['msgList'] and \
                tp[0]['msgList'][0].get('errType') == 'ERROR':
            raise UpstreamError(tp[0]['msgList'][0]['message'])
        elif response['result'] == 'OK':
            return self._parse_trains_list(response)
        elif response['result'] == 'RID':
            rzd_req.request_id = response['RID']
        return None

    async def trains(self, src: str, dst: str, departure_range: TimeRange) \
            -> Iterable[Train]:
        return await self.trains_by_code(
            await self.get_city_code(src),
            await self.get_city_code(dst),
            departure_range,
        )

    async def trains_by_code(self, src_сode: str, dst_сode: str,
                             departure_range: TimeRange):
        rzd_requests = RzdRequest.get_instances_from_range(
            src_сode,
            dst_сode,
            departure_range,
        )

        logging.debug(
            " (%s.%s) : %s" % (
                self.__class__.__name__,
                __func__(),
                'fetching trains info...'
            )
        )

        fetching = True
        while fetching:
            await asyncio.sleep(1)

            fetching = False
            try:
                for r in rzd_requests:
                    if r.result is None:
                        r.result = await self.send_query(r)
                        r.counter += 1
                    if r.result is None and r.counter < self.wait_tries:
                        fetching = True
            except CaptchaRequired:
                fetching = True
                # rebuild requests
                logging.warning('Captcha request')
                RzdRequest.session_counter += 100
                rzd_requests = RzdRequest.get_instances_from_range(
                    src_сode,
                    dst_сode,
                    departure_range,
                )
                await asyncio.sleep(120)

        logging.debug(
            " (%s.%s) : %s" % (
                self.__class__.__name__,
                __func__(),
                'parsing ...',
            )
        )

        trains = []
        for r in rzd_requests:
            if r.result is not None:
                trains.extend(r.result)

        return trains
