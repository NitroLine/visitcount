# Visitcount
Python adaptive visit counter based on Flask

## Before run
 - Redis database required. Can be installed from a folder `redis` using docker compose.
    - Set redis password in `.env` file. `REDIS_PASS=redispass`
    - Run with docker-compose using command `docker-compose -f redis-compose.yml up` 

 - Set database configuration in  `config.py` to `DATABASE_PARAMS`
 - Install python 3 requirements by `pip3 install -r requirements.txt`






