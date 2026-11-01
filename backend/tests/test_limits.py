from types import SimpleNamespace

from app.limits import DailyLimiter, client_ip


class FakeClock:
    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now


def test_visitor_limit():
    limiter = DailyLimiter(per_visitor=2, total=0, clock=FakeClock())
    assert limiter.check("a") is None
    assert limiter.check("a") is None
    assert limiter.check("a") == "visitor"
    assert limiter.check("b") is None  # another visitor is not affected


def test_total_limit():
    limiter = DailyLimiter(per_visitor=0, total=3, clock=FakeClock())
    assert [limiter.check(v) for v in ("a", "b", "c")] == [None, None, None]
    assert limiter.check("d") == "total"


def test_resets_next_day():
    clock = FakeClock()
    limiter = DailyLimiter(per_visitor=1, total=1, clock=clock)
    assert limiter.check("a") is None
    assert limiter.check("a") == "total"
    clock.now = 86400  # one day later
    assert limiter.check("a") is None


def test_zero_means_unlimited():
    limiter = DailyLimiter(per_visitor=0, total=0, clock=FakeClock())
    assert all(limiter.check("a") is None for _ in range(1000))


def test_client_ip_uses_last_forwarded_entry():
    request = SimpleNamespace(headers={"x-forwarded-for": "1.1.1.1, 2.2.2.2"},
                              client=SimpleNamespace(host="9.9.9.9"))
    assert client_ip(request) == "2.2.2.2"


def test_client_ip_falls_back_to_direct_address():
    request = SimpleNamespace(headers={}, client=SimpleNamespace(host="9.9.9.9"))
    assert client_ip(request) == "9.9.9.9"