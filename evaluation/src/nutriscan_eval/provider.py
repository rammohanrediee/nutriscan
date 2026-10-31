import json
import time
from dataclasses import dataclass
from typing import Any, Protocol

import httpx
from pydantic import ValidationError

from .candidates import Candidate
from .privacy import contains_nutrition_language, safe_error
from .prompt import messages_for_image, strict_response_format
from .schemas import ProviderUsage, RecognitionResult

ROUTER_URL = "https://router.huggingface.co/v1/chat/completions"


@dataclass(frozen=True, slots=True)
class ProviderObservation:
    result: RecognitionResult
    latency_seconds: float
    usage: ProviderUsage
    response_id: str | None
    system_fingerprint: str | None
    nutrition_leak: bool


class VisionProvider(Protocol):
    async def recognize(self, candidate: Candidate, data_url: str) -> ProviderObservation: ...


class ProviderFailure(RuntimeError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        latency_seconds: float,
        nutrition_leak: bool = False,
        usage: ProviderUsage | None = None,
    ) -> None:
        super().__init__(safe_error(message))
        self.code = code
        self.latency_seconds = latency_seconds
        self.nutrition_leak = nutrition_leak
        self.usage = usage or ProviderUsage()


def _message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    raise TypeError("Provider message content was not text")


class HuggingFaceProvider:
    def __init__(
        self,
        token: str,
        *,
        timeout_seconds: float = 30.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not token:
            raise ValueError("HF_TOKEN is required")
        self._token = token
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds))

    async def __aenter__(self) -> "HuggingFaceProvider":
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def recognize(self, candidate: Candidate, data_url: str) -> ProviderObservation:
        payload = {
            "model": candidate.routed_model,
            "messages": messages_for_image(data_url),
            "response_format": strict_response_format(),
            "temperature": 0,
            "max_tokens": 600,
        }
        started = time.perf_counter()
        try:
            response = await self._client.post(
                ROUTER_URL,
                headers={"Authorization": f"Bearer {self._token}"},
                json=payload,
            )
            response.raise_for_status()
            body = response.json()
            content = _message_text(body["choices"][0]["message"]["content"])
        except httpx.TimeoutException as error:
            raise ProviderFailure(
                "TIMEOUT",
                "Provider request timed out",
                latency_seconds=time.perf_counter() - started,
            ) from error
        except httpx.HTTPStatusError as error:
            raise ProviderFailure(
                f"HTTP_{error.response.status_code}",
                f"Provider returned HTTP {error.response.status_code}",
                latency_seconds=time.perf_counter() - started,
            ) from error
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
            raise ProviderFailure(
                "TRANSPORT_OR_RESPONSE_ERROR",
                safe_error(error),
                latency_seconds=time.perf_counter() - started,
            ) from error

        latency = time.perf_counter() - started
        nutrition_leak = contains_nutrition_language(content)
        usage = ProviderUsage.model_validate(body.get("usage", {}))
        try:
            result = RecognitionResult.model_validate(json.loads(content))
        except (json.JSONDecodeError, ValidationError) as error:
            raise ProviderFailure(
                "INVALID_SCHEMA",
                safe_error(error),
                latency_seconds=latency,
                nutrition_leak=nutrition_leak,
                usage=usage,
            ) from error
        return ProviderObservation(
            result=result,
            latency_seconds=latency,
            usage=usage,
            response_id=body.get("id"),
            system_fingerprint=body.get("system_fingerprint"),
            nutrition_leak=nutrition_leak,
        )
