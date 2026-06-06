import json
import os
import re
from datetime import datetime
from typing import Dict
from typing import List

from api.ai_provider import generate_response as generate_ai_response


ROUTES = {
    "research": {
        "agent": "research",
        "priority": 1,
        "keywords": {
            "research": 4,
            "analyze": 3,
            "citation": 4,
            "source": 3,
            "trend": 3,
            "market": 3,
            "future": 2,
            "compare": 2,
            "evidence": 4
        },
        "objective": "Gather source-grounded evidence and synthesize cited findings."
    },
    "code": {
        "agent": "code",
        "priority": 2,
        "keywords": {
            "build": 4,
            "code": 4,
            "develop": 3,
            "fix": 5,
            "debug": 5,
            "patch": 5,
            "backend": 3,
            "frontend": 3,
            "api": 3,
            "test": 3,
            "commit": 3
        },
        "objective": "Inspect implementation targets, apply bounded changes, and verify results."
    },
    "analytics": {
        "agent": "analytics",
        "priority": 3,
        "keywords": {
            "optimize": 4,
            "performance": 4,
            "metric": 3,
            "analytics": 4,
            "monitor": 3,
            "observability": 5,
            "latency": 4,
            "scale": 3,
            "failure": 2
        },
        "objective": "Measure execution health, surface risks, and recommend observability improvements."
    },
    "voice": {
        "agent": "voice",
        "priority": 4,
        "keywords": {
            "voice": 5,
            "audio": 4,
            "microphone": 4,
            "speech": 4,
            "realtime": 3
        },
        "objective": "Validate realtime voice flow, transcript handling, and assistant behavior."
    },
    "planning": {
        "agent": "planning",
        "priority": 5,
        "keywords": {
            "plan": 5,
            "planning": 5,
            "roadmap": 4,
            "sequence": 3,
            "prioritize": 4,
            "workflow": 3
        },
        "objective": "Decompose the objective into ordered, risk-aware execution steps."
    },
    "knowledge": {
        "agent": "memory",
        "priority": 6,
        "keywords": {
            "memory": 5,
            "knowledge": 5,
            "recall": 4,
            "project brain": 5,
            "semantic": 4,
            "index": 3
        },
        "objective": "Retrieve project knowledge and connect relevant memory signals."
    },
    "swarm": {
        "agent": "collaboration",
        "priority": 7,
        "keywords": {
            "swarm": 5,
            "debate": 5,
            "consensus": 5,
            "collaborate": 4,
            "critique": 4,
            "vote": 3
        },
        "objective": "Run parallel agent proposals, critique them, and converge on consensus."
    }
}

PHRASE_SIGNALS = {
    "research": {
        "what is": 2,
        "find out": 3,
        "source grounded": 5,
        "pros and cons": 3
    },
    "code": {
        "does not work": 4,
        "failing test": 5,
        "implement feature": 4,
        "edit file": 5
    },
    "analytics": {
        "how fast": 4,
        "failure rate": 5,
        "system health": 4,
        "slow request": 5
    },
    "voice": {
        "talk to": 3,
        "spoken response": 4,
        "realtime assistant": 4
    },
    "planning": {
        "break down": 4,
        "execution plan": 5,
        "next steps": 3
    },
    "knowledge": {
        "project brain": 5,
        "remember this": 4,
        "what do we know": 4
    },
    "swarm": {
        "multi agent": 5,
        "agent debate": 5,
        "reach consensus": 5
    }
}

RISK_TERMS = {
    "delete",
    "deploy",
    "production",
    "security",
    "auth",
    "payment",
    "database",
    "migration",
    "secret",
    "token",
    "commit"
}


def tokenize(
    text: str
) -> List[str]:
    return re.findall(
        r"[a-z0-9_]+",
        str(
            text
        ).lower()
    )


