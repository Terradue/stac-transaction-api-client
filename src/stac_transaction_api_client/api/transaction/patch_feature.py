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

from collections.abc import Mapping
from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx
from pystac import Item

from ...client import AuthenticatedClient, Client
from ...models import Exception as Exception_
from ...types import UNSET, Response, Unset


def _get_kwargs(
    collection_id: str,
    feature_id: str,
    *,
    body: Mapping[str, Any] | Item | Unset = UNSET,
    if_match: str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(if_match, Unset):
        headers["If-Match"] = if_match

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/collections/{collection_id}/items/{feature_id}".format(
            collection_id=quote(str(collection_id), safe=""),
            feature_id=quote(str(feature_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = dict(body) if isinstance(body, Mapping) else body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | Exception_ | Item:
    if response.status_code == 200:
        return Item.from_dict(response.json())

    if response.status_code == 202:
        return cast("Any", None)

    if response.status_code == 204:
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
    feature_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: Mapping[str, Any] | Item | Unset = UNSET,
    if_match: str | Unset = UNSET,
) -> Response[Any | Exception_ | Item]:
    """update an existing feature by Id with a partial item definition

     Use this method to update an existing feature. Requires a GeoJSON fragment (containing the fields to
    be updated) be submitted.

    Args:
        collection_id (str):
        feature_id (str):
        if_match (str | Unset):
        body (Mapping[str, Any] | Item | Unset): An object that contains at least a subset of the fields for a
            STAC Item.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Exception_ | Item]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        feature_id=feature_id,
        body=body,
        if_match=if_match,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    collection_id: str,
    feature_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: Mapping[str, Any] | Item | Unset = UNSET,
    if_match: str | Unset = UNSET,
) -> Any | Exception_ | Item | None:
    """update an existing feature by Id with a partial item definition

     Use this method to update an existing feature. Requires a GeoJSON fragment (containing the fields to
    be updated) be submitted.

    Args:
        collection_id (str):
        feature_id (str):
        if_match (str | Unset):
        body (Mapping[str, Any] | Item | Unset): An object that contains at least a subset of the fields for a
            STAC Item.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Exception_ | Item
    """

    return sync_detailed(
        collection_id=collection_id,
        feature_id=feature_id,
        client=client,
        body=body,
        if_match=if_match,
    ).parsed


async def asyncio_detailed(
    collection_id: str,
    feature_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: Mapping[str, Any] | Item | Unset = UNSET,
    if_match: str | Unset = UNSET,
) -> Response[Any | Exception_ | Item]:
    """update an existing feature by Id with a partial item definition

     Use this method to update an existing feature. Requires a GeoJSON fragment (containing the fields to
    be updated) be submitted.

    Args:
        collection_id (str):
        feature_id (str):
        if_match (str | Unset):
        body (Mapping[str, Any] | Item | Unset): An object that contains at least a subset of the fields for a
            STAC Item.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Exception_ | Item]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        feature_id=feature_id,
        body=body,
        if_match=if_match,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    feature_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: Mapping[str, Any] | Item | Unset = UNSET,
    if_match: str | Unset = UNSET,
) -> Any | Exception_ | Item | None:
    """update an existing feature by Id with a partial item definition

     Use this method to update an existing feature. Requires a GeoJSON fragment (containing the fields to
    be updated) be submitted.

    Args:
        collection_id (str):
        feature_id (str):
        if_match (str | Unset):
        body (Mapping[str, Any] | Item | Unset): An object that contains at least a subset of the fields for a
            STAC Item.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Exception_ | Item
    """

    return (
        await asyncio_detailed(
            collection_id=collection_id,
            feature_id=feature_id,
            client=client,
            body=body,
            if_match=if_match,
        )
    ).parsed
