# Copyright 2026 Terradue
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio

import httpx

from stac_transaction_api_client import AuthenticatedClient, Client


def test_client_constructs_httpx_client_with_configuration() -> None:
    timeout = httpx.Timeout(4.0)
    client = Client(
        base_url="https://stac.example.test/api",
        headers={"X-Request-ID": "request-1"},
        cookies={"session": "cookie-1"},
        timeout=timeout,
        follow_redirects=True,
    )

    http_client = client.get_httpx_client()

    assert str(http_client.base_url) == "https://stac.example.test/api/"
    assert http_client.headers["X-Request-ID"] == "request-1"
    assert http_client.cookies["session"] == "cookie-1"
    assert http_client.timeout == timeout
    assert http_client.follow_redirects is True
    assert client.get_httpx_client() is http_client
    http_client.close()


def test_authenticated_client_sets_configurable_authorization_header() -> None:
    client = AuthenticatedClient(
        base_url="https://stac.example.test",
        token="secret",
        prefix="Token",
        auth_header_name="X-Authorization",
    )

    http_client = client.get_httpx_client()

    assert http_client.headers["X-Authorization"] == "Token secret"
    assert "Authorization" not in client._headers
    http_client.close()


def test_authenticated_client_supports_token_without_prefix() -> None:
    client = AuthenticatedClient(
        base_url="https://stac.example.test", token="secret", prefix=""
    )

    http_client = client.get_httpx_client()

    assert http_client.headers["Authorization"] == "secret"
    http_client.close()


def test_client_modifiers_return_independent_configuration() -> None:
    original = Client(base_url="https://stac.example.test")

    modified = original.with_headers({"X-Test": "yes"}).with_cookies({"key": "value"})

    assert modified is not original
    assert modified._headers == {"X-Test": "yes"}
    assert modified._cookies == {"key": "value"}
    assert original._headers == {}
    assert original._cookies == {}


def test_async_client_uses_bearer_authentication() -> None:
    async def run() -> None:
        client = AuthenticatedClient(
            base_url="https://stac.example.test", token="secret"
        )

        http_client = client.get_async_httpx_client()

        assert http_client.headers["Authorization"] == "Bearer secret"
        assert client.get_async_httpx_client() is http_client
        await http_client.aclose()

    asyncio.run(run())
