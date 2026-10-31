import json
from pathlib import Path

import httpx
import pytest

from nutriscan_eval.candidates import CANDIDATES
from nutriscan_eval.provider import ROUTER_URL, HuggingFaceProvider, ProviderFailure


@pytest.mark.asyncio
async def test_provider_sends_data_url_and_strict_schema() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "chat_completion.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == ROUTER_URL
        assert request.headers["Authorization"] == "Bearer hf_fixture_secret"
        payload = json.loads(request.content)
        assert payload["model"] == "Qwen/Qwen3.5-9B:deepinfra"
        assert payload["temperature"] == 0
        assert payload["response_format"]["json_schema"]["strict"] is True
        image_url = payload["messages"][1]["content"][1]["image_url"]["url"]
        assert image_url.startswith("data:image/jpeg;base64,")
        return httpx.Response(200, json=fixture)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = HuggingFaceProvider("hf_fixture_secret", client=client)
        result = await provider.recognize(CANDIDATES["primary"], "data:image/jpeg;base64,ZmFrZQ==")
    assert result.result.detected_foods[0].name == "dal"
    assert result.usage.total_tokens == 1280
    assert not result.nutrition_leak


@pytest.mark.asyncio
async def test_invalid_schema_is_reported_without_returning_raw_content() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "calories: 500"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = HuggingFaceProvider("hf_fixture_secret", client=client)
        with pytest.raises(ProviderFailure) as captured:
            await provider.recognize(CANDIDATES["primary"], "data:image/jpeg;base64,ZmFrZQ==")
    assert captured.value.code == "INVALID_SCHEMA"
    assert captured.value.nutrition_leak
    assert captured.value.usage.total_tokens == 15
    assert "calories: 500" not in str(captured.value)
