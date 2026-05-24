from datetime import datetime
import re

# =====================================
# AGENT KEYWORDS
# =====================================

AGENT_KEYWORDS = {

    "Code Intelligence":[

        "bug",
        "error",
        "fix",
        "code",
        "python",
        "flutter",
        "react",
        "debug",
        "optimize",
        "optimization",
        "algorithm",
        "backend",
        "frontend",
        "api",
        "app",
        "database",
        "deploy",
        "deployment",
        "build",
        "streamlit",
        "css",
        "html",
        "javascript",
        "docker",
        "fastapi",
        "ui",
        "ux",
        "architecture"
    ],

    "Research Center":[

        "research",
        "analyze",
        "analysis",
        "future",
        "technology",
        "trend",
        "market",
        "ai",
        "comparison",
        "compare",
        "explain",
        "study",
        "innovation",
        "future scope",
        "deep dive",
        "llm",
        "machine learning",
        "startup"
    ],

    "System Analytics":[

        "analytics",
        "performance",
        "metrics",
        "system",
        "gpu",
        "memory",
        "monitoring",
        "statistics",
        "optimization",
        "usage",
        "latency",
        "telemetry",
        "cpu",
        "throughput",
        "bottleneck",
        "scalability"
    ],

    "Voice AI":[

        "talk",
        "voice",
        "speak",
        "conversation",
        "assistant",
        "microphone",
        "audio",
        "listen",
        "speech",
        "tts",
        "transcribe"
    ]
}

# =====================================
# CLEAN QUERY
# =====================================

def normalize_query(text):

    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    return text


# =====================================
# DETECT BEST AGENT
# =====================================

def detect_best_agent(user_query):

    query = normalize_query(
        user_query
    )

    scores = {}

    # =================================
    # SCORE AGENTS
    # =================================

    for agent, keywords in (
        AGENT_KEYWORDS.items()
    ):

        score = 0

        for keyword in keywords:

            keyword = keyword.lower()

            if keyword in query:

                # weighted scoring
                score += len(
                    keyword.split()
                )

        scores[agent] = score

    # =================================
    # SELECT BEST
    # =================================

    best_agent = max(
        scores,
        key=scores.get
    )

    # =================================
    # FALLBACK
    # =================================

    if scores[best_agent] <= 0:

        return "Research Center"

    return best_agent


# =====================================
# ROUTING TELEMETRY
# =====================================

def routing_report(user_query):

    agent = detect_best_agent(
        user_query
    )

    normalized = normalize_query(
        user_query
    )

    return {

        "query":
        user_query,

        "normalized_query":
        normalized,

        "selected_agent":
        agent,

        "timestamp":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "status":
        "ROUTED"
    }