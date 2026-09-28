"""Regression checks for worker concurrency and lifecycle edge cases."""

from concurrent.futures import ThreadPoolExecutor
import signal

from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest


def test_rate_limit_is_atomic_across_workers(fake_redis):
    from app.rate_limiter import RateLimiter

    def request(_):
        try:
            RateLimiter(fake_redis, 5).check("concurrent", now=1000.0)
            return 200
        except HTTPException as exc:
            return exc.status_code

    with ThreadPoolExecutor(max_workers=12) as workers:
        statuses = list(workers.map(request, range(30)))
    assert statuses.count(200) == 5
    assert statuses.count(429) == 25
    assert fake_redis.zcard("ratelimit:concurrent") == 5
    assert fake_redis.ttl("ratelimit:concurrent") > 0


def test_exact_budget_is_exhausted(fake_redis):
    from app.cost_guard import CostGuard

    guard = CostGuard(fake_redis, 1.0)
    guard.record("u1", 1.0)
    with pytest.raises(HTTPException) as exc:
        guard.check("u1")
    assert exc.value.status_code == 402


def test_install_twice_does_not_recurse():
    from app.lifecycle import Lifecycle

    life = Lifecycle()
    original = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}
    called = []
    try:
        signal.signal(signal.SIGTERM, lambda sig, frame: called.append(sig))
        life.install()
        life.install()
        life.request_shutdown(signal.SIGTERM, None)
        assert called == [signal.SIGTERM]
        life.uninstall()
        assert signal.getsignal(signal.SIGTERM) != life.request_shutdown
    finally:
        for sig, handler in original.items():
            signal.signal(sig, handler)


def test_lifespan_fails_before_serving_when_secret_missing(monkeypatch):
    from app import main
    from app.config import Settings
    from pydantic import ValidationError

    monkeypatch.delenv("AGENT_API_KEY", raising=False)
    monkeypatch.setattr(main, "get_settings", lambda: Settings(_env_file=None))
    with pytest.raises(ValidationError):
        with TestClient(main.app):
            pass


def test_shutdown_rejects_new_ask_before_llm(client, auth_headers, monkeypatch):
    from app import main

    def forbidden(*args, **kwargs):
        pytest.fail("LLM must not be called during shutdown")

    monkeypatch.setattr(main, "ask_llm", forbidden)
    main.lifecycle.shutting_down = True
    assert client.post("/ask", json={"question": "hello"}, headers=auth_headers).status_code == 503
