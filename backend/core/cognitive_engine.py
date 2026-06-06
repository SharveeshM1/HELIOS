from datetime import datetime
from typing import Any
from typing import Dict
from typing import List

from api.ai_provider import generate_response
from agents.analytics_agent import run_analytics_agent
from agents.code_agent import run_code_agent
from agents.research_agent import run_research_agent
from core.agent_memory import remember_agent_result
from core.agent_memory import search_agent_memory
from core.agent_brain import think_and_decide
from core.memory import add_to_memory
from core.memory import get_memory_stats
from core.memory import get_recent_memory
from core.memory import load_memory
from core.memory import search_memory
from core.shared_bus import shared_bus
from core.task_planner import build_execution_plan
from memory.vector_memory import search_memory_records
from memory.vector_memory import store_memory


class CognitiveEngine:

    def __init__(self):

        self.last_trace: List[Dict[str, Any]] = []
        self.last_plan: List[Dict[str, str]] = []

    def execute(
        self,
        text,
        web_results: str = "",
        file_content: str = ""
    ):

        user_text = str(text).strip()

        if not user_text:

            return "Please provide a valid objective."

        self.last_trace = []

        memory = load_memory()
        memory_context = self._build_memory_context(
            memory,
            user_text
        )

        plan = build_execution_plan(
            user_text
        )

        self.last_plan = plan

        self._trace(
            "plan",
            "Task Planner",
            {
                "steps": plan
            }
        )

        agent_outputs = self._run_planned_agents(
            plan,
            user_text,
            web_results,
            file_content,
            memory_context
        )

        response = self._compose_final_response(
            user_text,
            memory_context,
            plan,
            agent_outputs
        )

        add_to_memory(
            memory,
            user_text,
            response
        )

        self._send_telemetry(
            user_text,
            response
        )

        return response

    def status(self) -> Dict[str, Any]:

        memory = load_memory()

        return {
            "status": "online",
            "engine": "CognitiveEngine",
            "plan": self.last_plan,
            "trace": self.last_trace,
            "memory": get_memory_stats(memory)
        }

    def _run_planned_agents(
        self,
        plan: List[Dict[str, str]],
        user_text: str,
        web_results: str,
        file_content: str,
        memory_context: str
    ) -> List[Dict[str, str]]:

        outputs = []

        for step in plan:

            agent_key = step.get(
                "agent",
                "research"
            )

            objective = step.get(
                "objective",
                "General intelligence analysis"
            )

            agent_prompt = f"""
Objective:
{objective}

User Request:
{user_text}

Agent Long-Term Memory:
{self._agent_memory_context(agent_key, user_text)}
"""

            try:

                if agent_key == "code":

                    output = run_code_agent(
                        agent_prompt,
                        file_content,
                        memory_context
                    )

                elif agent_key == "analytics":

                    output = run_analytics_agent(
                        agent_prompt,
                        web_results,
                        memory_context
                    )

                else:

                    output = run_research_agent(
                        agent_prompt,
                        web_results,
                        file_content,
                        memory_context
                    )

                decision = think_and_decide(
                    agent_key,
                    user_text
                )

                self._trace(
                    "agent",
                    agent_key,
                    {
                        "objective": objective,
                        "decision": decision
                    }
                )

            except Exception as error:

                output = f"""
[HELIOS AGENT ERROR]

Agent:
{agent_key}

Error:
{str(error)}
"""

                self._trace(
                    "agent_error",
                    agent_key,
                    {
                        "objective": objective,
                        "error": str(error)
                    }
                )

            outputs.append(
                {
                    "agent": agent_key,
                    "objective": objective,
                    "output": str(output)
                }
            )
            remember_agent_result(
                agent_key,
                objective,
                str(
                    output
                ),
                metadata={
                    "source": "cognitive_engine"
                }
            )

        return outputs

    def _compose_final_response(
        self,
        user_text: str,
        memory_context: str,
        plan: List[Dict[str, str]],
        agent_outputs: List[Dict[str, str]]
    ) -> str:

        agent_report = "\n\n".join(
            f"""
Agent:
{item["agent"]}

Objective:
{item["objective"]}

Output:
{item["output"]}
"""
            for item in agent_outputs
        )

        final_prompt = f"""
You are HELIOS Cognitive Engine.

Use the memory, plan, and specialist agent outputs to answer the user.

Rules:
- Give the user the actual result, not internal process chatter.
- Keep the response useful and direct.
- Mention concrete next actions only when they are relevant.
- Do not claim a tool or file changed unless the agent output says it did.

Conversation Memory:
{memory_context}

Execution Plan:
{plan}

Specialist Outputs:
{agent_report}

User Request:
{user_text}
"""

        try:

            response = generate_response(
                final_prompt
            )

            if response and not response.startswith(
                "[HELIOS AI ERROR]"
            ):

                self._trace(
                    "synthesis",
                    "Cognitive Engine",
                    {
                        "status": "completed"
                    }
                )

                return str(response).strip()

        except Exception as error:

            self._trace(
                "synthesis_error",
                "Cognitive Engine",
                {
                    "error": str(error)
                }
            )

        return agent_report.strip()

    def _build_memory_context(
        self,
        memory: List[Dict],
        user_text: str
    ) -> str:

        recent = get_recent_memory(
            memory,
            limit=6
        )

        matches = search_memory(
            memory,
            user_text
        )[:4]
        semantic_matches = search_memory_records(
            user_text,
            top_k=4
        )

        items = []

        for item in recent + matches:

            items.append(
                f"""
Timestamp:
{item.get("timestamp", "")}

User:
{item.get("user", "")}

Assistant:
{item.get("assistant", "")}
"""
            )

        for item in semantic_matches:
            items.append(
                f"""
Semantic Memory:
{item.get("text", "")}

Similarity:
{item.get("score", 0)}
"""
            )

        context = "\n---\n".join(items)

        self._trace(
            "memory",
            "Conversation Memory",
            {
                "recent": len(recent),
                "matches": len(matches),
                "semantic_matches": len(
                    semantic_matches
                )
            }
        )

        return context or "No prior conversation memory found."

    def _agent_memory_context(
        self,
        agent: str,
        query: str
    ) -> str:
        memories = search_agent_memory(
            agent,
            query,
            limit=4
        )
        return "\n---\n".join(
            str(
                item.get(
                    "text",
                    item.get(
                        "result",
                        ""
                    )
                )
            )
            for item in memories
        ) or "No prior agent-specific memory found."

    def _trace(
        self,
        stage: str,
        actor: str,
        payload: Dict[str, Any]
    ):

        self.last_trace.append(
            {
                "stage": stage,
                "actor": actor,
                "payload": payload,
                "timestamp": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }
        )

    def _send_telemetry(
        self,
        user_text: str,
        response: str
    ):

        try:

            store_memory(
                f"conversation:{datetime.now().timestamp()}",
                f"{user_text}\n\n{response}",
                metadata={
                    "kind": "conversation"
                }
            )
            shared_bus.send_message(
                "Cognitive Engine",
                "System",
                f"""
Cognitive execution completed.

Request:
{user_text[:300]}

Response:
{response[:500]}
"""
            )

        except Exception:

            pass
