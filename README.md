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

# STAC Transaction API Client

[![PyPI - Version](https://img.shields.io/pypi/v/stac-transaction-api-client.svg)](https://pypi.org/project/stac-transaction-api-client)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/stac-transaction-api-client.svg)](https://pypi.org/project/stac-transaction-api-client)

`stac-transaction-api-client` is a Python client for the
[STAC API Transaction Extension](https://github.com/stac-api-extensions/transaction).
It exposes synchronous and asynchronous helpers for item transactions and uses
[PySTAC](https://pystac.readthedocs.io/) objects for STAC item payloads and
successful item responses.

The client currently covers:

- `GET /collections/{collectionId}/items/{featureId}` for retrieving an item;
- `POST /collections/{collectionId}/items` for creating an item;
- `PUT /collections/{collectionId}/items/{featureId}` for replacing an item;
- `PATCH /collections/{collectionId}/items/{featureId}` for updating an item;
- `DELETE /collections/{collectionId}/items/{featureId}` for deleting an item;
- unauthenticated and bearer-token authenticated `httpx` clients;
- synchronous and asynchronous request helpers;
- detailed responses containing the HTTP status, headers, raw bytes, and parsed payload.

## Installation

The transaction endpoint modules import PySTAC directly, so install the `pystac`
extra for normal use:

```console
python -m pip install "stac-transaction-api-client[pystac]"
```

The package requires Python 3.10 or newer.

## Quick start

The example below creates one STAC Item and reads it back. Replace the base URL
and collection ID with values from a transaction-enabled STAC API.

```python
from datetime import datetime, timezone
from http import HTTPStatus

from pystac import Item

from stac_transaction_api_client import Client
from stac_transaction_api_client.api.transaction import get_feature, post_feature

client = Client(base_url="https://stac.example.com")
collection_id = "example-collection"

item = Item(
    id="example-item",
    geometry={"type": "Point", "coordinates": [12.5, 41.9]},
    bbox=[12.5, 41.9, 12.5, 41.9],
    datetime=datetime.now(timezone.utc),
    properties={},
)

created = post_feature.sync_detailed(
    collection_id,
    client=client,
    body=item,
)

if created.status_code not in {HTTPStatus.CREATED, HTTPStatus.ACCEPTED}:
    raise RuntimeError(f"create failed: {created.status_code}")

fetched = get_feature.sync_detailed(
    collection_id,
    item.id,
    client=client,
)

if fetched.parsed is not None:
    print(fetched.parsed.id)
```

For secured APIs, use `AuthenticatedClient`:

```python
from stac_transaction_api_client import AuthenticatedClient

client = AuthenticatedClient(
    base_url="https://stac.example.com",
    token="your-access-token",
)
```

## Optimistic locking

The Transaction Extension supports optimistic locking with ETags. In the current
client API, `update_feature` (`PUT`) and `delete_feature` require an `if_match`
argument, while `patch_feature` accepts it optionally. Retrieve the current ETag
from a detailed response before modifying or deleting an item:

```python
current = get_feature.sync_detailed(
    "example-collection",
    "example-item",
    client=client,
)
etag = current.headers.get("ETag")
```

See the [how-to guides](https://eoap.github.io/stac-transaction-api-client/how-to/)
for complete create, replace, patch, delete, authentication, and asynchronous
examples.

## Current payload typing

The implementation intentionally reuses PySTAC instead of generated STAC models.
Two current type boundaries are important when integrating it:

- `post_feature` is reliable for a single `pystac.Item`. Its generated annotation
  also includes `pystac.Collection`, while the Transaction specification describes
  bulk creation in terms of an ItemCollection.
- `patch_feature` currently accepts a `pystac.Item`, not an arbitrary JSON Merge
  Patch dictionary. The HTTP endpoint is `PATCH`, but the Python type does not yet
  model a free-form RFC 7386 fragment.

The [API reference](https://eoap.github.io/stac-transaction-api-client/reference/)
documents the exact signatures exposed by the current codebase.

## Documentation

The documentation follows the [Diataxis](https://diataxis.fr/) structure:

- [Tutorials](https://eoap.github.io/stac-transaction-api-client/tutorials/) for guided learning;
- [How-to guides](https://eoap.github.io/stac-transaction-api-client/how-to/) for concrete tasks;
- [Reference](https://eoap.github.io/stac-transaction-api-client/reference/) for signatures and behavior;
- [Explanation](https://eoap.github.io/stac-transaction-api-client/explanation/) for architecture and design context.

## Development

Install [Hatch](https://hatch.pypa.io/) and [Task](https://taskfile.dev/), then
install the repository with the PySTAC extra or create the configured development
environment.

Install the Git hook with:

```console
task quality:pre-commit:install
```

Run all configured quality checks with:

```console
task quality:pre-commit:run
```

The `Taskfile.yaml` also contains the OpenAPI bundling and client-generation
workflow used to derive the client from the upstream Transaction specification.

## Contributing

Open a [GitHub issue](https://github.com/Terradue/stac-transaction-api-client/issues)
for bugs, documentation gaps, or enhancement proposals. See
[`CONTRIBUTING.md`](CONTRIBUTING.md) for repository contribution guidance.

## License

[![Apache License, Version 2.0](https://img.shields.io/badge/license-Apache%20License%202.0-blue)](https://www.apache.org/licenses/LICENSE-2.0)

Licensed under the Apache License, Version 2.0.
