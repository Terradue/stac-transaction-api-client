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

# Perform item transactions

These recipes assume the package was installed with the PySTAC extra:

```console
python -m pip install "stac-transaction-api-client[pystac]"
```

## Create a client

For a public API:

```python
from stac_transaction_api_client import Client

client = Client(base_url="https://stac.example.com")
```

For a bearer-token protected API:

```python
from stac_transaction_api_client import AuthenticatedClient

client = AuthenticatedClient(
    base_url="https://stac.example.com",
    token="your-access-token",
)
```

You can also pass `headers`, `cookies`, `timeout`, `verify_ssl`,
`follow_redirects`, and additional `httpx_args` when constructing either client.

## Create one item

Pass a `pystac.Item` to `post_feature`:

```python
from datetime import datetime, timezone

from pystac import Item

from stac_transaction_api_client.api.transaction import post_feature

item = Item(
    id="example-item",
    geometry={"type": "Point", "coordinates": [12.5, 41.9]},
    bbox=[12.5, 41.9, 12.5, 41.9],
    datetime=datetime.now(timezone.utc),
    properties={},
)

response = post_feature.sync_detailed(
    "example-collection",
    client=client,
    body=item,
)

print(response.status_code)
print(response.parsed)
```

Use `post_feature.sync(...)` if you only need the parsed result.

!!! note "Bulk create typing"
    The current generated signature also accepts `pystac.Collection`. The STAC
    Transaction specification defines bulk creation using an ItemCollection, not
    a STAC Collection metadata object. Prefer single-item creation until the
    Python body type is aligned with that specification contract.

## Retrieve an item

`get_feature` exposes detailed variants only:

```python
from stac_transaction_api_client.api.transaction import get_feature

response = get_feature.sync_detailed(
    "example-collection",
    "example-item",
    client=client,
)

item = response.parsed
if item is not None:
    print(item.to_dict())
```

Use the detailed response when you need the ETag:

```python
etag = response.headers.get("ETag")
```

## Replace an item with PUT

`update_feature` requires the complete `pystac.Item` and an `if_match` string.
Fetch the current resource first, then update it with the returned ETag:

```python
from stac_transaction_api_client.api.transaction import get_feature, update_feature

current = get_feature.sync_detailed(
    "example-collection",
    "example-item",
    client=client,
)

if current.parsed is None:
    raise RuntimeError("item not found")

etag = current.headers.get("ETag")
if etag is None:
    raise RuntimeError("service did not return an ETag")

current.parsed.properties["processing:state"] = "ready"

updated = update_feature.sync_detailed(
    "example-collection",
    "example-item",
    client=client,
    body=current.parsed,
    if_match=etag,
)
```

If another writer changed the resource first, the server can reject the request
with `412 Precondition Failed`. Fetch the item again to obtain its new state and
ETag before deciding whether to retry.

## Patch an item

`patch_feature` maps to the HTTP `PATCH` endpoint and accepts `if_match`
optionally:

```python
from stac_transaction_api_client.api.transaction import patch_feature

patched = patch_feature.sync_detailed(
    "example-collection",
    "example-item",
    client=client,
    body=current.parsed,
    if_match=etag,
)
```

!!! important "Current PATCH body type"
    The Transaction Extension defines PATCH semantics using JSON Merge Patch.
    The current Python signature is typed as `pystac.Item | Unset` and serializes
    the body through `Item.to_dict()`. It therefore does not expose an arbitrary
    dictionary fragment for RFC 7386 merge-patch operations. Use this endpoint
    only when a PySTAC Item payload is appropriate for the target service.

## Delete an item

`delete_feature` requires an `if_match` value:

```python
from stac_transaction_api_client.api.transaction import delete_feature, get_feature

current = get_feature.sync_detailed(
    "example-collection",
    "example-item",
    client=client,
)
etag = current.headers.get("ETag")

if etag is None:
    raise RuntimeError("service did not return an ETag")

deleted = delete_feature.sync_detailed(
    "example-collection",
    "example-item",
    client=client,
    if_match=etag,
)

print(deleted.status_code)
```

## Use asynchronous calls

Each mutation module exposes `asyncio_detailed(...)` and `asyncio(...)` variants.
`get_feature` exposes `asyncio_detailed(...)`.

```python
import asyncio

from stac_transaction_api_client import Client
from stac_transaction_api_client.api.transaction import get_feature


async def main() -> None:
    async with Client(base_url="https://stac.example.com") as client:
        response = await get_feature.asyncio_detailed(
            "example-collection",
            "example-item",
            client=client,
        )
        print(response.status_code)


asyncio.run(main())
```

## Inspect the raw HTTP response

Use a `*_detailed` function whenever you need more than the parsed object. It
returns `Response[T]` with:

- `status_code`: an `http.HTTPStatus` value;
- `headers`: the response headers, including ETag when supplied by the server;
- `content`: raw response bytes;
- `parsed`: the parsed PySTAC Item, error model, or `None`, depending on the endpoint and status.
