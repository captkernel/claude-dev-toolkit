"""Tests for the minimal A2A demo (written first, TDD).

These exercise three layers without opening real sockets:
  1. agent-card construction
  2. each agent's in-process message handler logic
  3. the orchestrator chaining Research -> Writer

The handlers are tested by calling the pure ``handle_message`` functions
directly. The orchestrator is tested against an injected transport so no
HTTP server needs to bind a port.
"""

import agent_card
import research_agent
import writer_agent
import orchestrator


# --------------------------------------------------------------------------- #
# 1. Agent card construction
# --------------------------------------------------------------------------- #
def test_build_card_has_required_fields():
    card = agent_card.build_card(
        name="Research Agent",
        url="http://localhost:8001",
        description="desc",
        skills=[{"id": "summarize_topic", "name": "Summarize Topic"}],
    )
    assert card["name"] == "Research Agent"
    assert card["url"] == "http://localhost:8001"
    assert card["description"] == "desc"
    assert isinstance(card["skills"], list)
    assert card["skills"][0]["id"] == "summarize_topic"


def test_card_is_json_serializable():
    import json

    card = agent_card.build_card(
        name="X", url="http://localhost:9", description="d", skills=[]
    )
    # must round-trip cleanly (it is published as JSON)
    assert json.loads(json.dumps(card)) == card


def test_well_known_path_constant():
    assert agent_card.AGENT_CARD_PATH == "/.well-known/agent-card.json"


def test_research_card_advertises_summarize_skill():
    card = research_agent.build_agent_card()
    assert card["name"] == "Research Agent"
    skill_ids = [s["id"] for s in card["skills"]]
    assert "summarize_topic" in skill_ids


def test_writer_card_advertises_rewrite_skill():
    card = writer_agent.build_agent_card()
    assert card["name"] == "Writer Agent"
    skill_ids = [s["id"] for s in card["skills"]]
    assert "rewrite_simple" in skill_ids


# --------------------------------------------------------------------------- #
# 2. Message handler logic (uses the default stub llm -> no API key needed)
# --------------------------------------------------------------------------- #
def test_research_handler_returns_text():
    result = research_agent.handle_message("transformers in AI")
    assert isinstance(result, str)
    assert result.strip() != ""
    # the stub should reflect the input topic somewhere
    assert "transformers in AI" in result


def test_writer_handler_returns_text():
    result = writer_agent.handle_message("Some dense summary text.")
    assert isinstance(result, str)
    assert result.strip() != ""
    assert "Some dense summary text." in result


def test_handler_uses_injected_llm():
    captured = {}

    def fake_llm(prompt: str) -> str:
        captured["prompt"] = prompt
        return "FAKE-OUTPUT"

    out = research_agent.handle_message("topic", llm=fake_llm)
    assert out == "FAKE-OUTPUT"
    # the system prompt + topic should both be present in what the llm saw
    assert "topic" in captured["prompt"]


def test_default_llm_runs_without_api_key():
    # the stub must be callable with no environment setup
    out = agent_card.stub_llm("hello prompt")
    assert isinstance(out, str)
    assert out != ""


# --------------------------------------------------------------------------- #
# 3. Orchestrator chaining (research output feeds writer input)
# --------------------------------------------------------------------------- #
def test_orchestrator_chains_agents_in_process():
    # A fake transport that routes /message calls to the real handlers and
    # serves the real cards, all without sockets.
    cards = {
        "http://research": research_agent.build_agent_card(),
        "http://writer": writer_agent.build_agent_card(),
    }

    def fake_get_card(base_url):
        return cards[base_url]

    def fake_send_message(base_url, text):
        if base_url == "http://research":
            return research_agent.handle_message(text)
        if base_url == "http://writer":
            return writer_agent.handle_message(text)
        raise AssertionError("unknown agent url")

    final = orchestrator.run(
        topic="transformers in AI",
        research_url="http://research",
        writer_url="http://writer",
        get_card=fake_get_card,
        send_message=fake_send_message,
    )

    # final output must be the writer's product, which was fed the research
    # summary (which itself mentions the topic) -> the topic survives the chain
    assert isinstance(final, str)
    assert "transformers in AI" in final


def test_orchestrator_reads_cards_for_discovery():
    seen = []

    def fake_get_card(base_url):
        seen.append(base_url)
        return {"name": base_url, "url": base_url, "skills": []}

    def fake_send_message(base_url, text):
        return f"[{base_url}] {text}"

    orchestrator.run(
        topic="t",
        research_url="http://r",
        writer_url="http://w",
        get_card=fake_get_card,
        send_message=fake_send_message,
    )
    # discovery must happen for BOTH agents before/while messaging
    assert "http://r" in seen
    assert "http://w" in seen
