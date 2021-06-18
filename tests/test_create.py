import requests


def test_hello(httpserver):
    """ Test Hello """
    httpserver.expect_request("/hello").respond_with_json({"hello": "world"})

    assert requests.get(httpserver.url_for("/hello")).json() == {"hello": "world"}
