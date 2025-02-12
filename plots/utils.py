import os


def setup_cache():
    if os.environ.get('ENV') == 'heroku':
        # Use tmp directory for Heroku
        cache_dir = '/tmp/f1-cache'
    else:
        # Use default directory for local development
        cache_dir = os.path.expanduser('~/Library/Caches/fastf1')

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return cache_dir
