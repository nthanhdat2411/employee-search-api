import time
import threading
from collections import defaultdict, deque
from typing import Dict, Deque, Tuple
import hashlib

class RateLimiter:
    """
    Custom rate limiter implementation without external dependencies.
    Uses sliding window algorithm for accurate rate limiting.
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
        self.lock = threading.Lock()
    
    def _get_client_key(self, client_id: str) -> str:
        """Generate a unique key for the client"""
        return hashlib.md5(client_id.encode()).hexdigest()
    
    def _clean_old_requests(self, client_key: str, current_time: float):
        """Remove requests older than the window"""
        if client_key in self.requests:
            while self.requests[client_key] and self.requests[client_key][0] < current_time - self.window_seconds:
                self.requests[client_key].popleft()
    
    def is_allowed(self, client_id: str) -> Tuple[bool, Dict]:
        """
        Check if the request is allowed for the given client.
        Returns (is_allowed, rate_limit_info)
        """
        current_time = time.time()
        client_key = self._get_client_key(client_id)
        
        with self.lock:
            self._clean_old_requests(client_key, current_time)
            
            # Check if we're under the limit
            if len(self.requests[client_key]) < self.max_requests:
                self.requests[client_key].append(current_time)
                return True, {
                    "remaining": self.max_requests - len(self.requests[client_key]),
                    "reset_time": current_time + self.window_seconds,
                    "limit": self.max_requests
                }
            else:
                return False, {
                    "remaining": 0,
                    "reset_time": self.requests[client_key][0] + self.window_seconds,
                    "limit": self.max_requests
                }
    
    def get_rate_limit_info(self, client_id: str) -> Dict:
        """Get current rate limit information for a client"""
        current_time = time.time()
        client_key = self._get_client_key(client_id)
        
        with self.lock:
            self._clean_old_requests(client_key, current_time)
            
            return {
                "remaining": max(0, self.max_requests - len(self.requests[client_key])),
                "reset_time": current_time + self.window_seconds if self.requests[client_key] else current_time,
                "limit": self.max_requests
            }

# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=100, window_seconds=60) 