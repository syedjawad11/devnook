"""
DevNook — LLM Router
Central routing module. All LLM calls go through route() — no agent
imports API clients directly.

Supported task types and their targets:
  frontend_dev  → Anthropic: claude-sonnet-4-20250514
  tool_builder  → Anthropic: claude-sonnet-4-20250514
  writer        → Anthropic: claude-sonnet-4-5
  qa            → Anthropic: claude-haiku-4-5-20251001
  keyword       → Gemini:    gemini-2.5-flash
  planner       → Gemini:    gemini-2.5-flash
  seo           → Gemini:    gemini-2.5-flash
  analytics     → Gemini:    gemini-2.5-flash
"""

import os
import time
import requests
from dataclasses import dataclass
from typing import Optional

import anthropic as _anthropic_sdk

# ---------------------------------------------------------------------------
# Response type
# ---------------------------------------------------------------------------

@dataclass
class LLMResponse:
    text: str
    model_used: str          # actual model used (may differ from requested if fallback hit)
    fallback_triggered: bool
    input_tokens: int
    output_tokens: int

    @property
    def estimated_cost_usd(self) -> float:
        return _estimate_cost(self.model_used, self.input_tokens, self.output_tokens)


# ---------------------------------------------------------------------------
# Cost rates (USD per token)
# ---------------------------------------------------------------------------

_COST_RATES: dict[str, dict[str, float]] = {
    "claude-sonnet-4-5":         {"input": 3.00 / 1_000_000, "output": 15.00 / 1_000_000},
    "claude-haiku-4-5-20251001": {"input": 0.80 / 1_000_000, "output":  4.00 / 1_000_000},
    "gemini-2.5-flash":          {"input": 0.0,               "output":  0.0},
    "gemini-2.0-flash-001":      {"input": 0.0,               "output":  0.0},
}


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    rates = _COST_RATES.get(model, {"input": 0.0, "output": 0.0})
    return round(input_tokens * rates["input"] + output_tokens * rates["output"], 6)


# ---------------------------------------------------------------------------
# Routing table
# ---------------------------------------------------------------------------

_ROUTING: dict[str, tuple[str, str]] = {
    "frontend_dev": ("anthropic", "claude-sonnet-4-5"),
    "tool_builder": ("anthropic", "claude-sonnet-4-5"),
    "writer":       ("anthropic", "claude-sonnet-4-5"),
    "qa":           ("anthropic", "claude-haiku-4-5-20251001"),
    "keyword":      ("anthropic", "claude-haiku-4-5-20251001"),
    "planner":      ("anthropic", "claude-haiku-4-5-20251001"),
    "seo":          ("anthropic", "claude-haiku-4-5-20251001"),
    "analytics":    ("anthropic", "claude-haiku-4-5-20251001"),
}

_GEMINI_FALLBACK_MODEL = "gemini-2.0-flash-001"


# ---------------------------------------------------------------------------
# Gemini internals (raw requests — established pattern)
# ---------------------------------------------------------------------------

_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


