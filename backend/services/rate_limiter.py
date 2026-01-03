from datetime import datetime, timedelta
from typing import Dict
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list[datetime]] = defaultdict(list)
    
    def is_allowed(self, key: str, max_requests: int, window_minutes: int = 60) -> bool:
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        if len(self.requests[key]) >= max_requests:
            return False
        
        self.requests[key].append(now)
        return True
    
    def cleanup_old_entries(self):
        now = datetime.utcnow()
        cutoff = now - timedelta(hours=2)
        
        keys_to_delete = []
        for key, timestamps in self.requests.items():
            self.requests[key] = [t for t in timestamps if t > cutoff]
            if not self.requests[key]:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self.requests[key]

rate_limiter = RateLimiter()
