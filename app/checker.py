import asyncio
import time

import httpx


async def check_http(client: httpx.AsyncClient, url: str, timeout: float = 5.0) -> dict:
    start = time.perf_counter()
    try:
        response = await client.get(url, timeout=timeout, follow_redirects=True)
        elapsed_ms = round((time.perf_counter() - start) * 1000)
        return {"address": url, "up": response.status_code < 400, "status_code": response.status_code, "response_ms": elapsed_ms}
    except httpx.RequestError as error:
        return {"address": url, "up": False, "status_code": None, "response_ms": None, "error": type(error).__name__}


async def check_tcp(host: str, port: int, timeout: float = 5.0) -> dict:
    address = f"{host}:{port}"
    start = time.perf_counter()
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
        elapsed_ms = round((time.perf_counter() - start) * 1000)
        writer.close()
        await writer.wait_closed()
        return {"address": address, "up": True, "status_code": None, "response_ms": elapsed_ms}
    except OSError as error:
        return {"address": address, "up": False, "status_code": None, "response_ms": None, "error": type(error).__name__}


async def check_target(client: httpx.AsyncClient, target: dict) -> dict:
    if target["type"] == "http":
        result = await check_http(client, target["url"])
    elif target["type"] == "tcp":
        result = await check_tcp(target["host"], target["port"])
    else:
        raise ValueError(f"Unknown target type: {target['type']}")
    result["name"] = target["name"]
    result["type"] = target["type"]
    return result


async def check_all(targets: list[dict]) -> list[dict]:
    async with httpx.AsyncClient() as client:
        return await asyncio.gather(*(check_target(client, target) for target in targets))