def _call_gemini(model: str, system: str, prompt: str, max_tokens: int) -> tuple[str, int, int]:
    """
    Returns (text, input_tokens, output_tokens).
    Raises on failure — caller handles retry/fallback.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY is not set.")

    url = f"{_GEMINI_BASE_URL}/{model}:generateContent?key={api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens},
    }

    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"]
    usage = data.get("usageMetadata", {})
    input_tokens = usage.get("promptTokenCount", 0)
    output_tokens = usage.get("candidatesTokenCount", 0)

    return text, input_tokens, output_tokens


def _route_gemini(model: str, system: str, prompt: str, max_tokens: int) -> LLMResponse:
    """
    Retry schedule: attempt 1 immediate, attempt 2 after 30s, attempt 3 after 60s.
    On third consecutive failure: wait 90s then try fallback model once.
    """
    time.sleep(4)  # Respect free tier 15 RPM limit
    retry_delays = [30, 60]  # waits between attempts 1→2 and 2→3
    last_error: Optional[Exception] = None

    for attempt_idx in range(3):
        attempt_num = attempt_idx + 1
        try:
            text, in_tok, out_tok = _call_gemini(model, system, prompt, max_tokens)
            return LLMResponse(
                text=text,
                model_used=model,
                fallback_triggered=False,
                input_tokens=in_tok,
                output_tokens=out_tok,
            )
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            print(f"  [Gemini/{model}] HTTP {status} on attempt {attempt_num}/3")
            if status in (401, 403):
                raise RuntimeError(
                    f"Gemini auth error ({status}). Check GEMINI_API_KEY."
                ) from e
            last_error = e
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print(f"  [Gemini/{model}] Network error on attempt {attempt_num}/3: {e}")
            last_error = e

        if attempt_idx < 2:
            wait = retry_delays[attempt_idx]
            print(f"  [Gemini] Waiting {wait}s before retry...")
            time.sleep(wait)

    # All 3 attempts failed — fallback after 90s
    print(
        f"  [Gemini] 3 consecutive failures on {model}. "
        f"Waiting 90s then falling back to {_GEMINI_FALLBACK_MODEL}..."
    )
    time.sleep(90)

    try:
        text, in_tok, out_tok = _call_gemini(
            _GEMINI_FALLBACK_MODEL, system, prompt, max_tokens
        )
        return LLMResponse(
            text=text,
            model_used=_GEMINI_FALLBACK_MODEL,
            fallback_triggered=True,
            input_tokens=in_tok,
            output_tokens=out_tok,
        )
    except Exception as e:
        raise RuntimeError(
            f"Gemini call failed after 3 attempts on {model} and fallback to "
            f"{_GEMINI_FALLBACK_MODEL} also failed. Last error: {last_error}"
        ) from e


# ---------------------------------------------------------------------------
# Anthropic internals (official SDK, lazy singleton)
# ---------------------------------------------------------------------------

_anthropic_client: Optional[_anthropic_sdk.Anthropic] = None


def _get_anthropic_client() -> _anthropic_sdk.Anthropic:
    """Lazy singleton — does not require ANTHROPIC_API_KEY at import time."""
    global _anthropic_client
    if _anthropic_client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY is not set.")
        _anthropic_client = _anthropic_sdk.Anthropic(api_key=api_key)
    return _anthropic_client


def _call_anthropic(model: str, system: str, prompt: str, max_tokens: int) -> tuple[str, int, int]:
    """
    Returns (text, input_tokens, output_tokens).
    Raises anthropic.APIStatusError on HTTP errors — caller handles retry.
    """
    client = _get_anthropic_client()
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    text = message.content[0].text
    input_tokens = message.usage.input_tokens
    output_tokens = message.usage.output_tokens
    return text, input_tokens, output_tokens


def _route_anthropic(model: str, system: str, prompt: str, max_tokens: int) -> LLMResponse:
    """
    Retry only on HTTP 529 (overload) and connection errors.
    Delays: 5s / 10s / 20s between attempts. No fallback model.
    """
    retry_delays = [5, 10, 20]
    last_error: Optional[Exception] = None

    for attempt_idx in range(3):
        attempt_num = attempt_idx + 1
        try:
            text, in_tok, out_tok = _call_anthropic(model, system, prompt, max_tokens)
            return LLMResponse(
                text=text,
                model_used=model,
                fallback_triggered=False,
                input_tokens=in_tok,
                output_tokens=out_tok,
            )
        except _anthropic_sdk.APIStatusError as e:
            print(f"  [Anthropic/{model}] HTTP {e.status_code} on attempt {attempt_num}/3")
            if e.status_code == 529:
                last_error = e
                if attempt_idx < 2:
                    wait = retry_delays[attempt_idx]
                    print(f"  [Anthropic] Overload. Waiting {wait}s before retry...")
                    time.sleep(wait)
            else:
                # Auth, bad request, etc. — do not retry
                raise RuntimeError(
                    f"Anthropic call failed ({e.status_code}): {e.message}"
                ) from e
        except _anthropic_sdk.APIConnectionError as e:
            print(f"  [Anthropic/{model}] Connection error on attempt {attempt_num}/3: {e}")
            last_error = e
            if attempt_idx < 2:
                wait = retry_delays[attempt_idx]
                print(f"  [Anthropic] Waiting {wait}s before retry...")
                time.sleep(wait)

    raise RuntimeError(
        f"Anthropic call failed after 3 attempts on {model}. Last error: {last_error}"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def route(
    task_type: str,
    system: str,
    prompt: str,
    max_tokens: int = 4096,
) -> LLMResponse:
    """
    Central entry point for all LLM calls in DevNook.

    Args:
        task_type:  One of the keys in _ROUTING. Determines provider and model.
        system:     System prompt / persona context.
        prompt:     User message / task.
        max_tokens: Maximum response tokens (default 4096).

    Returns:
        LLMResponse with .text, .model_used, .fallback_triggered,
        .input_tokens, .output_tokens, .estimated_cost_usd.

    Raises:
        ValueError:       Unknown task_type.
        RuntimeError:     All retry/fallback attempts exhausted.
        EnvironmentError: Required API key missing.
    """
    if task_type not in _ROUTING:
        valid = ", ".join(sorted(_ROUTING.keys()))
        raise ValueError(f"Unknown task_type '{task_type}'. Valid types: {valid}")

    provider, model = _ROUTING[task_type]

    if provider == "gemini":
        return _route_gemini(model, system, prompt, max_tokens)
    elif provider == "anthropic":
        return _route_anthropic(model, system, prompt, max_tokens)
    else:
        raise RuntimeError(f"Unknown provider '{provider}' in routing table.")


# ---------------------------------------------------------------------------
# Cost summary utility (for pipeline run reporting)
# ---------------------------------------------------------------------------

def print_cost_summary(responses: list[tuple[str, LLMResponse]]) -> None:
    """
    Print a formatted cost summary for a pipeline run.

    Args:
        responses: List of (agent_name, LLMResponse) tuples collected during the run.

    Example:
        results = []
        r = route("writer", system, prompt)
        results.append(("writer_agent", r))
        print_cost_summary(results)
    """
    print("\n── Cost Summary ────────────────────────────────")
    total_cost = 0.0
    total_in = 0
    total_out = 0

    for agent_name, resp in responses:
        cost = resp.estimated_cost_usd
        total_cost += cost
        total_in += resp.input_tokens
        total_out += resp.output_tokens
        fallback_flag = " [FALLBACK]" if resp.fallback_triggered else ""
        print(
            f"  {agent_name:<20} {resp.model_used}{fallback_flag}"
            f"  in={resp.input_tokens:,} out={resp.output_tokens:,}"
            f"  ${cost:.4f}"
        )

    print(f"  {'TOTAL':<20} in={total_in:,} out={total_out:,}  ${total_cost:.4f}")
    print("────────────────────────────────────────────────\n")
