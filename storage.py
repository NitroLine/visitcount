import datetime
import time

import redis

from .config import SESSION_TIMEOUT


class VisitInfo:
    def __init__(self, origin, client_id, path, referer, browser, language,
                 platform):
        self.origin = origin
        self.client_id = client_id
        self.path = path
        self.referer = referer
        self.browser = browser
        self.language = language
        self.platform = platform
        self.date = str(datetime.datetime.now().date())

    def __str__(self):
        return f'{self.date} | ' \
               f'{self.origin}{self.path} from' \
               f' {self.client_id}-{self.language}-' \
               f'{self.platform}-{self.browser}'


class RedisStorage:
    def __init__(self, config):
        self.redis = redis.Redis(**config)

    def add_information(self, visit_info: VisitInfo):
        self.redis.sadd(f'dates', visit_info.date)
        self.redis.sadd(f'{visit_info.date}:{visit_info.origin}:paths',
                        visit_info.path)
        self._recalculate_visits_info(visit_info)
        self._recalculate_clients_info(visit_info)
        self._recalculate_referer_info(visit_info)
        self._recalculate_deep(visit_info)

    def _recalculate_referer_info(self, visit_info: VisitInfo):
        if len(visit_info.referer) > 0:
            self.redis.sadd(
                f'{visit_info.date}:{visit_info.origin}:'
                f'referer:{visit_info.path}',
                visit_info.referer)
            self.redis.hincrby(
                f'{visit_info.date}:{visit_info.origin}:referers_count',
                visit_info.referer)

    def _recalculate_clients_info(self, visit_info: VisitInfo):
        self.redis.sadd(
            f'{visit_info.date}:{visit_info.origin}:clients:{visit_info.path}',
            visit_info.client_id)
        self.redis.sadd(f'{visit_info.date}:{visit_info.origin}:clients',
                        visit_info.client_id)

    def _recalculate_visits_info(self, visit_info: VisitInfo):
        self.redis.hincrby('visits', visit_info.origin)
        self.redis.hincrby(
            f'{visit_info.date}:{visit_info.origin}:paths_visits',
            visit_info.path)  #
        self.redis.hincrby(f'{visit_info.date}:visits', visit_info.origin)
        if visit_info.browser:
            self.redis.hincrby(
                f'{visit_info.date}:{visit_info.origin}:browsers',
                visit_info.browser)
        if visit_info.language:
            self.redis.hincrby(
                f'{visit_info.date}:{visit_info.origin}:languages',
                visit_info.language)
        if visit_info.platform:
            self.redis.hincrby(
                f'{visit_info.date}:{visit_info.origin}:platforms',
                visit_info.platform)

    def _recalculate_deep(self, visit_info: VisitInfo):
        last_session = self.redis.hget(
            f'{visit_info.date}:{visit_info.origin}:clients_session',
            visit_info.client_id)
        if last_session and time.time() - float(
                last_session.decode()) > SESSION_TIMEOUT:
            self.redis.delete(
                f'{visit_info.date}:{visit_info.origin}:'
                f'{visit_info.client_id}')
        deep_before = len(self.redis.sscan(
            f'{visit_info.date}:{visit_info.origin}:{visit_info.client_id}')[
                              1])
        self.redis.sadd(
            f'{visit_info.date}:{visit_info.origin}:{visit_info.client_id}',
            visit_info.path)
        deep = len(self.redis.sscan(
            f'{visit_info.date}:{visit_info.origin}:{visit_info.client_id}')[
                       1])
        if deep > deep_before:
            self.redis.hincrby(
                f'{visit_info.date}:{visit_info.origin}:count_deep_visit',
                deep)
            if deep_before > 0:
                self.redis.hincrby(
                    f'{visit_info.date}:{visit_info.origin}:count_deep_visit',
                    deep_before, -1)
        self.redis.hset(
            f'{visit_info.date}:{visit_info.origin}:clients_session',
            visit_info.client_id, time.time())

    def get_all_clients(self, origin, date):
        return [i.decode() for i in
                self.redis.sscan(f'{date}:{origin}:clients')[1]]

    def get_all_paths(self, origin, date):
        return [i.decode() for i in
                self.redis.sscan(f'{date}:{origin}:paths')[1]]

    def get_browser_stats(self, origin, date):
        return dict((browser.decode(), count.decode()) for browser, count in
                    self.redis.hscan(f'{date}:{origin}:browsers')[1].items())

    def get_language_stats(self, origin, date):
        return dict((lang.decode(), count.decode()) for lang, count in
                    self.redis.hscan(f'{date}:{origin}:languages')[1].items())

    def get_platforms_stats(self, origin, date):
        return dict((platform.decode(), count.decode()) for platform, count in
                    self.redis.hscan(f'{date}:{origin}:platforms')[1].items())

    def get_all_origins(self):
        return [i.decode() for i in self.redis.hscan('visits')[1]]

    def get_total_visits(self, origin, date):
        visits = self.redis.hget(f'{date}:visits', origin)
        return 0 if visits is None else visits.decode()

    def get_average_deep_of_visits(self, origin, date):
        sum = 0
        count = 0
        data = self.redis.hscan(f'{date}:{origin}:count_deep_visit')[1]
        for i in data:
            number = int(i.decode())
            if number > 0:
                c = int(data[i].decode())
                sum += number * c
                count += c
        if count == 0:
            return 0
        return sum / count

    def get_origin_statistics_at_date(self, origin, date):
        clients = self.get_all_clients(origin, date)
        paths = self.get_all_paths(origin, date)
        paths_stats = {}
        total_referer_stats = {}
        for path in paths:
            referers = [i.decode() for i in
                        self.redis.sscan(f'{date}:{origin}:referer:{path}')[1]]
            referer_stats = {}
            for ref in referers:
                referer_stats[ref] = self.redis.hget(
                    f'{date}:{origin}:referers_count', ref)
                if referer_stats[ref] is not None:
                    referer_stats[ref] = referer_stats[ref].decode()
            visits = self.redis.hget(f'{date}:{origin}:paths_visits', path)
            if visits is not None:
                visits = visits.decode()
            paths_stats[path] = {'unic_visits': len(
                self.redis.sscan(f'{date}:{origin}:clients:{path}')[1]),
                                 'visits': visits,
                                 'refer': referer_stats}
            total_referer_stats.update(referer_stats)
        return {
            "total_clients": len(clients),
            "total_visits": self.get_total_visits(origin, date),
            "paths_stats": paths_stats,
            'total_refer_stats': total_referer_stats,
            'average_visits_deep': self.get_average_deep_of_visits(origin,
                                                                   date),
            'browsers_stats': self.get_browser_stats(origin, date),
            'platform_stats': self.get_platforms_stats(origin, date),
            'language_stats': self.get_language_stats(origin, date)
        }
