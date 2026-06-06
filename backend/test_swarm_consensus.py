from core.swarm_engine import build_consensus
from core.swarm_engine import build_consensus_block
from core import swarm_engine


def test_swarm_consensus_builds_debate_and_steps():
    consensus = build_consensus(
        [
            {
                "agent": "Research Agent",
                "output": "Use cited sources before final claims.",
                "status": "completed"
            },
            {
                "agent": "Code Agent",
                "output": "Patch target files and run backend tests.",
                "status": "completed"
            },
            {
                "agent": "Analytics Agent",
                "output": "Track latency, retries, and failures.",
                "status": "completed"
            }
        ]
    )

    assert len(
        consensus["proposals"]
    ) == 3
    assert consensus["confidence"] == 1
    assert consensus["debate"][0]["critiques"]
    assert consensus["consensus_steps"]


def test_swarm_consensus_block_contains_report_sections():
    block = build_consensus_block(
        {
            "confidence": 0.67,
            "proposals": [
                {
                    "agent": "Code Agent",
                    "focus": "implementation",
                    "proposal": "Run tests."
                }
            ],
            "debate": [
                {
                    "agent": "Code Agent",
                    "critiques": [
                        "Needs source support."
                    ]
                }
            ],
            "consensus_steps": [
                "Verify and report."
            ]
        }
    )

    assert "Swarm Debate + Consensus" in block
    assert "Run tests." in block
    assert "Verify and report." in block


def test_structured_swarm_runs_proposal_and_review_rounds(
    monkeypatch
):
    monkeypatch.setattr(
        swarm_engine,
        "execute_agent",
        lambda name, fn, *args: {
            "agent": name,
            "output": f"{name} proposal with concrete next steps.",
            "status": "completed",
            "duration": 0
        }
    )

    artifact = swarm_engine.run_swarm_artifact(
        "Debate the implementation"
    )

    assert len(
        artifact["agents"]
    ) == 3
    assert len(
        artifact["reviews"]
    ) == 3
    assert len(
        artifact["consensus"]["rounds"]
    ) == 2
