import re
from datetime import datetime

import streamlit as st

try:
    import markdown  # type: ignore
except ModuleNotFoundError:
    markdown = None

from components.ui import (
    esc,
    render_command_shell,
    render_empty_state
)
from utils.ui_utils import sanitize_text


def clean_ai_response(text):

    text = str(text)

    text = re.sub(
        r"```html",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```",
        "",
        text
    )

    text = re.sub(
        r"<script.*?>.*?</script>",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    text = re.sub(
        r"<style.*?>.*?</style>",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    return text.strip()


def markdown_to_safe_html(text):

    escaped = sanitize_text(text)

    if markdown is None:

        return escaped.replace(
            "\n",
            "<br>"
        )

    return markdown.markdown(
        escaped.replace(
            "\n",
            "  \n"
        )
    )


def render_safe_markdown(text):

    st.markdown(
        markdown_to_safe_html(text),
        unsafe_allow_html=True
    )


def _rerun_app():

    rerun = getattr(
        st,
        "rerun",
        None
    )

    if rerun is None:

        rerun = getattr(
            st,
            "experimental_rerun",
            None
        )

    if rerun is not None:

        rerun()


def _compact_text(text, limit=140):

    clean = re.sub(
        r"\s+",
        " ",
        str(text or "")
    ).strip()

    if len(clean) <= limit:

        return clean

    return clean[: limit - 1].rstrip() + "..."


def _chat_title(chat):

    return _compact_text(
        chat.get("user", "Untitled conversation"),
        72
    ) or "Untitled conversation"


def _chat_kind(chat):

    combined = (
        f"{chat.get('user', '')} {chat.get('assistant', '')}"
    ).lower()

    if any(token in combined for token in ("error", "failed", "ollama", "api key", "provider")):

        return "Errors"

    if any(token in combined for token in ("code", "python", "function", "backend", "frontend", "css")):

        return "Code"

    if any(token in combined for token in ("voice", "mic", "audio", "transcript")):

        return "Voice"

    if any(token in combined for token in ("research", "summarize", "source", "quantum", "what is")):

        return "Research"

    return "General"


def _chat_timestamp(chat):

    return str(
        chat.get(
            "timestamp",
            "No timestamp"
        )
    )


def _matches_filter(chat, query, mode):

    combined = (
        f"{chat.get('user', '')} {chat.get('assistant', '')}"
    ).lower()

    if query and query.lower() not in combined:

        return False

    if mode == "All":

        return True

    if mode == "Today":

        return _chat_timestamp(chat).startswith(
            datetime.now().strftime("%Y-%m-%d")
        )

    return _chat_kind(chat) == mode


def render_chat_history(chat_history):

    total_items = len(chat_history)
    latest_user = (
        chat_history[-1].get("user", "No prompt stored.")
        if chat_history
        else "No prompt stored."
    )

    render_command_shell(
        title="Chat History",
        subtitle="A dedicated recall archive for your conversations with HELIOS.",
        kicker="MEMORY ARCHIVE",
        status="MEMORY • RECALL READY",
        icon="memory",
        tabs=[
            "Latest",
            "Memory",
            "Recall"
        ],
        metrics=[
            {
                "label": "User Turns",
                "value": total_items
            },
            {
                "label": "AI Turns",
                "value": total_items
            },
            {
                "label": "Indexed",
                "value": len(chat_history)
            },
            {
                "label": "Mode",
                "value": "Vault"
            }
        ]
    )

    if not chat_history:

        render_empty_state(
            "No conversations stored yet."
        )

        return

    indexed_history = [
        {
            "index": index,
            "turn": index + 1,
            "chat": chat,
            "kind": _chat_kind(chat)
        }
        for index, chat in enumerate(chat_history)
    ]

    if "helios_history_selected_index" not in st.session_state:

        st.session_state["helios_history_selected_index"] = len(chat_history) - 1

    st.markdown(
        f"""
        <section class="helios-memory-vault helios-motion-card">
            <div class="helios-vault-sigil">◴</div>
            <div>
                <span>Latest Signal</span>
                <strong>{esc(latest_user)}</strong>
                <p>Search stored turns, inspect replies, export memory, or replay a past prompt into the reactor.</p>
            </div>
            <em>{total_items} saved turns</em>
        </section>
        """,
        unsafe_allow_html=True
    )

    controls = st.columns(
        [2.4, .9, .9, .9],
        gap="small"
    )

    with controls[0]:

        query = st.text_input(
            "Search chat history",
            key="helios_history_query",
            placeholder="Search prompts, replies, errors, code notes...",
            label_visibility="collapsed"
        )

    with controls[1]:

        mode = st.selectbox(
            "Filter",
            [
                "All",
                "Today",
                "Errors",
                "Code",
                "Voice",
                "Research",
                "General"
            ],
            key="helios_history_filter",
            label_visibility="collapsed"
        )

    with controls[2]:

        order = st.selectbox(
            "Order",
            [
                "Newest first",
                "Oldest first"
            ],
            key="helios_history_order",
            label_visibility="collapsed"
        )

    with controls[3]:

        density = st.selectbox(
            "Density",
            [
                "Compact",
                "Detailed"
            ],
            key="helios_history_density",
            label_visibility="collapsed"
        )

    filtered = [
        item
        for item in indexed_history
        if _matches_filter(
            item["chat"],
            query,
            mode
        )
    ]

    if order == "Newest first":

        filtered = list(
            reversed(filtered)
        )

    if not filtered:

        render_empty_state(
            "No memory records match that search."
        )

        return

    valid_indices = {
        item["index"]
        for item in filtered
    }

    if st.session_state["helios_history_selected_index"] not in valid_indices:

        st.session_state["helios_history_selected_index"] = filtered[0]["index"]

    selected_chat = chat_history[
        st.session_state["helios_history_selected_index"]
    ]

    st.markdown(
        f"""
        <section class="helios-vault-metrics">
            <div><span>Visible</span><strong>{len(filtered)}</strong></div>
            <div><span>Errors</span><strong>{sum(1 for item in indexed_history if item["kind"] == "Errors")}</strong></div>
            <div><span>Code</span><strong>{sum(1 for item in indexed_history if item["kind"] == "Code")}</strong></div>
            <div><span>Selected</span><strong>Turn {st.session_state["helios_history_selected_index"] + 1}</strong></div>
        </section>
        """,
        unsafe_allow_html=True
    )

    left, right = st.columns(
        [0.36, 0.64],
        gap="medium"
    )

    with left:

        item_lookup = {
            item["index"]: item
            for item in filtered
        }

        st.markdown(
            f"""
            <section class="helios-session-rail">
                <div class="helios-session-rail-head">
                    <span>Scroll Timeline</span>
                    <strong>{len(filtered)} visible memories</strong>
                    <p>Use search above, then scroll the recall stream without moving the inspector.</p>
                </div>
            </section>
            """,
            unsafe_allow_html=True
        )

        latest_index = max(
            item["index"]
            for item in filtered
        )

        if st.button(
            "Jump to latest",
            key="helios_history_jump_latest",
            use_container_width=True
        ):

            st.session_state["helios_history_selected_index"] = latest_index
            _rerun_app()

        def _format_memory_option(index):

            item = item_lookup.get(
                index
            )

            if item is None:

                return f"Turn {index + 1}"

            chat = item["chat"]
            preview = (
                _compact_text(
                    chat.get(
                        "assistant",
                        ""
                    ),
                    56
                )
                if density == "Detailed"
                else ""
            )
            timestamp = _chat_timestamp(
                chat
            )
            time_label = (
                timestamp[5:16]
                if len(timestamp) >= 16
                else timestamp
            )

            label = (
                f"T{item['turn']} · {item['kind']} · "
                f"{_compact_text(_chat_title(chat), 36)}"
            )

            if preview:

                label = f"{label} · {preview}"

            return f"{label} · {time_label}"

        timeline_indices = [
            item["index"]
            for item in filtered
        ]

        st.markdown(
            """
            <div class="helios-memory-scroll-frame">
            """,
            unsafe_allow_html=True
        )

        with st.container(
            height=640,
            key="helios_memory_scroll_container",
            border=False
        ):

            selected_index = st.radio(
                "Memory records",
                options=timeline_indices,
                index=(
                    timeline_indices.index(
                        st.session_state["helios_history_selected_index"]
                    )
                    if st.session_state["helios_history_selected_index"] in timeline_indices
                    else 0
                ),
                format_func=_format_memory_option,
                key=(
                    "helios_history_record_picker_"
                    f"{len(filtered)}_{mode}_{order}_{density}_{abs(hash(query))}"
                ),
                label_visibility="collapsed"
            )

        st.markdown(
            """
            </div>
            """,
            unsafe_allow_html=True
        )

        if selected_index != st.session_state["helios_history_selected_index"]:

            st.session_state["helios_history_selected_index"] = selected_index
            selected_chat = chat_history[
                selected_index
            ]

        selected_item = next(
            (
                item
                for item in filtered
                if item["index"] == st.session_state["helios_history_selected_index"]
            ),
            filtered[0]
        )

        selected_preview = selected_item["chat"]

        st.markdown(
            f"""
            <section class="helios-session-focus">
                <span>{esc(selected_item["kind"])} • Turn {selected_item["turn"]}</span>
                <strong>{esc(_chat_title(selected_preview))}</strong>
                <p>{esc(_compact_text(selected_preview.get("assistant", ""), 180))}</p>
                <em>{esc(_chat_timestamp(selected_preview))}</em>
            </section>
            """,
            unsafe_allow_html=True
        )

    with right:

        assistant_clean = clean_ai_response(
            selected_chat.get(
                "assistant",
                ""
            )
        )

        user_clean = selected_chat.get(
            "user",
            ""
        )

        st.markdown(
            f"""
            <section class="helios-memory-detail helios-motion-card">
                <div class="helios-memory-detail-head">
                    <div>
                        <span>{esc(_chat_kind(selected_chat))} Memory</span>
                        <strong>{esc(_chat_title(selected_chat))}</strong>
                        <em>{esc(_chat_timestamp(selected_chat))}</em>
                    </div>
                    <b>Turn {st.session_state["helios_history_selected_index"] + 1}</b>
                </div>
                <div class="helios-memory-thread">
                    <article class="user">
                        <span>You</span>
                        <div>{esc(user_clean).replace("\n", "<br>")}</div>
                    </article>
                    <article class="ai">
                        <span>HELIOS</span>
                        <div>{markdown_to_safe_html(assistant_clean)}</div>
                    </article>
                </div>
            </section>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="helios-memory-actions">
            """,
            unsafe_allow_html=True
        )

        action_cols = st.columns(
            3,
            gap="small"
        )

        with action_cols[0]:

            st.download_button(
                "Export memory",
                data=(
                    f"# HELIOS Memory Turn {st.session_state['helios_history_selected_index'] + 1}\n\n"
                    f"Timestamp: {_chat_timestamp(selected_chat)}\n\n"
                    f"## You\n{user_clean}\n\n"
                    f"## HELIOS\n{assistant_clean}\n"
                ),
                file_name=f"helios-memory-turn-{st.session_state['helios_history_selected_index'] + 1}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with action_cols[1]:

            if st.button(
                "Replay prompt",
                key="helios_history_replay",
                use_container_width=True
            ):

                st.session_state["helios_prefill_prompt"] = user_clean
                st.session_state["helios_toolbar_message"] = "Prompt copied into recall buffer."

        with action_cols[2]:

            st.download_button(
                "Export all",
                data="\n\n---\n\n".join(
                    [
                        f"# Turn {item['turn']}\n\n"
                        f"Timestamp: {_chat_timestamp(item['chat'])}\n\n"
                        f"## You\n{item['chat'].get('user', '')}\n\n"
                        f"## HELIOS\n{clean_ai_response(item['chat'].get('assistant', ''))}"
                        for item in filtered
                    ]
                ),
                file_name="helios-filtered-memory.md",
                mime="text/markdown",
                use_container_width=True
            )

        st.markdown(
            """
            </div>
            """,
            unsafe_allow_html=True
        )
