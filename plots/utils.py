import os
import redis
from urllib.parse import urlparse
import gc
import matplotlib.pyplot as plt
import fastf1 as ff1
from pathlib import Path

def get_redis():
    # Get Redis URL from Heroku config - try both possible environment variables
    redis_url = os.getenv('REDISCLOUD_URL') or os.getenv('REDIS_URL')
    if redis_url:
        try:
            url = urlparse(redis_url)
            return redis.Redis(
                host=url.hostname, 
                port=url.port, 
                password=url.password,
                ssl=True,
                ssl_cert_reqs=None,
                decode_responses=True,  # Add this to handle string encoding
                socket_timeout=5,  # Add timeout
                retry_on_timeout=True  # Add retry logic
            )
        except Exception as e:
            print(f"Redis connection error: {str(e)}")
            return None
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
    
    # Clear FastF1 cache if it's too large
    cache_dir = setup_cache()
    try:
        import shutil
        cache_size = sum(f.stat().st_size for f in Path(cache_dir).glob('**/*') if f.is_file()) / (1024 * 1024)
        if cache_size > 400:  # If cache is over 400MB
            shutil.rmtree(cache_dir)
            os.makedirs(cache_dir)
    except Exception as e:
        print(f"Error cleaning cache: {str(e)}")

def get_plot_cache():
    try:
        # Return Redis for plot caching if available
        if os.environ.get('ENV') == 'heroku':
            redis_client = get_redis()
            if redis_client:
                try:
                    redis_client.ping()  # Test connection
                    return redis_client
                except:
                    print("Redis ping failed, falling back to file cache")
                    return None
        return None
    finally:
        cleanup_memory()
