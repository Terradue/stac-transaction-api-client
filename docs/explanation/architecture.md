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

# Architecture and design

`stac-transaction-api-client` is a small generated HTTP client adapted to use
PySTAC objects at the STAC Item boundary. Its runtime design separates transport,
endpoint behavior, STAC objects, and error models.

## Source and generation pipeline

The repository keeps both the upstream and bundled OpenAPI descriptions under
`schemas/`. `Taskfile.yaml` defines two relevant tasks:

1. `bundle_api` downloads the Transaction Extension `openapi.yaml` from
   `stac-api-extensions/transaction` and bundles it locally.
2. `client_generation` runs the shared OpenAPI client generator and then removes
   generated STAC model modules as part of the adaptation toward PySTAC.

The resulting endpoint modules live under:

```text
src/stac_transaction_api_client/api/transaction/
```

The current endpoint set is `get_feature`, `post_feature`, `update_feature`,
`patch_feature`, and `delete_feature`.

## Runtime layers

The client can be understood as four layers:

```text
application code
    |
    v
transaction endpoint modules
    |
    +--> PySTAC Item serialization/deserialization
    |
    v
Client / AuthenticatedClient
    |
    v
httpx.Client / httpx.AsyncClient
    |
    v
STAC API
```

### Transport clients

`Client` owns base URL, headers, cookies, timeout, TLS verification, redirect
behavior, and optional extra `httpx` arguments. It lazily creates either a sync
`httpx.Client` or async `httpx.AsyncClient`.

`AuthenticatedClient` adds token-based authentication. By default it sends:

```text
Authorization: Bearer <token>
```

Both classes can also wrap an externally created `httpx` client, which is useful
when an application already manages connection pools, middleware, proxies, or
custom transports.

### Endpoint modules

Each transaction operation is represented by a module rather than a method on
the client object. A typical generated module performs four steps:

1. build request arguments;
2. send the request through the configured client;
3. parse the HTTP response into a Python object;
4. optionally wrap the result in `Response[T]`.

Mutation modules provide convenience functions that return only the parsed body
and `*_detailed` functions that preserve the complete response metadata.
`get_feature` currently exposes only detailed sync and async variants.

## Why PySTAC is used

STAC Items already have a well-established Python representation in PySTAC.
Rather than maintaining a second generated model for the same domain object, the
endpoint modules serialize request bodies with `Item.to_dict()` and deserialize
successful item responses with `Item.from_dict()`.

This means callers can construct, inspect, mutate, and validate items using the
same PySTAC objects they use elsewhere in a STAC workflow.

PySTAC is declared as the `pystac` optional dependency in `pyproject.toml`, but
the transaction endpoint modules import it directly. Consequently,
`stac-transaction-api-client[pystac]` is the practical installation target for
transaction use.

## Detailed versus parsed responses

The shared `Response[T]` type preserves:

- the `HTTPStatus` value;
- raw body bytes;
- response headers;
- the parsed result.

That distinction matters for the Transaction Extension because important
protocol state can live outside the JSON body. ETags are the most obvious
example: callers need response headers to implement optimistic locking.

Use a convenience `sync(...)` or `asyncio(...)` function when the parsed body is
all you need. Use `sync_detailed(...)` or `asyncio_detailed(...)` when status,
headers, or raw bytes influence application behavior.

## Optimistic locking and ETags

The Transaction Extension supports optimistic locking through ETags. A client
first reads a resource and receives an ETag representing its current state. The
ETag is then sent in `If-Match` for a mutation. If the resource changed in the
meantime, the server can reject the stale write rather than silently overwrite a
newer version.

The current Python signatures encode that protocol choice explicitly:

- `update_feature` requires `if_match`;
- `delete_feature` requires `if_match`;
- `patch_feature` makes `if_match` optional.

This is why detailed GET responses are central to update and delete workflows:
the parsed `pystac.Item` contains the domain object, while the response headers
contain the concurrency token.

## Where the generated typing does not fully match the specification

Reusing PySTAC simplifies complete-item payloads, while mappings represent
partial PATCH payloads.

### POST and ItemCollection

The Transaction Extension describes POST bodies as an Item or ItemCollection.
The `post_feature` module therefore accepts `pystac.Item` and
`pystac.ItemCollection`; it does not confuse bulk item creation with a STAC
Collection metadata object.

### PATCH and JSON Merge Patch

The Transaction Extension defines PATCH according to JSON Merge Patch semantics.
The `patch_feature` body accepts a mapping containing only the fields to be
merged. It also retains `pystac.Item` support for applications that intentionally
send an item-shaped payload.

The underlying `httpx` client remains available for requests outside the
generated endpoint signatures.

## Sync and async symmetry

The transport layer supports both blocking and asynchronous `httpx` clients.
Mutation modules mirror that with `sync`/`sync_detailed` and
`asyncio`/`asyncio_detailed`. This keeps endpoint semantics the same while
allowing the integration style to match the surrounding application.

Async clients can be used as context managers so connection pools are closed
cleanly:

```python
async with Client(base_url="https://stac.example.com") as client:
    ...
```
