import time

import httpx

def check_http(url: str, timeout: float = 5.0) -> dict:
    start = time.perf_counter()

    try:
        response = httpx.get(url, timeout=timeout, follow_redirects = True)
        elapsed_ms = round((time.perf_counter() - start) * 1000)
        return {
            "url": url,
            "up": response.status_code < 400,
            "status_code": response.status_code,
            "response_ms": elapsed_ms
        }

    except httpx.RequestError as error:
        return {
            "url": url,
            "up": False,
            "status_code": None,
            "response_ms": None,
            "error": type(error).__name__
        }