import pytest
import os

@pytest.fixture(autouse=True)
def setup_test_env():
    os.environ['TOTP_SECRET_KEY'] = 'test_secret_key'
    yield
    if 'TOTP_SECRET_KEY' in os.environ:
        del os.environ['TOTP_SECRET_KEY']
