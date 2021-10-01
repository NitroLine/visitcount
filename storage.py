import redis
import time
from .config import SESSION_TIMEOUT


class BaseStorage:
    def origin_exists(self, origin):
        """Check is origin exits"""
        pass

    def get_origin(self, origin):
        """Get origin counts"""
        pass

    def add_origin(self, origin):
        """Add new origin"""
        pass

    def set_total_visits(self, origin, count):
        """Update total visits"""
        pass

    def increment_total_visits(self, origin):
        """Increment total visits"""
        pass


class VisitInfo:
    def __init__(self, origin, client_id, path, referer, browser, language, platform):
        self.origin = origin
        self.client_id = client_id
        self.path = path
        self.referer = referer
        self.browser = browser
        self.language = language
        self.platform = platform


class RedisStorage:
    def __init__(self, config):
        self.redis = redis.Redis(**config)

    def add_information(self, visit_info: VisitInfo):
        self.redis.sadd(f'{visit_info.origin}:clients:{visit_info.path}', visit_info.client_id) #
        self.redis.sadd(f'{visit_info.origin}:clients', visit_info.client_id) #
        self.redis.sadd(f'{visit_info.origin}:paths', visit_info.path) #
        self.redis.hincrby('visits', visit_info.origin) #
        self.redis.hincrby(f'{visit_info.origin}:paths_visits', visit_info.path) #
        if visit_info.browser:
            self.redis.hincrby(f'{visit_info.origin}:browsers', visit_info.browser)
        if visit_info.language:
            self.redis.hincrby(f'{visit_info.origin}:languages', visit_info.language)
        if visit_info.platform:
            self.redis.hincrby(f'{visit_info.origin}:platforms', visit_info.platform)
        if len(visit_info.referer) > 0:
            self.redis.sadd(f'{visit_info.origin}:referer:{visit_info.path}', visit_info.referer)
            self.redis.hincrby(f'{visit_info.origin}:referers_count', visit_info.referer)
        last_session = self.redis.hget(f'{visit_info.origin}:clients_session', visit_info.client_id)
        if last_session and time.time() - float(last_session.decode()) > SESSION_TIMEOUT:
            deep = len(self.redis.sscan(f'{visit_info.origin}:{visit_info.client_id}')[1])
            self.redis.hincrby(f'{visit_info.origin}:count_deep_visit', deep)
            self.redis.delete(f'{visit_info.origin}:{visit_info.client_id}')
            self.redis.sadd(f'{visit_info.origin}:{visit_info.client_id}', visit_info.path)
        self.redis.hset(f'{visit_info.origin}:clients_session', visit_info.client_id, time.time())

    def get_all_clients(self, origin):
        return [i.decode() for i in self.redis.sscan(f'{origin}:clients')[1]]

    def get_all_paths(self, origin):
        return [i.decode() for i in self.redis.sscan(f'{origin}:paths')[1]]

    def get_browser_stats(self, origin):
        return dict((browser.decode(), count.decode()) for browser, count in self.redis.hscan(f'{origin}:browsers')[1].items())

    def get_language_stats(self, origin):
        return dict((lang.decode(), count.decode()) for lang, count in self.redis.hscan(f'{origin}:languages')[1].items())

    def get_platforms_stats(self, origin):
        return dict((platform.decode(), count.decode()) for platform, count in self.redis.hscan(f'{origin}:platforms')[1].items())

    def get_all_origins(self):
        return [i.decode() for i in self.redis.hscan('visits')[1]]

    def get_total_visits(self, origin):
        visits = self.redis.hget('visits', origin)
        return 0 if visits is None else visits.decode()

    def get_average_deep_of_visits(self, origin):
        sum = 0
        count = 0
        data = self.redis.hscan(f'{origin}:count_deep_visit')[1]
        print(data)
        for i in data:
            c = int(data[i].decode())
            sum += int(i.decode()) * c
            count += c
        if count == 0:
            return 0
        return sum / count

    def get_origin_statistics(self, origin):
        clients = self.get_all_clients(origin)
        paths = self.get_all_paths(origin)
        paths_stats = {}
        total_referer_stats = {}
        for path in paths:
            referers = [i.decode() for i in self.redis.sscan(f'{origin}:referer:{path}')[1]]
            referer_stats = {}
            for ref in referers:
                referer_stats[ref] = self.redis.hget(f'{origin}:referers_count', ref)
                if referer_stats[ref] is not None:
                    referer_stats[ref] = referer_stats[ref].decode()
            visits = self.redis.hget(f'{origin}:paths_visits', path)
            if visits is not None:
                visits = visits.decode()
            paths_stats[path] = { 'unic_visits': len(self.redis.sscan(f'{origin}:clients:{path}')[1]),
                                  'visits': visits,
                                  'refer' : referer_stats}
            total_referer_stats.update(referer_stats)
        return {
            "total_clients": len(clients),
            "total_visits": self.get_total_visits(origin),
            "paths_stats":paths_stats,
            'total_refer_stats': total_referer_stats,
            'average_visits_deep': self.get_average_deep_of_visits(origin),
            'browsers_stats':self.get_browser_stats(origin),
            'platform_stats':self.get_platforms_stats(origin),
            'language_stats':self.get_language_stats(origin)
        }


class DictStorage:
    def __init__(self, config):
        self.storage = dict()

    def origin_exists(self, origin):
        return origin in self.storage

    def get_origin(self, origin):
        return self.storage.get(origin)

    def increment_total_visits(self, origin):
        if origin not in self.storage:
            self.storage[origin] = 0
        self.storage[origin] += 1
        return self.storage[origin]

    def add_origin(self, origin):
        self.storage[origin] = 0

    def set_total_visits(self, origin, count):
        self.storage[origin] = count
