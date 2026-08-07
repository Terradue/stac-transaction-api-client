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

# Install the client

The project requires Python 3.10 or newer.

## Install from PyPI for transaction use

Install the `pystac` extra. The transaction endpoint modules import PySTAC
objects directly, so this is the recommended installation for API use:

```console
python -m pip install "stac-transaction-api-client[pystac]"
```

Verify the import:

```console
python -c "from stac_transaction_api_client import Client; from stac_transaction_api_client.api.transaction import post_feature"
```

## Install only the core package

The base package can be installed without the optional extra:

```console
python -m pip install stac-transaction-api-client
```

This installs the transport/client dependencies, but importing transaction
modules that reference `pystac.Item` or `pystac.Collection` requires PySTAC to be
installed separately.

## Install from source

Clone the repository and install it in editable mode with PySTAC support:

```console
git clone https://github.com/Terradue/stac-transaction-api-client.git
cd stac-transaction-api-client
python -m pip install -e ".[pystac]"
```

## Set up a development environment

The repository uses Hatch and Task for its development workflows. After cloning
the project, install the pre-commit hook with:

```console
task quality:pre-commit:install
```

Run all configured checks with:

```console
task quality:pre-commit:run
```
