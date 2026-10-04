import asyncio
import httpx
import pytest

from app.checker import check_http, check_target, check_tcp

async def test_http_up_when_status_200():
    transport = httpx.MockTransport(lambda request: httpx.Response(200))
    async with httpx.AsyncClient(transport=transport) as client:
        result = await check_http(client, "https://example.com")
    assert result["up"] is True
    assert result["status_code"] == 200
    assert result["response_ms"] is not None

async def test_http_down_when_status_500():
    transport = httpx.MockTransport(lambda request: httpx.Response(500))
    async with httpx.AsyncClient(transport=transport) as client:
        result = await check_http(client, "https://example.com")
    assert result["up"] is False
    assert result["status_code"] == 500

async def test_http_down_when_connection_fails():

    def broken(request):
        raise httpx.ConnectError("boom", request=request)

    transport = httpx.MockTransport(broken)
    async with httpx.AsyncClient(transport=transport) as client:
        result = await check_http(client, "https://example.com")
    assert result["up"] is False
    assert result["error"] == "ConnectError"

async def test_tcp_up_when_port_is_open():
    server = await asyncio.start_server(lambda reader, writer: writer.close(), "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    async with server:
        result = await check_tcp("127.0.0.1", port)
    assert result["up"] is True

async def test_unknown_target_type_raises():
    async with httpx.AsyncClient() as client:
        with pytest.raises(ValueError):
            await check_target(client, {"name": "x", "type": "carrier-pigeon"})