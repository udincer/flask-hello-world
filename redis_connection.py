import os
import logging

import redis


class RedisConnectionException(Exception):
    pass

class RedisConnection:
    def __init__(self) -> None:
        REDIS_URL = os.getenv("REDIS_URL")
        if len(REDIS_URL) > 0:
            self._r = redis.from_url(REDIS_URL)
        else:
            logging.error("REDIS_URL environment variable not set")
            self._r = None

    @property
    def r(self):
        if self._r is not None:
            return self._r
        else:
            raise RedisConnectionException()

    def is_available(self):
        try:
            ping_res = self.r.ping()
            print(ping_res)
            if ping_res:
                return True
            else:
                return False
        except Exception as e:
            logging.debug(e)
            return False

    def add_sid(self, sid):
        return self.r.sadd("sids", sid)

    def check_sid(self, sid):
        return bool(self.r.sismember("sids", sid))
