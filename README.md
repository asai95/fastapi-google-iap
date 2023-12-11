# fastapi-google-iap

![PyPI - Version](https://img.shields.io/pypi/v/fastapi-google-iap?color=%2300CD00)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fastapi-google-iap)](https://pypi.org/project/fastapi-google-iap/)
[![PyPI - License](https://img.shields.io/pypi/l/fastapi-google-iap)](https://pypi.org/project/fastapi-google-iap/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/fastapi-google-iap)](https://pypi.org/project/fastapi-google-iap/)
[![codecov](https://codecov.io/gh/asai95/fastapi-google-iap/branch/master/graph/badge.svg)](https://codecov.io/gh/asai95/fastapi-google-iap)

A FastAPI plugin for Google Cloud Identity-Aware Proxy (IAP) authentication.

## Installation

```bash
pip install fastapi-google-iap
```

## Usage

```python
from fastapi import FastAPI
from fastapi_google_iap import GoogleIapMiddleware

app = FastAPI()

app.use_middleware(
    GoogleIapMiddleware,
    audience="/projects/999999999999/apps/example-project",
    unprotected_routes=["/healthz"],
    restrict_to_domains=["example.com"],
)
```

## License

This project is licensed under the terms of the MIT license.