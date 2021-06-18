from urllib.request import urlopen

import pytest


@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("localhost", 8888)


def test_hello(httpserver):
    body = "Hello, World!"
    endpoint = "/hello"
    httpserver.expect_request(endpoint).respond_with_data(body)
    with urlopen(httpserver.url_for(endpoint)) as response:
        result = response.read().decode()
    assert body == result
