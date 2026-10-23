"""Bearer-token scheme, declared so that the docs offer "Authorize"."""

from fastapi import Security
from fastapi.security import HTTPBearer

# Documentation only: the gateway in front of the API validates the token, so
# `auto_error=False` keeps this app from rejecting a request itself.
bearer_auth = [Security(HTTPBearer(auto_error=False))]
