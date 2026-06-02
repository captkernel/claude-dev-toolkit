"""Agent-card construction + the pluggable LLM seam.

An *agent card* is a tiny JSON document every A2A agent publishes at the
fixed path ``/.well-known/agent-card.json``. It answers three questions:

  * who are you  -> ``name`` / ``description``
  * what can you do -> ``skills``
  * how do I reach you -> ``url`` (plus the protocol)

A caller reads the card first, so endpoints are never hard-coded in calling
logic -- that is the whole "discovery" trick of A2A.

This module also defines the *pluggable LLM seam*: ``stub_llm``. Every agent
calls an ``llm(prompt) -> str`` function; the default is this offline stub so
the entire system runs and the tests pass with NO API key. To use a real
model, pass your own ``llm`` (see ``make_groq_llm`` / ``make_anthropic_llm``
below, which are inert until you add the dependency + key).
"""

from __future__ import annotations

from typing import Callable, List, Dict, Any

# The fixed, well-known discovery path mandated by A2A.
AGENT_CARD_PATH = "/.well-known/agent-card.json"

# Type alias for the pluggable seam.
LLM = Callable[[str], str]


def build_card(
    name: str,
    url: str,
    description: str,
    skills: List[Dict[str, Any]],
    version: str = "1.0.0",
) -> Dict[str, Any]:
    """Return an agent card as a plain (JSON-serializable) dict.

    Kept deliberately small: a real A2A card (a2a-sdk) also carries
    ``capabilities``, ``supportedInterfaces``, input/output modes, etc.
    For a dependency-light demo, name + url + skills is the useful core.
    """
    return {
        "name": name,
        "description": description,
        "version": version,
        "url": url,
        # In a full A2A card the protocol lives under supportedInterfaces;
        # we keep a flat hint so the orchestrator stays trivial.
        "protocol": "JSONRPC-lite/HTTP",
        "skills": list(skills),
    }


# --------------------------------------------------------------------------- #
# The pluggable LLM seam
# --------------------------------------------------------------------------- #
def stub_llm(prompt: str) -> str:
    """Default, offline LLM. No network, no key -- templated echo.

    It returns the prompt's user payload verbatim so the data (the topic /
    the text being rewritten) still flows through the whole pipeline, which
    is what the tests assert on. Swap this out for a real model in prod.
    """
    return f"[stub-llm] {prompt.strip()}"


def make_groq_llm(model: str = "llama-3.3-70b-versatile") -> LLM:
    """Return a real Groq-backed ``llm(prompt)->str``.

    Inert until you ``pip install groq`` and set ``GROQ_API_KEY``. This is
    the single place to plug a real LLM for the Research/Writer agents.

        from groq import Groq            # pip install groq
        client = Groq()                  # reads GROQ_API_KEY from env

    See the tutorial: call ``load_dotenv()`` before constructing the client.
    """

    def _llm(prompt: str) -> str:  # pragma: no cover - needs network + key
        from groq import Groq  # imported lazily so the dep stays optional

        client = Groq()  # reads GROQ_API_KEY from the environment
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
        )
        return resp.choices[0].message.content

    return _llm


def make_anthropic_llm(model: str = "claude-3-5-haiku-latest") -> LLM:
    """Return a real Anthropic-backed ``llm(prompt)->str``.

    Inert until you ``pip install anthropic`` and set ``ANTHROPIC_API_KEY``.
    """

    def _llm(prompt: str) -> str:  # pragma: no cover - needs network + key
        import anthropic  # imported lazily so the dep stays optional

        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
        msg = client.messages.create(
            model=model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in msg.content if block.type == "text")

    return _llm
