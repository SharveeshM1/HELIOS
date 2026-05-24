"""
HELIOS Realtime Web Intelligence Layer

Lightweight DuckDuckGo-powered search utilities
for realtime intelligence retrieval.
"""

from typing import List
from typing import Dict
from typing import Any

try:
    from duckduckgo_search import DDGS
except ModuleNotFoundError:
    DDGS = None

# =========================================
# FORMAT SINGLE RESULT
# =========================================

def format_result(

    index: int,
    result: Dict[str, Any]

) -> str:

    title = str(

        result.get(
            "title",
            "Untitled Result"
        )

    ).strip()

    body = str(

        result.get(
            "body",
            "No summary available."
        )

    ).strip()

    link = str(

        result.get(
            "href",
            "No source URL"
        )

    ).strip()

    return f"""

## Result {index}

**Title:**  
{title}

**Summary:**  
{body}

**Source:**  
{link}

---

"""

# =========================================
# SEARCH WEB
# =========================================

def search_web(

    query: str,

    max_results: int = 5

) -> str:

    """
    Perform realtime web search
    using DuckDuckGo.
    """

    # =====================================
    # VALIDATION
    # =====================================

    if not query:

        return (
            "No search query received."
        )

    query = str(query).strip()

    if len(query) == 0:

        return (
            "Search query is empty."
        )

    if DDGS is None:

        return (
            "Realtime web search is unavailable because duckduckgo_search is not installed."
        )

    # =====================================
    # SEARCH EXECUTION
    # =====================================

    entries: List[str] = []

    try:

        with DDGS() as ddgs:

            results = ddgs.text(

                query,

                max_results=max_results
            )

            for index, result in enumerate(

                results,

                start=1
            ):

                formatted = format_result(

                    index,

                    result
                )

                entries.append(
                    formatted
                )

    # =====================================
    # ERROR HANDLING
    # =====================================

    except Exception:

        return (
            "Realtime web search failed."
        )

    # =====================================
    # EMPTY RESULTS
    # =====================================

    if not entries:

        return (
            "No realtime intelligence results found."
        )

    # =====================================
    # FINAL OUTPUT
    # =====================================

    final_output = f"""

# 🌐 HELIOS Web Intelligence

**Query:**  
{query}

**Results Retrieved:**  
{len(entries)}

---

{"".join(entries)}

# ✅ Realtime Intelligence Retrieval Complete

"""

    return final_output.strip()

# =========================================
# QUICK SEARCH
# =========================================

def quick_search(

    query: str

) -> str:

    """
    Lightweight search helper.
    """

    return search_web(

        query=query,

        max_results=3
    )

# =========================================
# HEALTH CHECK
# =========================================

def web_search_health():

    if DDGS is None:

        return {

            "status":
            "offline",

            "reason":
            "duckduckgo_search is not installed."
        }

    try:

        with DDGS() as ddgs:

            _ = list(

                ddgs.text(

                    "HELIOS AI",

                    max_results=1
                )
            )

        return {

            "status":
            "online",

            "provider":
            "DuckDuckGo"
        }

    except Exception:

        return {

            "status":
            "offline",

            "reason":
            "Search provider unavailable."
        }
