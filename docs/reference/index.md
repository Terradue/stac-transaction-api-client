<!--
Copyright 2026 Terradue

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Reference

This section describes the public objects and endpoint functions exposed by the
current codebase.

## Transaction endpoint summary

| Operation | HTTP request | Module | Sync API | Async API | `If-Match` |
| --- | --- | --- | --- | --- | --- |
| Retrieve item | `GET /collections/{collection_id}/items/{feature_id}` | `get_feature` | `sync_detailed` | `asyncio_detailed` | n/a |
| Create item | `POST /collections/{collection_id}/items` | `post_feature` | `sync`, `sync_detailed` | `asyncio`, `asyncio_detailed` | n/a |
| Replace item | `PUT /collections/{collection_id}/items/{feature_id}` | `update_feature` | `sync`, `sync_detailed` | `asyncio`, `asyncio_detailed` | required |
| Patch item | `PATCH /collections/{collection_id}/items/{feature_id}` | `patch_feature` | `sync`, `sync_detailed` | `asyncio`, `asyncio_detailed` | optional |
| Delete item | `DELETE /collections/{collection_id}/items/{feature_id}` | `delete_feature` | `sync`, `sync_detailed` | `asyncio`, `asyncio_detailed` | required |

## Client classes

`stac_transaction_api_client.Client` stores the base URL and HTTP configuration.
`stac_transaction_api_client.AuthenticatedClient` adds an authorization token,
using `Bearer` as the default prefix and `Authorization` as the default header
name.

Both classes support:

- `headers` and `cookies` applied to requests;
- `timeout`;
- TLS verification through `verify_ssl`;
- redirect handling through `follow_redirects`;
- extra `httpx.Client` and `httpx.AsyncClient` constructor arguments through `httpx_args`;
- sync and async context-manager use;
- injection of an existing `httpx.Client` or `httpx.AsyncClient`.

## Detailed responses

Detailed endpoint functions return `stac_transaction_api_client.types.Response[T]`.
It contains:

| Field | Type | Meaning |
| --- | --- | --- |
| `status_code` | `http.HTTPStatus` | HTTP response status |
| `content` | `bytes` | Raw response body |
| `headers` | mutable mapping | HTTP response headers |
| `parsed` | `T | None` | Parsed endpoint-specific result |

Successful item bodies are converted to `pystac.Item`. Error bodies handled by
mutation endpoints use `stac_transaction_api_client.models.Exception`, which has
a required `code`, an optional `description`, and allows additional fields.

## Current PySTAC body types

- `post_feature`: `pystac.Item | pystac.Collection | Unset`.
- `update_feature`: `pystac.Item | Unset`.
- `patch_feature`: `pystac.Item | Unset`.

The upstream Transaction specification describes POST bulk payloads as
ItemCollections and PATCH payloads as JSON Merge Patch fragments. Those concepts
are not fully represented by the current generated Python annotations, so the
how-to guides favor single-item POST and call out the PATCH constraint.

For generated signatures and docstrings, see [API objects](api.md).
