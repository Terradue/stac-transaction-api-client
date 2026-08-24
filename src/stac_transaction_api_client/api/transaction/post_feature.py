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

from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx
from pystac import Collection, Item

from ...client import AuthenticatedClient, Client
from ...models import Exception as Exception_
from ...types import UNSET, Response, Unset


def _get_kwargs(
    collection_id: str,
    *,
    body: Item | Collection | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/collections/{collection_id}/items".format(
            collection_id=quote(str(collection_id), safe=""),
        ),
    }

    if body:
        _kwargs["json"] = body.to_dict()
        headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | Exception_ | Item:
    if response.status_code == 201:
        return Item.from_dict(response.json())

    if response.status_code == 202:
        return cast("Any", None)

    if response.status_code == 400:
        return Exception_.model_validate(response.json())

    if response.status_code == 404:
        return cast("Any", None)

    if response.status_code == 500:
        return Exception_.model_validate(response.json())

    return Exception_.model_validate(response.json())


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | Exception_ | Item]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    collection_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: Item | Collection | Unset = UNSET,
) -> Response[Any | Exception_ | Item]:
    """add a new STAC Item or Items in an ItemCollection to a collection

     create a new STAC Item r Items in an ItemCollection in a specific collection

    Args:
        collection_id (str):
        body (Item | Collection | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Exception_ | Item]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    collection_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: Item | Collection | Unset = UNSET,
) -> Any | Exception_ | Item | None:
    """add a new STAC Item or Items in an ItemCollection to a collection

     create a new STAC Item r Items in an ItemCollection in a specific collection

    Args:
        collection_id (str):
        body (Item | Collection | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Exception_ | Item
    """

    return sync_detailed(
        collection_id=collection_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    collection_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: Item | Collection | Unset = UNSET,
) -> Response[Any | Exception_ | Item]:
    """add a new STAC Item or Items in an ItemCollection to a collection

     create a new STAC Item r Items in an ItemCollection in a specific collection

    Args:
        collection_id (str):
        body (Item | Collection | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Exception_ | Item]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: Item | Collection | Unset = UNSET,
) -> Any | Exception_ | Item | None:
    """add a new STAC Item or Items in an ItemCollection to a collection

     create a new STAC Item r Items in an ItemCollection in a specific collection

    Args:
        collection_id (str):
        body (Item | Collection | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Exception_ | Item
    """

    return (
        await asyncio_detailed(
            collection_id=collection_id,
            client=client,
            body=body,
        )
    ).parsed
