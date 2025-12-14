import time
from threading import Lock
from loguru import logger
from collections import defaultdict

class PerSessionRateLimiter:
    """Rate limiter per session (better for multi-user scenarios)"""
    
    def __init__(self, calls_per_minute: int = 15, calls_per_second: int = 2):
        self.calls_per_minute = calls_per_minute
        self.calls_per_second = calls_per_second
        
        self.minute_interval = 60.0 / calls_per_minute
        self.second_interval = 1.0 / calls_per_second
        
        # Track per session
        self.session_data = defaultdict(lambda: {
            'last_call': 0,
            'call_times': []
        })
        self.lock = Lock()
    
    def wait_if_needed(self, session_id: str = "default"):
        """Wait if necessary to respect rate limits for this session"""
        with self.lock:
            data = self.session_data[session_id]
            now = time.time()
            
            # Remove calls older than 1 minute
            data['call_times'] = [t for t in data['call_times'] if now - t < 60]
            
            # Check per-minute limit
            if len(data['call_times']) >= self.calls_per_minute:
                wait_time = 60 - (now - data['call_times'][0])
                if wait_time > 0:
                    logger.warning(f"⏳ Session {session_id[:8]}...: waiting {wait_time:.2f}s (minute limit)")
                    time.sleep(wait_time)
                    now = time.time()
                    data['call_times'] = []
            
            # Check per-second limit
            time_since_last = now - data['last_call']
            if time_since_last < self.second_interval:
                wait_time = self.second_interval - time_since_last
                logger.debug(f"⏳ Session {session_id[:8]}...: waiting {wait_time:.2f}s (second limit)")
                time.sleep(wait_time)
                now = time.time()
            
            # Record this call
            data['last_call'] = now
            data['call_times'].append(now)

# Global rate limiter with per-session tracking
gemini_rate_limiter = PerSessionRateLimiter(
    calls_per_minute=15,
    calls_per_second=2
)