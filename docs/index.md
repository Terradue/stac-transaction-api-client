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

`stac-transaction-api-client` is a Python client for the STAC API Transaction
Extension. It provides sync and async endpoint helpers backed by `httpx` and
uses PySTAC objects for STAC item payloads and successful item responses.

## Choose the documentation you need

- [Tutorials](tutorials/): learn the client through a complete item lifecycle.
- [How-to guides](how-to/): install the package or perform a specific transaction.
- [Reference](reference/): look up endpoint signatures, response types, and client options.
- [Explanation](explanation/): understand generation, PySTAC integration, and optimistic locking.

## Quick start

Install the package with the PySTAC integration used by the transaction modules:

```console
python -m pip install "stac-transaction-api-client[pystac]"
```

Create a client and retrieve an item:

```python
from stac_transaction_api_client import Client
from stac_transaction_api_client.api.transaction import get_feature

client = Client(base_url="https://stac.example.com")
response = get_feature.sync_detailed(
    "example-collection",
    "example-item",
    client=client,
)

item = response.parsed
if item is not None:
    print(item.id)
```

Start with [First steps](tutorials/first-steps.md) for a guided create, read,
replace, and delete workflow.
