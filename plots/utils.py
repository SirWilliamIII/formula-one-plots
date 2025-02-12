import os
import redis
from urllib.parse import urlparse
import gc
import matplotlib.pyplot as plt
import fastf1 as ff1

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
    # Always return a file path for FastF1
    if os.environ.get('ENV') == 'heroku':
        cache_dir = '/tmp/f1-cache'
    else:
        cache_dir = os.path.expanduser('~/Library/Caches/fastf1')

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return cache_dir

def cleanup_memory():
    plt.close('all')
    gc.collect()

def get_plot_cache():
    try:
        # Return Redis for plot caching if available
        if os.environ.get('ENV') == 'heroku':
            return get_redis()
        return None
    finally:
        cleanup_memory()
