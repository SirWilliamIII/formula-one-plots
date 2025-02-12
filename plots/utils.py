import os


def setup_cache():
    cache_dir = os.getenv('FASTF1_CACHE_DIR', '/cache/fastf1')
    print(f"FastF1 cache directory: {cache_dir}")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir
