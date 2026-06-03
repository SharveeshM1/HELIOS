import re
from datetime import datetime
from typing import Dict
from typing import List


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
