import os
import redis
from urllib.parse import urlparse

def get_redis():
    # Get Redis URL from Heroku config - try both possible environment variables
    redis_url = os.getenv('REDISCLOUD_URL') or os.getenv('REDIS_URL')
    if redis_url:
        url = urlparse(redis_url)
        return redis.Redis(host=url.hostname, 
                         port=url.port, 
                         password=url.password,
                         ssl=True,
                         ssl_cert_reqs=None)
    return None

def setup_cache():
    if os.environ.get('ENV') == 'heroku':
        # Try to use Redis first
        redis_client = get_redis()
        if redis_client:
            return redis_client
        
        # Fallback to tmp directory if Redis isn't available
        cache_dir = '/tmp/f1-cache'
    else:
        # Use default directory for local development
        cache_dir = os.path.expanduser('~/Library/Caches/fastf1')

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return cache_dir
