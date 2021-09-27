import sqlite3
import redis


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


class RedisStorage(BaseStorage):
    def __init__(self, config):
        self.redis = redis.Redis(**config)

    def origin_exists(self, origin):
        return self.redis.exists(origin)

    def get_origin(self, origin):
        return self.redis.get(origin)

    def increment_total_visits(self, origin):
        return self.redis.incr(origin)

    def add_origin(self, origin):
        self.redis.set(origin, 0)

    def set_total_visits(self, origin, count):
        self.redis.set(origin, count)


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


class SQLStorage(BaseStorage):
    def __init__(self, database):
        self.database_name = database
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Connect to database and set cursor"""
        self.connection = sqlite3.connect(self.database_name)
        self.cursor = self.connection.cursor()

    def origin_exists(self, origin):
        """Check is origin exits"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `counts` WHERE `origin` = ?', (origin,)).fetchall()
            return bool(len(result))

    def get_origin(self, origin):
        """Get origin counts"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `counts` WHERE `origin` = ?', (origin,)).fetchall()
            return result[0]

    def add_origin(self, origin):
        """Add new origin"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `counts` (`origin`) VALUES(?)", (origin,))

    def update_total_visits(self, origin, count):
        """Update total visits"""
        self.connect()
        with self.connection:
            return self.cursor.execute("UPDATE `counts` SET `count` = ? WHERE `origin` = ?", (count, origin))

    def close(self):
        """Close connections to database"""
        if self.connection:
            self.connection.close()
