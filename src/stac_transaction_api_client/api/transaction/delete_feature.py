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

from ...client import AuthenticatedClient, Client
from ...models import Exception as Exception_
from ...types import Response


def _get_kwargs(
    collection_id: str,
    feature_id: str,
    *,
    if_match: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["If-Match"] = if_match

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/collections/{collection_id}/items/{feature_id}".format(
            collection_id=quote(str(collection_id), safe=""),
            feature_id=quote(str(feature_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | Exception_:
    if response.status_code == 200:
        return cast("Any", None)

    if response.status_code == 202:
        return cast("Any", None)

    if response.status_code == 204:
        return cast("Any", None)

    if response.status_code == 400:
        return Exception_.model_validate_json(response.json())

    if response.status_code == 404:
        return cast("Any", None)

    if response.status_code == 500:
        return Exception_.model_validate_json(response.json())

    return Exception_.model_validate_json(response.json())


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | Exception_]:
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
    if_match: str,
) -> Response[Any | Exception_]:
    """delete an existing feature by Id

     Use this method to delete an existing feature.

    Args:
        collection_id (str):
        feature_id (str):
        if_match (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Exception_]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        feature_id=feature_id,
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
    if_match: str,
) -> Any | Exception_ | None:
    """delete an existing feature by Id

     Use this method to delete an existing feature.

    Args:
        collection_id (str):
        feature_id (str):
        if_match (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Exception_
    """

    return sync_detailed(
        collection_id=collection_id,
        feature_id=feature_id,
        client=client,
        if_match=if_match,
    ).parsed


async def asyncio_detailed(
    collection_id: str,
    feature_id: str,
    *,
    client: AuthenticatedClient | Client,
    if_match: str,
) -> Response[Any | Exception_]:
    """delete an existing feature by Id

     Use this method to delete an existing feature.

    Args:
        collection_id (str):
        feature_id (str):
        if_match (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Exception_]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        feature_id=feature_id,
        if_match=if_match,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    feature_id: str,
    *,
    client: AuthenticatedClient | Client,
    if_match: str,
) -> Any | Exception_ | None:
    """delete an existing feature by Id

     Use this method to delete an existing feature.

    Args:
        collection_id (str):
        feature_id (str):
        if_match (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Exception_
    """

    return (
        await asyncio_detailed(
            collection_id=collection_id,
            feature_id=feature_id,
            client=client,
            if_match=if_match,
        )
    ).parsed