def route_objective(
    objective: str
) -> Dict:
    objective_text = str(
        objective
    ).lower()
    tokens = tokenize(
        objective
    )
    token_set = set(
        tokens
    )
    route_scores = []

    for route, config in ROUTES.items():
        score = sum(
            weight
            for term, weight in config["keywords"].items()
            if term in token_set
        )
        phrase_matches = [
            phrase
            for phrase in PHRASE_SIGNALS.get(
                route,
                {}
            )
            if phrase in objective_text
        ]
        score += sum(
            PHRASE_SIGNALS[
                route
            ][phrase]
            for phrase in phrase_matches
        )

        if score:
            route_scores.append(
                {
                    "route": route,
                    "agent": config["agent"],
                    "score": score,
                    "priority": config["priority"],
                    "matched_terms": [
                        term
                        for term in config["keywords"]
                        if term in token_set
                    ]
                    + phrase_matches,
                    "objective": config["objective"]
                }
            )

    if not route_scores:
        route_scores.append(
            {
                "route": "research",
                "agent": "research",
                "score": 1,
                "priority": 1,
                "matched_terms": [],
                "objective": "Clarify the request and gather enough context to route safely."
            }
        )

    route_scores.sort(
        key=lambda item: (
            -item["score"],
            item["priority"]
        )
    )

    top_score = max(
        item["score"]
        for item in route_scores
    )
    total_score = sum(
        item["score"]
        for item in route_scores
    ) or 1
    risk_terms = sorted(
        term
        for term in token_set
        if term in RISK_TERMS
    )

    tasks = [
        {
            "agent": item["agent"],
            "route": item["route"],
            "objective": item["objective"],
            "priority": index + 1,
            "confidence": round(
                item["score"] / total_score,
                2
            ),
            "matched_terms": item["matched_terms"]
        }
        for index, item in enumerate(
            route_scores
        )
    ]

    return {
        "objective": str(
            objective
        ),
        "primary_route": route_scores[0]["route"],
        "confidence": round(
            top_score / total_score,
            2
        ),
        "risk": {
            "level": "high"
            if len(
                risk_terms
            )
            >= 2
            else "medium"
            if risk_terms
            else "low",
            "terms": risk_terms
        },
        "ambiguous": len(
            route_scores
        )
        > 1
        and (
            route_scores[0]["score"]
            == route_scores[1]["score"]
        ),
        "tasks": tasks,
        "routing_trace": route_scores,
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }


def model_assisted_route_objective(
    objective: str,
    *,
    enabled: bool | None = None
) -> Dict:
    baseline = route_objective(
        objective
    )
    use_model = (
        enabled
        if enabled is not None
        else os.getenv(
            "HELIOS_MODEL_ASSISTED_PLANNING",
            "false"
        ).strip().lower()
        in {
            "1",
            "true",
            "yes",
            "on"
        }
    )
    if not use_model:
        return {
            **baseline,
            "planning_source": "rules",
            "model_assisted": False
        }

    prompt = f"""
You are the HELIOS planning router.
Refine this rule-based route plan for the user objective.
Return JSON only with this shape:
{{
  "primary_route": "one of {', '.join(ROUTES)}",
  "routes": ["ordered route ids"],
  "reason": "short explanation"
}}

Objective:
{objective}

Rule-based plan:
{json.dumps(baseline, ensure_ascii=False)}
"""
    try:
        raw = str(
            generate_ai_response(
                prompt
            )
            or ""
        ).strip()
        if raw.startswith(
            "```"
        ):
            raw = re.sub(
                r"^```(?:json)?\s*|\s*```$",
                "",
                raw,
                flags=re.IGNORECASE
            )
        proposal = json.loads(
            raw
        )
        routes = [
            route
            for route in proposal.get(
                "routes",
                []
            )
            if route in ROUTES
        ]
        primary = proposal.get(
            "primary_route"
        )
        if primary in ROUTES and primary not in routes:
            routes.insert(
                0,
                primary
            )
        if not routes:
            raise ValueError(
                "Model proposal did not contain valid routes."
            )
        baseline_tasks = {
            task["route"]: task
            for task in baseline.get(
                "tasks",
                []
            )
        }
        tasks = []
        for index, route in enumerate(
            routes
        ):
            task = baseline_tasks.get(
                route,
                {
                    "agent": ROUTES[
                        route
                    ][
                        "agent"
                    ],
                    "route": route,
                    "objective": ROUTES[
                        route
                    ][
                        "objective"
                    ],
                    "confidence": 0.5,
                    "matched_terms": []
                }
            )
            tasks.append(
                {
                    **task,
                    "priority": index + 1
                }
            )
        return {
            **baseline,
            "primary_route": routes[
                0
            ],
            "tasks": tasks,
            "planning_source": "model_assisted",
            "model_assisted": True,
            "model_reason": str(
                proposal.get(
                    "reason",
                    ""
                )
            )[:500]
        }
    except Exception as error:
        return {
            **baseline,
            "planning_source": "rules_fallback",
            "model_assisted": False,
            "model_error": str(
                error
            )[:500]
        }
