from collections import Counter

import streamlit as st

from components.ui import (
    esc,
    render_section_header
)
from core.source_library import (
    load_sources,
    source_stats
)


def _source_signal(source):

    content = str(
        source.get(
            "content",
            ""
        )
    )

    if source.get("status") != "Indexed":
        return "Pending"

    if len(content) >= 6000:
        return "Deep context"

    if len(content) >= 1400:
        return "Usable"

    if content:
        return "Brief"

    return "Needs text"


def _coverage_score(sources):

    if not sources:
        return 0

    indexed = [
        source
        for source in sources
        if source.get("status") == "Indexed"
    ]

    scoped = {
        str(source.get("scope", "project")).lower()
        for source in sources
    }

    typed = {
        str(source.get("type", "file")).lower()
        for source in sources
    }

    text_volume = sum(
        len(
            str(
                source.get(
                    "content",
                    ""
                )
            )
        )
        for source in indexed
    )

    score = min(
        45,
        len(indexed) * 9
    )
    score += min(
        25,
        text_volume // 900
    )
    score += min(
        15,
        len(scoped) * 5
    )
    score += min(
        15,
        len(typed) * 5
    )

    return min(
        100,
        int(score)
    )


def render_source_intelligence_panel():

    sources = load_sources()
    stats = source_stats()
    coverage = _coverage_score(
        sources
    )

    scope_counts = Counter(
        str(source.get("scope", "project"))
        for source in sources
    )

    type_counts = Counter(
        str(source.get("type", "FILE")).upper()
        for source in sources
    )

    sorted_sources = sorted(
        sources,
        key=lambda source: str(
            source.get(
                "updated_at",
                ""
            )
        ),
        reverse=True
    )

    source_rows = "".join(
        f"""
        <article class="helios-source-intel-row">
            <span>{esc(str(source.get("type", "FILE")).upper()[:6])}</span>
            <div>
                <strong>{esc(source.get("name", "source"))}</strong>
                <small>{esc(source.get("scope", "project"))} • {esc(source.get("updated_at", "not indexed yet"))}</small>
            </div>
            <em>{esc(_source_signal(source))}</em>
        </article>
        """
        for source in sorted_sources[:6]
    )

    if not source_rows:
        source_rows = """
        <article class="helios-source-intel-empty">
            <strong>No indexed sources yet</strong>
            <p>Upload a TXT, PY, or MD file to build the first source map.</p>
        </article>
        """

    scope_rows = "".join(
        f"<span>{esc(scope)} <b>{count}</b></span>"
        for scope, count in scope_counts.most_common(4)
    ) or "<span>Waiting <b>0</b></span>"

    type_rows = "".join(
        f"<span>{esc(source_type)} <b>{count}</b></span>"
        for source_type, count in type_counts.most_common(4)
    ) or "<span>None <b>0</b></span>"

    render_section_header(
        "Source Intelligence",
        "Indexed context, coverage, freshness, and retrieval readiness."
    )

    st.markdown(
        f"""
        <section class="helios-source-intel helios-motion-card">
            <div class="helios-source-intel-head">
                <div>
                    <span>Evidence Coverage</span>
                    <strong>{coverage}%</strong>
                </div>
                <div class="helios-source-intel-meter">
                    <i style="width:{coverage}%"></i>
                </div>
            </div>
            <div class="helios-source-intel-grid">
                <article>
                    <span>Total Sources</span>
                    <strong>{esc(stats.get("total_sources", 0))}</strong>
                </article>
                <article>
                    <span>Indexed</span>
                    <strong>{esc(stats.get("indexed_sources", 0))}</strong>
                </article>
                <article>
                    <span>Pending</span>
                    <strong>{esc(stats.get("pending_sources", 0))}</strong>
                </article>
                <article>
                    <span>Library Cap</span>
                    <strong>200</strong>
                </article>
            </div>
            <div class="helios-source-intel-split">
                <div class="helios-source-intel-list">
                    <div class="helios-source-intel-title">
                        <strong>Fresh Sources</strong>
                        <span>latest six</span>
                    </div>
                    {source_rows}
                </div>
                <aside class="helios-source-intel-aside">
                    <div>
                        <strong>Scopes</strong>
                        {scope_rows}
                    </div>
                    <div>
                        <strong>Types</strong>
                        {type_rows}
                    </div>
                </aside>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )
