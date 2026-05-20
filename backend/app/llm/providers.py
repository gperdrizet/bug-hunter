from abc import ABC, abstractmethod

from app.config import settings


class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, prompt: str) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        raise NotImplementedError

    @property
    def provider_name(self) -> str:
        return self.__class__.__name__.replace("Provider", "").lower()


class OpenAIProvider(LLMProvider):
    def __init__(self):
        from openai import AsyncOpenAI
        kwargs = {"api_key": settings.openai_api_key or "llama-cpp"}
        if settings.openai_base_url:
            kwargs["base_url"] = settings.openai_base_url
        self._client = AsyncOpenAI(**kwargs)
        self._model = settings.openai_model

    @property
    def model_name(self) -> str:
        return self._model

    async def complete(self, prompt: str) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content or ""


class AnthropicProvider(LLMProvider):
    def __init__(self):
        import anthropic
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.anthropic_model

    @property
    def model_name(self) -> str:
        return self._model

    async def complete(self, prompt: str) -> str:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text


class OllamaProvider(LLMProvider):
    def __init__(self):
        import httpx
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=120.0)

    @property
    def model_name(self) -> str:
        return self._model

    async def complete(self, prompt: str) -> str:
        response = await self._client.post(
            "/api/chat",
            json={
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"]


def get_provider() -> LLMProvider:
    name = settings.llm_provider.lower()
    if name == "openai":
        return OpenAIProvider()
    elif name == "anthropic":
        return AnthropicProvider()
    elif name == "ollama":
        return OllamaProvider()
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {name!r}. Must be openai, anthropic, or ollama.")
