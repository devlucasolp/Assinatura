"""
Carregado automaticamente pelo Python no boot da sandbox.
Injeta o header X-Sandbox-Instance em TODOS os requests HTTP de httpx/requests/urllib3.
Isso identifica a instância no egress-proxy.
"""

import os

_INSTANCE_ID = os.getenv("SANDBOX_INSTANCE_ID", "")
_HEADER_NAME = "X-Sandbox-Instance"


if _INSTANCE_ID:
    # --- httpx (síncrono e async) ---
    try:
        import httpx

        _orig_send = httpx.Client.send
        def _httpx_send(self, request, **kwargs):
            request.headers[_HEADER_NAME] = _INSTANCE_ID
            return _orig_send(self, request, **kwargs)
        httpx.Client.send = _httpx_send

        _orig_async_send = httpx.AsyncClient.send
        async def _httpx_async_send(self, request, **kwargs):
            request.headers[_HEADER_NAME] = _INSTANCE_ID
            return await _orig_async_send(self, request, **kwargs)
        httpx.AsyncClient.send = _httpx_async_send
    except Exception:
        pass

    # --- requests ---
    try:
        from requests.sessions import Session as _RSession
        _orig_request = _RSession.request
        def _requests_request(self, method, url, **kwargs):
            headers = kwargs.get("headers") or {}
            headers[_HEADER_NAME] = _INSTANCE_ID
            kwargs["headers"] = headers
            return _orig_request(self, method, url, **kwargs)
        _RSession.request = _requests_request
    except Exception:
        pass

    # --- urllib3 (cobre urllib3 direto + libs que não passam por httpx/requests) ---
    try:
        from urllib3 import PoolManager
        _orig_urlopen = PoolManager.urlopen
        def _u3_urlopen(self, method, url, **kwargs):
            headers = kwargs.get("headers") or {}
            try: headers[_HEADER_NAME] = _INSTANCE_ID
            except Exception: pass
            kwargs["headers"] = headers
            return _orig_urlopen(self, method, url, **kwargs)
        PoolManager.urlopen = _u3_urlopen
    except Exception:
        pass
