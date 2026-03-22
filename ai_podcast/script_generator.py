"""
Script Generator Module
Generates multi-speaker podcast scripts using an LLM.
Output format: structured chunks with speaker labels for TTS.
"""

import re
from abc import ABC, abstractmethod

from config import LLM_MODEL, LLM_PROVIDER, OPENAI_API_KEY, OPENAI_BASE_URL


# --- Script format: list of {"speaker": "Host"|"Guest"|..., "text": "..."}
SCRIPT_PROMPT = """You are a podcast scriptwriter. Generate a podcast script on the topic below.

Rules:
- Use exactly 2 speakers: HOST and GUEST
- Format each line as: SPEAKER: text
- Keep each line under 2 sentences for natural TTS pacing
- Aim for a conversational, engaging tone
- Script should be approximately {approx_words} words
- End with a clear outro

Topic: {topic}

Generate the script now. Use only "HOST:" and "GUEST:" as speaker labels."""


def parse_script(raw: str) -> list[dict]:
    """
    Parse LLM output into structured chunks.
    Expects lines like: HOST: Hello and welcome...
    Returns list of {"speaker": str, "text": str}
    """
    chunks = []
    lines = raw.strip().split("\n")
    current_speaker = None
    current_text = []

    for line in lines:
        line = line.strip()
        if not line:
            if current_speaker and current_text:
                chunks.append({
                    "speaker": current_speaker,
                    "text": " ".join(current_text).strip()
                })
                current_text = []
            continue

        # Match "SPEAKER: text" pattern
        match = re.match(r"^(HOST|GUEST)\s*:\s*(.*)$", line, re.IGNORECASE)
        if match:
            if current_speaker and current_text:
                chunks.append({
                    "speaker": current_speaker,
                    "text": " ".join(current_text).strip()
                })
            current_speaker = match.group(1).upper()
            current_text = [match.group(2).strip()] if match.group(2).strip() else []
        elif current_speaker:
            current_text.append(line)

    if current_speaker and current_text:
        chunks.append({
            "speaker": current_speaker,
            "text": " ".join(current_text).strip()
        })

    return chunks


class LLMBackend(ABC):
    """Abstract base for LLM backends. Swap implementations easily."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass


class OllamaBackend(LLMBackend):
    """Uses local Ollama for script generation."""

    def __init__(self, model: str = LLM_MODEL):
        self.model = model

    def generate(self, prompt: str) -> str:
        import ollama
        response = ollama.generate(model=self.model, prompt=prompt)
        return response.get("response", "")


class OpenAIBackend(LLMBackend):
    """Uses OpenAI or compatible API (e.g. DeepInfra, together.ai)."""

    def __init__(
        self,
        model: str = LLM_MODEL,
        api_key: str = OPENAI_API_KEY,
        base_url: str = OPENAI_BASE_URL,
    ):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""


def get_llm() -> LLMBackend:
    """Factory: returns configured LLM backend based on config."""
    if LLM_PROVIDER.lower() == "ollama":
        return OllamaBackend(LLM_MODEL)
    elif LLM_PROVIDER.lower() == "openai":
        return OpenAIBackend(LLM_MODEL, OPENAI_API_KEY, OPENAI_BASE_URL)
    raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")


def generate_script(topic: str, approx_minutes: int = 10) -> list[dict]:
    """
    Generate a multi-speaker podcast script for the given topic.
    approx_minutes: target length (affects word count ~150 wpm).
    Returns list of {"speaker": str, "text": str}.
    """
    approx_words = approx_minutes * 150  # ~150 words per minute
    prompt = SCRIPT_PROMPT.format(topic=topic, approx_words=approx_words)
    llm = get_llm()
    raw = llm.generate(prompt)
    return parse_script(raw)
