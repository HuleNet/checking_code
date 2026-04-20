from os import environ

from pytest import fixture

from checking_service.infrastructure.core import get_settings_cached


environ["APP_ENV"] = "test"


@fixture(autouse=True)
def test_settings():
    get_settings_cached.cache_clear()
    return get_settings_cached()
