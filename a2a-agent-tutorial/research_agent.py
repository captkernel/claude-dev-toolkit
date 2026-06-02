"""Research Agent -- an A2A server that summarizes a topic.

Takes a topic, returns a short factual summary. The LLM call is pluggable:
by default it uses the offline ``stub_llm`` (no API key needed). Pass a real
``llm`` (e.g. ``agent_card.make_groq_llm()``) to do real summarization.

Run as a server:  python research_agent.py [port]   (default 8001)
"""

from __future__ import annotations

from agent_card import build_card, stub_llm, LLM

SYSTEM_PROMPT = (
    "You are a research assistant. Given a topic, write a tight, factual "
    "summary in 3-4 sentences. No preamble, no bullet points."
)

DEFAULT_URL = "http://localhost:8001"


def build_agent_card(url: str = DEFAULT_URL) -> dict:
    return build_card(
        name="Research Agent",
        url=url,
        description="Summarizes any topic into a short research brief.",
        skills=[
            {
                "id": "summarize_topic",
                "name": "Summarize Topic",
                "description": "Generates a concise 3-4 sentence research summary of any topic.",
                "tags": ["research", "summary"],
                "examples": ["Summarize transformers in AI"],
            }
        ],
    )


def handle_message(topic: str, llm: LLM = stub_llm) -> str:
    """Pure handler: topic in, summary out. No sockets -> trivially testable."""
    prompt = f"{SYSTEM_PROMPT}\n\nTopic: {topic}"
    return llm(prompt)


def main() -> None:
    import sys
    from a2a_server import serve

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    card = build_agent_card(f"http://localhost:{port}")
    # To use a real model, replace the default below, e.g.:
    #     from agent_card import make_groq_llm
    #     handler = lambda t: handle_message(t, llm=make_groq_llm())
    serve(card, handle_message, port=port)


if __name__ == "__main__":
    main()
