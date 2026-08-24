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
from collections.abc import Callable
from typing import Any

import httpx
import pytest
from pydantic import ValidationError
from pystac import Item, ItemCollection

from stac_transaction_api_client import Client, errors
from stac_transaction_api_client.api.transaction import (
    delete_feature,
    get_feature,
    patch_feature,
    post_feature,
    update_feature,
)
from stac_transaction_api_client.models import Exception as ApiException


def _response(status_code: int, json: dict[str, Any] | None = None) -> httpx.Response:
    request = httpx.Request("GET", "https://stac.example.test/resource")
    if json is None:
        return httpx.Response(status_code, request=request)
    return httpx.Response(status_code, json=json, request=request)


def test_get_request_matches_contract_path_and_escapes_parameters() -> None:
    kwargs = get_feature._get_kwargs("collection/with space", "item?one")

    assert kwargs == {
        "method": "get",
        "url": "/collections/collection%2Fwith%20space/items/item%3Fone",
    }


def test_post_serializes_single_item(item: Item) -> None:
    kwargs = post_feature._get_kwargs("collection/one", body=item)

    assert kwargs["method"] == "post"
    assert kwargs["url"] == "/collections/collection%2Fone/items"
    assert kwargs["headers"] == {"Content-Type": "application/json"}
    assert kwargs["json"]["type"] == "Feature"
    assert kwargs["json"]["id"] == item.id


def test_post_serializes_empty_item_collection() -> None:
    """The contract permits a FeatureCollection with an empty features array."""
    kwargs = post_feature._get_kwargs("collection", body=ItemCollection([]))

    assert kwargs["json"] == {"type": "FeatureCollection", "features": []}
    assert kwargs["headers"] == {"Content-Type": "application/json"}


def test_post_without_body_does_not_claim_json_content() -> None:
    kwargs = post_feature._get_kwargs("collection")

    assert "json" not in kwargs
    assert kwargs["headers"] == {}


def test_put_requires_if_match_and_serializes_complete_item(item: Item) -> None:
    kwargs = update_feature._get_kwargs(
        "collection", "item", body=item, if_match='"revision-1"'
    )

    assert kwargs["method"] == "put"
    assert kwargs["headers"] == {
        "If-Match": '"revision-1"',
        "Content-Type": "application/json",
    }
    assert kwargs["json"]["id"] == item.id


def test_patch_accepts_partial_object_and_optional_if_match() -> None:
    patch = {"properties": {"quality": "updated"}}

    without_etag = patch_feature._get_kwargs("collection", "item", body=patch)
    with_etag = patch_feature._get_kwargs(
        "collection", "item", body=patch, if_match='"revision-1"'
    )

    assert without_etag["method"] == "patch"
    assert without_etag["json"] == patch
    assert without_etag["headers"] == {"Content-Type": "application/json"}
    assert with_etag["headers"]["If-Match"] == '"revision-1"'


def test_delete_requires_if_match() -> None:
    kwargs = delete_feature._get_kwargs("collection", "item", if_match='"revision-1"')

    assert kwargs == {
        "method": "delete",
        "url": "/collections/collection/items/item",
        "headers": {"If-Match": '"revision-1"'},
    }


def test_get_parses_item_response(item_dict: dict[str, Any]) -> None:
    parsed = get_feature._parse_response(
        client=Client(base_url="https://stac.example.test"),
        response=_response(200, item_dict),
    )

    assert isinstance(parsed, Item)
    assert parsed.id == item_dict["id"]


def test_get_honors_raise_on_unexpected_status() -> None:
    response = _response(404)
    permissive = Client(base_url="https://stac.example.test")
    strict = Client(
        base_url="https://stac.example.test", raise_on_unexpected_status=True
    )

    assert get_feature._parse_response(client=permissive, response=response) is None
    with pytest.raises(errors.UnexpectedStatus) as raised:
        get_feature._parse_response(client=strict, response=response)
    assert raised.value.status_code == 404


