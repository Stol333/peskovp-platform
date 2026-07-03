from rate_limiter import InMemoryRateLimiter


def test_rate_limiter_blocks_after_limit() -> None:
    limiter = InMemoryRateLimiter(max_requests=2, window_seconds=60)
    assert limiter.allow("u-1")[0] is True
    assert limiter.allow("u-1")[0] is True
    allowed, retry = limiter.allow("u-1")
    assert allowed is False
    assert retry >= 1
