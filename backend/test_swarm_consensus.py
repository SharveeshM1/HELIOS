from core.swarm_engine import build_consensus
from core.swarm_engine import build_consensus_block


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
