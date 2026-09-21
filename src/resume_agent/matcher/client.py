import json
from typing import Dict, Any, Optional
import httpx

from resume_agent.config import get_settings
from resume_agent.logging import logger


class LLMClient:
    """
    Unified LLM Client supporting OpenRouter API (DeepSeek V3, Llama 3.3, Claude),
    Anthropic direct API, and offline deterministic fallback.
    """

    def __init__(self):
        self.settings = get_settings()

    @property
    def is_configured(self) -> bool:
        """Check if an external LLM API key is available."""
        return bool(self.settings.openrouter_api_key or self.settings.anthropic_api_key)

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1500,
        temperature: float = 0.1,
    ) -> Optional[Dict[str, Any]]:
        """
        Execute completion with strict JSON response guarantee.
        Routes to OpenRouter by default, then Anthropic, or returns None if no key configured.
        """
        if self.settings.openrouter_api_key:
            return self._call_openrouter(system_prompt, user_prompt, max_tokens, temperature)
        elif self.settings.anthropic_api_key:
            return self._call_anthropic(system_prompt, user_prompt, max_tokens, temperature)
        return None

    def _call_openrouter(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Optional[Dict[str, Any]]:
        """Call OpenRouter chat completions endpoint."""
        url = f"{self.settings.openrouter_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "HTTP-Referer": "https://github.com/UtkarshSingh-09/Job_Automator-",
            "X-Title": "Autonomous Resume Agent",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }

        import time
        for attempt in range(3):
            try:
                with httpx.Client(timeout=45.0) as client:
                    resp = client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data["choices"][0]["message"]["content"]
                        return json.loads(content)
                    elif resp.status_code == 429 and attempt < 2:
                        logger.warning(f"OpenRouter 429 rate limit/admission control. Retrying in 2.5s (attempt {attempt+1}/3)...")
                        time.sleep(2.5)
                        continue
                    logger.warning(
                        f"OpenRouter API call failed with status {resp.status_code}: {resp.text}"
                    )
                    return None
            except Exception as e:
                if attempt < 2:
                    time.sleep(2.0)
                    continue
                logger.warning(f"Error calling OpenRouter API: {e}")
                return None
        return None

    def _call_anthropic(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Optional[Dict[str, Any]]:
        """Direct Anthropic API fallback."""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }

        try:
            with httpx.Client(timeout=45.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["content"][0]["text"]
                    # Clean potential markdown wrapping
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.endswith("```"):
                        content = content[:-3]
                    return json.loads(content.strip())
                logger.warning(f"Anthropic API call failed: {resp.status_code} - {resp.text}")
                return None
        except Exception as e:
            logger.warning(f"Error calling Anthropic API: {e}")
            return None
