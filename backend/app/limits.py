import threading
import time
from collections import defaultdict

SECONDS_PER_DAY = 86400


class DailyLimiter:
    """Counts requests per visitor and in total, and starts again every day (UTC).

    A limit of 0 means "no limit".
    """

    def __init__(self, per_visitor=0, total=0, clock=time.time):
        self.per_visitor = per_visitor
        self.total = total
        self.clock = clock
        self.lock = threading.Lock()
        self.day = self._today()
        self.counts = defaultdict(int)
        self.total_count = 0

    def _today(self):
        return int(self.clock() // SECONDS_PER_DAY)

    def _reset_if_new_day(self):
        today = self._today()
        if today != self.day:
            self.day = today
            self.counts.clear()
            self.total_count = 0

    def check(self, visitor):
        """Return None if the request is allowed (and count it), else "total" or "visitor"."""
        with self.lock:
            self._reset_if_new_day()
            if self.total and self.total_count >= self.total:
                return "total"
            if self.per_visitor and self.counts[visitor] >= self.per_visitor:
                return "visitor"
            self.counts[visitor] += 1
            self.total_count += 1
            return None


def client_ip(request):
    """Visitor address. Behind a proxy, use the last X-Forwarded-For entry (added by the proxy)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"