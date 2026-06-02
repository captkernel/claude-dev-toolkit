"""Writer Agent -- an A2A server that rewrites text simply.

Structurally identical to the Research Agent; only the prompt, the advertised
skill, the card identity, and the default port differ. The LLM call is the
same pluggable seam (offline ``stub_llm`` by default).

Run as a server:  python writer_agent.py [port]   (default 8002)
"""

from __future__ import annotations

from agent_card import build_card, stub_llm, LLM

SYSTEM_PROMPT = (
    "You are an explainer. Rewrite the given text as a punchy, "
    "beginner-friendly explanation a smart 15-year-old would enjoy. Keep it "
    "to 3-4 short sentences. Use plain words and one concrete analogy. No preamble."
)

DEFAULT_URL = "http://localhost:8002"


def build_agent_card(url: str = DEFAULT_URL) -> dict:
    return build_card(
        name="Writer Agent",
        url=url,
        description="Rewrites text into a punchy, beginner-friendly explanation.",
        skills=[
            {
                "id": "rewrite_simple",
                "name": "Rewrite Simply",
                "description": "Rewrites any text into a punchy, beginner-friendly explanation.",
                "tags": ["writing", "explainer"],
                "examples": ["Rewrite this dense paragraph so a beginner gets it"],
            }
        ],
    )


def handle_message(text: str, llm: LLM = stub_llm) -> str:
    """Pure handler: text in, rewrite out."""
    prompt = f"{SYSTEM_PROMPT}\n\nText: {text}"
    return llm(prompt)


def main() -> None:
    import sys
    from a2a_server import serve

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    card = build_agent_card(f"http://localhost:{port}")
    serve(card, handle_message, port=port)


if __name__ == "__main__":
    main()
