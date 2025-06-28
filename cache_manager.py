import os
import json
import hashlib
import threading

class CacheManager:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        self.memory_cache = {}
        self.lock = threading.Lock()
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _get_cache_path(self, query, site):
        key = hashlib.md5(f'{site}:{query}'.encode('utf-8')).hexdigest()
        return os.path.join(self.cache_dir, f'{site}_{key}.json')

    def get_cached_results(self, query, site):
        key = (site, query)
        with self.lock:
            if key in self.memory_cache:
                return self.memory_cache[key]
        path = self._get_cache_path(query, site)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                with self.lock:
                    self.memory_cache[key] = results
                return results
            except Exception:
                return None
        return None

    def cache_results(self, query, site, results):
        key = (site, query)
        with self.lock:
            self.memory_cache[key] = results
        path = self._get_cache_path(query, site)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(results, f)
        except Exception:
            pass 