@pytest.mark.parametrize(
    ("parser", "status_code"),
    [
        (post_feature._parse_response, 201),
        (update_feature._parse_response, 200),
        (patch_feature._parse_response, 200),
    ],
)
def test_mutations_parse_item_responses(
    parser: Callable[..., Any], status_code: int, item_dict: dict[str, Any]
) -> None:
    parsed = parser(
        client=Client(base_url="https://stac.example.test"),
        response=_response(status_code, item_dict),
    )

    assert isinstance(parsed, Item)
    assert parsed.id == item_dict["id"]


@pytest.mark.parametrize(
    ("parser", "status_code"),
    [
        (post_feature._parse_response, 202),
        (post_feature._parse_response, 404),
        (update_feature._parse_response, 202),
        (update_feature._parse_response, 204),
        (update_feature._parse_response, 404),
        (patch_feature._parse_response, 202),
        (patch_feature._parse_response, 204),
        (patch_feature._parse_response, 404),
        (delete_feature._parse_response, 200),
        (delete_feature._parse_response, 202),
        (delete_feature._parse_response, 204),
        (delete_feature._parse_response, 404),
    ],
)
def test_documented_bodyless_responses_parse_as_none(
    parser: Callable[..., Any], status_code: int
) -> None:
    assert (
        parser(
            client=Client(base_url="https://stac.example.test"),
            response=_response(status_code),
        )
        is None
    )


@pytest.mark.parametrize(
    ("parser", "status_code"),
    [
        (post_feature._parse_response, 400),
        (post_feature._parse_response, 500),
        (post_feature._parse_response, 418),
        (update_feature._parse_response, 400),
        (update_feature._parse_response, 412),
        (update_feature._parse_response, 500),
        (update_feature._parse_response, 418),
        (patch_feature._parse_response, 400),
        (patch_feature._parse_response, 500),
        (patch_feature._parse_response, 418),
        (delete_feature._parse_response, 400),
        (delete_feature._parse_response, 500),
        (delete_feature._parse_response, 418),
    ],
)
def test_documented_error_responses_parse_exception_schema(
    parser: Callable[..., Any], status_code: int
) -> None:
    parsed = parser(
        client=Client(base_url="https://stac.example.test"),
        response=_response(
            status_code, {"code": "transaction-error", "description": "failed"}
        ),
    )

    assert parsed == ApiException(code="transaction-error", description="failed")


def test_error_response_requires_contract_code() -> None:
    with pytest.raises(ValidationError):
        post_feature._parse_response(
            client=Client(base_url="https://stac.example.test"),
            response=_response(400, {"description": "missing code"}),
        )


def test_sync_detailed_sends_contract_request(item: Item) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.raw_path == b"/collections/a%2Fb/items"
        assert request.headers["Content-Type"] == "application/json"
        assert request.headers["X-Test"] == "present"
        return httpx.Response(202, request=request)

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(
        base_url="https://stac.example.test",
        headers={"X-Test": "present"},
        transport=transport,
    )
    client = Client(base_url="https://unused.test").set_httpx_client(http_client)

    result = post_feature.sync_detailed("a/b", client=client, body=item)

    assert result.status_code == 202
    assert result.parsed is None
    http_client.close()


def test_async_detailed_sends_contract_request() -> None:
    async def run() -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert request.url.path == "/collections/collection/items/item"
            assert request.headers["If-Match"] == '"revision-1"'
            assert request.headers["Content-Type"] == "application/json"
            assert request.content == b'{"properties":{"quality":"updated"}}'
            return httpx.Response(
                204, headers={"ETag": '"revision-2"'}, request=request
            )

        transport = httpx.MockTransport(handler)
        http_client = httpx.AsyncClient(
            base_url="https://stac.example.test", transport=transport
        )
        client = Client(base_url="https://unused.test").set_async_httpx_client(
            http_client
        )

        result = await patch_feature.asyncio_detailed(
            "collection",
            "item",
            client=client,
            body={"properties": {"quality": "updated"}},
            if_match='"revision-1"',
        )

        assert result.status_code == 204
        assert result.headers["ETag"] == '"revision-2"'
        assert result.parsed is None
        await http_client.aclose()

    asyncio.run(run())
