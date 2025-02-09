import os

def setup_cache():
    cache_dir = os.path.join("/Users/will/Library/Caches/fastf1")
    print(f"FastF1 cache directory: {cache_dir}")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir 