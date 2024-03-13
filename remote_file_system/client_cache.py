class Cache:
    def __init__(self, cache_location: str, freshness_interval_in_seconds: int):
        self.cache_location: str = cache_location
        self.freshness_interval_in_seconds: int = freshness_interval_in_seconds

    def is_in_cache(self, file_name: str) -> bool:
        pass

    def put_in_cache(self, file_name: str, content: str) -> None:
        pass

    def get_from_cache(self, file_name: str) -> bytes:
        pass

    def get_file_metadata(self, file_path: str):
        pass
