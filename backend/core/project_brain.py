from typing import Dict
from typing import List

from core import memory
from core import project_memory
from core.mission_ledger import latest_missions
from core.mission_ledger import mission_stats
from core.source_library import load_sources
from core.source_library import source_stats
from core.runtime_store import load_semantic_memories
from memory.execution_memory import execution_stats
from memory.execution_memory import get_execution_events


def _node(
    node_id: str,
    label: str,
    kind: str,
    weight: int,
    detail: str = ""
) -> Dict:
    return {
        "id": node_id,
        "label": label,
        "kind": kind,
        "weight": weight,
        "detail": detail
    }


def build_project_brain(
    limit: int = 8
) -> Dict:
    conversations = memory.load_memory()
    memory_stats = memory.get_memory_stats(
        conversations
    )
    project_stats = project_memory.get_project_memory_stats()
    recent_projects = project_memory.get_recent_projects(
        limit
    )
    sources = load_sources()[-limit:]
    missions = latest_missions()[:limit]
    executions = get_execution_events(
        limit=limit,
        event_type="tool_event"
    )
    semantic_memories = load_semantic_memories()[
        -limit:
    ]

    nodes: List[Dict] = [
        _node(
            "brain",
            "Project Brain",
            "core",
            10,
            "Live map of memory, sources, missions, and execution."
        ),
        _node(
            "memory",
            "Conversation Memory",
            "memory",
            memory_stats.get(
                "total_conversations",
                0
            ),
            f"{memory_stats.get('total_conversations', 0)} saved conversation(s)."
        ),
        _node(
            "sources",
            "Source Library",
            "source",
            source_stats().get(
                "indexed_sources",
                0
            ),
            "Indexed project knowledge."
        ),
        _node(
            "missions",
            "Mission Ledger",
            "mission",
            mission_stats().get(
                "total_events",
                0
            ),
            "Recent mission activity."
        ),
        _node(
            "execution",
            "Execution Ledger",
            "execution",
            execution_stats().get(
                "tool_events",
                0
            ),
            "Tool calls, attempts, failures, and durations."
        ),
        _node(
            "semantic",
            "Semantic Memory",
            "memory",
            len(
                semantic_memories
            ),
            "Vector-ranked project knowledge."
        ),
    ]

    links = [
        {
            "from": "brain",
            "to": "memory",
            "label": "recalls"
        },
        {
            "from": "brain",
            "to": "sources",
            "label": "grounds"
        },
        {
            "from": "brain",
            "to": "missions",
            "label": "plans"
        },
        {
            "from": "brain",
            "to": "semantic",
            "label": "recalls"
        },
        {
            "from": "missions",
            "to": "execution",
            "label": "runs"
        },
    ]

    for item in recent_projects:
        node_id = f"project:{item.get('id')}"
        nodes.append(
            _node(
                node_id,
                str(
                    item.get(
                        "title",
                        "Project memory"
                    )
                )[:80],
                "project",
                2,
                str(
                    item.get(
                        "summary",
                        ""
                    )
                )[:180]
            )
        )
        links.append(
            {
                "from": "memory",
                "to": node_id,
                "label": "project"
            }
        )

    for item in sources:
        node_id = f"source:{item.get('id')}"
        nodes.append(
            _node(
                node_id,
                str(
                    item.get(
                        "name",
                        "Source"
                    )
                )[:80],
                "source",
                1,
                str(
                    item.get(
                        "scope",
                        "project"
                    )
                )
            )
        )
        links.append(
            {
                "from": "sources",
                "to": node_id,
                "label": "indexed"
            }
        )

    for item in missions:
        node_id = f"mission:{item.get('id')}"
        nodes.append(
            _node(
                node_id,
                str(
                    item.get(
                        "title",
                        "Mission"
                    )
                )[:80],
                "mission",
                int(
                    item.get(
                        "event_count",
                        1
                    )
                    or 1
                ),
                str(
                    item.get(
                        "status",
                        ""
                    )
                )
            )
        )
        links.append(
            {
                "from": "missions",
                "to": node_id,
                "label": str(
                    item.get(
                        "stage",
                        "mission"
                    )
                )
            }
        )

    for item in executions[-limit:]:
        node_id = f"execution:{item.get('id')}"
        nodes.append(
            _node(
                node_id,
                str(
                    item.get(
                        "tool",
                        "tool"
                    )
                ),
                "execution",
                1,
                str(
                    item.get(
                        "status",
                        ""
                    )
                )
            )
        )
        links.append(
            {
                "from": "execution",
                "to": node_id,
                "label": "tool"
            }
        )

    for item in semantic_memories:
        node_id = f"semantic:{item.get('id')}"
        nodes.append(
            _node(
                node_id,
                str(
                    item.get(
                        "text",
                        "Semantic memory"
                    )
                )[:80],
                "memory",
                1,
                str(
                    item.get(
                        "metadata",
                        {}
                    )
                )[:180]
            )
        )
        links.append(
            {
                "from": "semantic",
                "to": node_id,
                "label": "vector"
            }
        )

    return {
        "nodes": nodes,
        "links": links,
        "stats": {
            "memory": memory_stats,
            "project_memory": project_stats,
            "sources": source_stats(),
            "missions": mission_stats(),
            "execution": execution_stats()
        },
        "summary": {
            "total_nodes": len(
                nodes
            ),
            "total_links": len(
                links
            ),
            "health": "mapped"
            if nodes
            else "empty"
        }
    }
