import time
import asyncio
from collections import deque

class RateLimiter:
    """
    Implements a simple token bucket rate limiting mechanism.
    """
    def __init__(self, rate_limit: int, interval: int):
        """
        Args:
            rate_limit: Maximum number of calls allowed within the interval.
            interval: Time window in seconds.
        """
        self.rate_limit = rate_limit
        self.interval = interval
        self.timestamps = deque()

    def __call__(self, func):
        """
        Decorator to apply rate limiting to a function.
        """
        def wrapper(*args, **kwargs):
            self.wait_for_permission()
            return func(*args, **kwargs)
        return wrapper

    async def wait_for_permission(self):
        """
        Blocks until a call is permitted by the rate limit.
        """
        while True:
            now = time.time()
            # Remove timestamps older than the interval
            while self.timestamps and self.timestamps[0] <= now - self.interval:
                self.timestamps.popleft()

            if len(self.timestamps) < self.rate_limit:
                self.timestamps.append(now)
                break
            else:
                # Calculate time to wait until the oldest call expires
                time_to_wait = self.timestamps[0] - (now - self.interval)
                await asyncio.sleep(time_to_wait + 0.01) # Add a small buffer
