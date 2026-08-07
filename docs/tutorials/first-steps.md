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

# First steps: complete an item transaction lifecycle

In this tutorial you will create a STAC Item, read it back, replace it using an
ETag, and finally delete it. This gives you the core workflow used by the client.

You need:

- Python 3.10 or newer;
- a STAC API implementing the Transaction Extension;
- a collection where you may create and delete an item.

The examples use `https://stac.example.com` and `example-collection` as
placeholders. Substitute values for your service.

## 1. Install the client

Install the package with the PySTAC extra because the endpoint modules use
`pystac.Item` directly:

```console
python -m pip install "stac-transaction-api-client[pystac]"
```

## 2. Create a client

Create an unauthenticated client first:

```python
from stac_transaction_api_client import Client

client = Client(base_url="https://stac.example.com")
collection_id = "example-collection"
```

If your service requires a bearer token, use `AuthenticatedClient` instead:

```python
from stac_transaction_api_client import AuthenticatedClient

client = AuthenticatedClient(
    base_url="https://stac.example.com",
    token="your-access-token",
)
collection_id = "example-collection"
```

The endpoint calls are the same for both client classes.

## 3. Build a PySTAC Item

Create a small point item for the tutorial:

```python
from datetime import datetime, timezone

from pystac import Item

item = Item(
    id="stac-transaction-client-tutorial",
    geometry={"type": "Point", "coordinates": [12.5, 41.9]},
    bbox=[12.5, 41.9, 12.5, 41.9],
    datetime=datetime.now(timezone.utc),
    properties={"tutorial:step": "created"},
)
```

The collection identifier is supplied in the request path. The Transaction
Extension defines the server as responsible for populating the item's
`collection` field from that path.

## 4. Create the item

Use `post_feature.sync_detailed` so you retain the status code and response
headers in addition to the parsed body:

```python
from http import HTTPStatus

from stac_transaction_api_client.api.transaction import post_feature

created = post_feature.sync_detailed(
    collection_id,
    client=client,
    body=item,
)

if created.status_code == HTTPStatus.CREATED:
    print("created")
elif created.status_code == HTTPStatus.ACCEPTED:
    print("accepted for asynchronous processing")
else:
    raise RuntimeError(f"create failed: {created.status_code}")
```

For the rest of this tutorial, use a service that completes the operation
synchronously so the item can be fetched immediately.

## 5. Retrieve the item and its ETag

The current `get_feature` module exposes detailed sync and async calls. Fetch the
item with `sync_detailed`:

```python
from stac_transaction_api_client.api.transaction import get_feature

current = get_feature.sync_detailed(
    collection_id,
    item.id,
    client=client,
)

if current.parsed is None:
    raise RuntimeError(f"item was not returned: {current.status_code}")

print(current.parsed.id)
```

The Transaction Extension supports optimistic locking with ETags. The current
client requires an `if_match` value for `PUT` and `DELETE`, so read the ETag from
the detailed response:

```python
etag = current.headers.get("ETag")
if etag is None:
    raise RuntimeError("the service did not return an ETag")
```

## 6. Replace the item

Change a property on the returned PySTAC Item and send the complete item back
with `update_feature`:

```python
from stac_transaction_api_client.api.transaction import update_feature

current.parsed.properties["tutorial:step"] = "replaced"

replaced = update_feature.sync_detailed(
    collection_id,
    current.parsed.id,
    client=client,
    body=current.parsed,
    if_match=etag,
)

if replaced.status_code not in {
    HTTPStatus.OK,
    HTTPStatus.ACCEPTED,
    HTTPStatus.NO_CONTENT,
}:
    raise RuntimeError(f"replace failed: {replaced.status_code}")
```

A stale ETag can result in `412 Precondition Failed`. Fetch the resource again
before retrying rather than reusing an old ETag.

## 7. Delete the item

Fetch the item again so the delete uses its current ETag:

```python
latest = get_feature.sync_detailed(
    collection_id,
    item.id,
    client=client,
)
latest_etag = latest.headers.get("ETag")

if latest_etag is None:
    raise RuntimeError("the service did not return an ETag")
```

Delete it:

```python
from stac_transaction_api_client.api.transaction import delete_feature

deleted = delete_feature.sync_detailed(
    collection_id,
    item.id,
    client=client,
    if_match=latest_etag,
)

if deleted.status_code not in {
    HTTPStatus.OK,
    HTTPStatus.ACCEPTED,
    HTTPStatus.NO_CONTENT,
}:
    raise RuntimeError(f"delete failed: {deleted.status_code}")
```

You have now completed the core transaction lifecycle.

## Where to go next

Use [Perform item transactions](../how-to/transactions.md) when you need focused
recipes for authentication, patching, deleting, or asynchronous calls. Use the
[reference](../reference/index.md) when you need exact function signatures and
return types.
