import re
from typing import Dict
from typing import List

STOP_TERMS = {
    "about",
    "also",
    "and",
    "are",
    "can",
    "does",
    "for",
    "from",
    "has",
    "have",
    "how",
    "into",
    "its",
    "the",
    "this",
    "what",
    "when",
    "where",
    "which",
    "why",
    "with"
}


def extract_terms(
    text: str
) -> List[str]:
    return sorted(
        {
            term
            for term in re.findall(
                r"[a-z0-9_]{3,}",
                str(
                    text
                ).lower()
            )
            if term not in STOP_TERMS
        }
    )


def build_citations(
    evidence: List[Dict]
) -> List[Dict]:
    citations = []

    for index, item in enumerate(
        evidence,
        start=1
    ):
        citation_id = f"S{index}"
        match_terms = item.get(
            "match_terms",
            []
        )

        citations.append(
            {
                "id": citation_id,
                "source_id": item.get(
                    "id"
                ),
                "name": item.get(
                    "name",
                    f"Source {index}"
                ),
                "scope": item.get(
                    "scope",
                    "project"
                ),
                "snippet": item.get(
                    "snippet",
                    ""
                ),
                "match_terms": match_terms,
                "confidence": min(
                    1.0,
                    0.45
                    + (
                        len(
                            match_terms
                        )
                        * 0.12
                    )
                )
            }
        )

    return citations


def grounded_claims(
    title: str,
    citations: List[Dict]
) -> List[Dict]:
    claims = []

    for citation in citations:
        snippet = str(
            citation.get(
                "snippet",
                ""
            )
        ).strip()

        if not snippet:
            continue

        sentence = re.split(
            r"(?<=[.!?])\s+",
            snippet
        )[0][:220]

        claims.append(
            {
                "claim": sentence,
                "citations": [
                    citation["id"]
                ],
                "source": citation.get(
                    "name"
                )
            }
        )

    if not claims and citations:
        claims.append(
            {
                "claim": f"Indexed evidence exists for {title}.",
                "citations": [
                    citations[0]["id"]
                ],
                "source": citations[0].get(
                    "name"
                )
            }
        )

    return claims


def research_coverage(
    title: str,
    citations: List[Dict],
    source_stats: Dict
) -> Dict:
    query_terms = extract_terms(
        title
    )
    matched_terms = sorted(
        {
            term
            for citation in citations
            for term in citation.get(
                "match_terms",
                []
            )
        }
    )

    coverage_ratio = (
        round(
            len(
                matched_terms
            )
            / len(
                query_terms
            ),
            2
        )
        if query_terms
        else 1
    )
    grounded = bool(
        citations
    )
    enforced = grounded and coverage_ratio >= 0.5

    return {
        "query_terms": query_terms,
        "matched_terms": matched_terms,
        "unmatched_terms": [
            term
            for term in query_terms
            if term not in matched_terms
        ],
        "coverage_ratio": coverage_ratio,
        "citation_count": len(
            citations
        ),
        "grounded": grounded,
        "enforced": enforced,
        "answer_policy": "cite_or_refuse",
        "minimum_coverage_ratio": 0.5,
        **source_stats
    }


def cited_summary(
    title: str,
    citations: List[Dict],
    claims: List[Dict],
    coverage: Dict
) -> str:
    if not citations:
        return (
            "No indexed evidence matched this research request. "
            "HELIOS should not make source-backed claims until sources are added or the query is broadened."
        )

    if not coverage.get(
        "enforced",
        False
    ):
        missing = coverage.get(
            "unmatched_terms",
            []
        )
        return (
            "Indexed evidence was found, but coverage is too thin for a fully source-grounded answer. "
            f"Matched terms: {', '.join(coverage.get('matched_terms', [])[:8]) or 'none'}. "
            f"Unsupported terms: {', '.join(missing[:8]) or 'none'}. "
            "Add stronger sources or broaden the query before treating this as answered."
        )

    claim_lines = [
        f"- {claim['claim']} [{', '.join(claim['citations'])}]"
        for claim in claims[:4]
    ]
    missing = coverage.get(
        "unmatched_terms",
        []
    )
    missing_text = (
        f" Unmatched terms: {', '.join(missing[:8])}."
        if missing
        else " All major query terms were represented in matched source text."
    )

    return "\n".join(
        [
            f"Source-grounded brief for {title}:",
            *claim_lines,
            missing_text.strip()
        ]
    )


def build_grounded_research_artifact(
    title: str,
    evidence: List[Dict],
    source_stats: Dict
) -> Dict:
    citations = build_citations(
        evidence
    )
    claims = grounded_claims(
        title,
        citations
    )
    coverage = research_coverage(
        title,
        citations,
        source_stats
    )
    graph_nodes = [
        {
            "id": "query",
            "label": title or "Research query",
            "kind": "query"
        }
    ]
    graph_links = []
    for citation in citations:
        graph_nodes.append(
            {
                "id": citation["id"],
                "label": citation.get(
                    "name",
                    citation["id"]
                ),
                "kind": "source",
                "confidence": citation.get(
                    "confidence",
                    0
                )
            }
        )
        graph_links.append(
            {
                "from": "query",
                "to": citation["id"],
                "label": "supports",
                "terms": citation.get(
                    "match_terms",
                    []
                )
            }
        )
    for index, claim in enumerate(
        claims,
        start=1
    ):
        claim_id = f"C{index}"
        graph_nodes.append(
            {
                "id": claim_id,
                "label": claim["claim"],
                "kind": "claim"
            }
        )
        for citation_id in claim.get(
            "citations",
            []
        ):
            graph_links.append(
                {
                    "from": citation_id,
                    "to": claim_id,
                    "label": "grounds"
                }
            )

    return {
        "citations": citations,
        "claims": claims,
        "coverage": coverage,
        "enforcement": {
            "policy": coverage["answer_policy"],
            "grounded": coverage["grounded"],
            "enforced": coverage["enforced"],
            "coverage_ratio": coverage["coverage_ratio"],
            "minimum_coverage_ratio": coverage["minimum_coverage_ratio"],
            "unsupported_terms": coverage["unmatched_terms"]
        },
        "grounded_answer": cited_summary(
            title,
            citations,
            claims,
            coverage
        ),
        "graph": {
            "nodes": graph_nodes,
            "links": graph_links
        }
    }
