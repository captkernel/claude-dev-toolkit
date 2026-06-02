"""Orchestrator -- discovers both agents and chains them.

It contains NO AI logic. Its job is: discover (read each agent's card),
send (POST a topic to Research, pipe the result to Writer), print. It knows
the two agents only by URL -- everything else it learns from their cards at
runtime. That is the "agents hiring other agents" pattern.

The networking (``get_card`` / ``send_message``) is injected so the chaining
logic can be unit-tested in-process with no real sockets.

Run:  python orchestrator.py            (needs both agents already running)
"""

from __future__ import annotations

import json
import urllib.request
from typing import Callable, Dict, Any

from agent_card import AGENT_CARD_PATH

MESSAGE_PATH = "/message"

GetCard = Callable[[str], Dict[str, Any]]
SendMessage = Callable[[str, str], str]


# --------------------------------------------------------------------------- #
# Default HTTP transport (real sockets). Swappable for tests.
# --------------------------------------------------------------------------- #
def http_get_card(base_url: str) -> Dict[str, Any]:
    """Fetch and parse an agent's published card -- this is discovery."""
    with urllib.request.urlopen(base_url + AGENT_CARD_PATH, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_send_message(base_url: str, text: str) -> str:
    """POST a JSON-RPC-flavoured SendMessage and return the result text."""
    payload = json.dumps(
        {"method": "SendMessage", "params": {"text": text}, "id": 1}
    ).encode("utf-8")
    req = urllib.request.Request(
        base_url + MESSAGE_PATH,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body["result"]["text"]


# --------------------------------------------------------------------------- #
# The orchestration itself
# --------------------------------------------------------------------------- #
def run(
    topic: str,
    research_url: str,
    writer_url: str,
    get_card: GetCard = http_get_card,
    send_message: SendMessage = http_send_message,
    verbose: bool = False,
) -> str:
    """Discover both agents, chain topic -> research -> writer, return output."""

    def say(*a):
        if verbose:
            print(*a)

    # 1. Discover the Research agent by reading its card.
    research_card = get_card(research_url)
    say(f"Discovered: {research_card['name']} ({research_url})")

    # 2. Send the topic, get a summary.
    summary = send_message(research_url, topic)
    say("Research summary:\n  " + summary.replace("\n", "\n  "))

    # 3. Discover the Writer agent.
    writer_card = get_card(writer_url)
    say(f"Discovered: {writer_card['name']} ({writer_url})")

    # 4. Pipe the summary into the writer -- the chaining IS the orchestration.
    final = send_message(writer_url, summary)
    say("Final rewrite:\n  " + final.replace("\n", "\n  "))

    return final


def main() -> None:
    research_url = "http://localhost:8001"
    writer_url = "http://localhost:8002"
    topic = "Tell me about transformers in AI"

    print(f"Topic: {topic}\n")
    final = run(topic, research_url, writer_url, verbose=True)
    print("\n=== FINAL OUTPUT ===")
    print(final)


if __name__ == "__main__":
    main()
