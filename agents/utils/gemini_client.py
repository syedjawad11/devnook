"""
DevNook — Gemini Client
Shared utility for calling Gemini via Google AI API.
Used by content-team and tools-team agents.
"""

import os
import time
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def call_gemini(
    system: str,
    prompt: str,
    max_tokens: int = 4096,
    retries: int = 3,
    retry_delay: float = 10.0,
) -> str:
    """
    Call Gemini 2.5 Flash via Google AI API.

    Args:
        system: System prompt / persona context.
        prompt: User message / task description.
        max_tokens: Maximum tokens in the response.
        retries: Number of retry attempts on failure.
        retry_delay: Seconds to wait between retries.

    Returns:
        The model's text response.

    Raises:
        RuntimeError: If all retries are exhausted.
        EnvironmentError: If GEMINI_API_KEY is not set.
    """
    if not GEMINI_API_KEY:
        raise EnvironmentError(
            "GEMINI_API_KEY environment variable is not set. "
            "Export it before running this script."
        )

    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens},
    }

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(
                f"{API_URL}?key={GEMINI_API_KEY}",
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            print(f"  [Gemini] HTTP {status} on attempt {attempt}/{retries}")
            last_error = e
            if status in (401, 403):
                raise RuntimeError(f"Gemini auth error ({status}). Check your API key.") from e
            if status in (429, 503):
                wait = retry_delay * attempt * 2
                print(f"  [Gemini] Retryable error {status}. Waiting {wait}s...")
                time.sleep(wait)
                continue
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print(f"  [Gemini] Network error on attempt {attempt}/{retries}: {e}")
            last_error = e

        if attempt < retries:
            time.sleep(retry_delay * attempt)

    raise RuntimeError(
        f"Gemini call failed after {retries} attempts. Last error: {last_error}"
    )
