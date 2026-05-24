import streamlit as st

from core.project_memory import (
    load_project_memory
)

from utils.ui_utils import (
    sanitize_text
)


# =========================================
# PROJECT MEMORY DASHBOARD
# =========================================

def render_project_memory():

    memory = load_project_memory()

    # =====================================
    # HEADER
    # =====================================

    st.markdown(
        """
        <div style="
            margin-top:28px;
            margin-bottom:20px;
        ">

            <h2 style="
                margin:0;
                color:white;
                font-size:26px;
                font-weight:800;
                letter-spacing:-0.4px;
            ">
                Project Memory
            </h2>

            <p style="
                margin-top:8px;
                color:#94a3b8;
                font-size:14px;
                line-height:1.7;
            ">
                Persistent neural memory and contextual recall
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================
    # EMPTY STATE
    # =====================================

    if not memory:

        st.markdown(
            """
            <div style="
                padding:22px;
                border-radius:24px;

                background:
                linear-gradient(
                    180deg,
                    rgba(15,23,42,0.78),
                    rgba(2,6,23,0.92)
                );

                border:
                1px solid rgba(255,255,255,0.06);

                backdrop-filter:blur(18px);

                color:#94a3b8;

                font-size:14px;

                line-height:1.8;

                box-shadow:
                0 10px 30px rgba(0,0,0,0.18);
            ">
                No project memories stored yet.
            </div>
            """,
            unsafe_allow_html=True
        )

        return

    # =====================================
    # RECENT MEMORIES
    # =====================================

    recent_memory = memory[-5:]

    for item in reversed(recent_memory):

        title = sanitize_text(
            item.get(
                "title",
                "Untitled Memory"
            )
        )

        summary = sanitize_text(
            item.get(
                "summary",
                ""
            )
        )

        st.markdown(
            f"""
            <div style="
                position:relative;
                overflow:hidden;

                border-radius:28px;

                margin-bottom:18px;

                padding:24px;

                background:
                linear-gradient(
                    180deg,
                    rgba(15,23,42,0.82),
                    rgba(2,6,23,0.94)
                );

                border:
                1px solid rgba(255,255,255,0.06);

                backdrop-filter:blur(24px);

                box-shadow:
                0 10px 40px rgba(0,0,0,0.22);

                transition:
                transform .25s ease,
                border .25s ease,
                box-shadow .25s ease;
            ">

                <div style="
                    position:absolute;

                    width:180px;
                    height:180px;

                    border-radius:999px;

                    background:
                    rgba(124,58,237,0.12);

                    top:-90px;
                    right:-90px;

                    filter:blur(22px);
                "></div>

                <div style="
                    position:absolute;

                    inset:0;

                    background:
                    linear-gradient(
                        135deg,
                        rgba(255,255,255,0.03),
                        transparent 45%
                    );

                    pointer-events:none;
                "></div>

                <div style="
                    position:relative;
                    z-index:2;

                    display:flex;
                    align-items:center;
                    justify-content:space-between;

                    gap:16px;
                    flex-wrap:wrap;

                    margin-bottom:18px;
                ">

                    <div style="
                        display:flex;
                        align-items:center;
                        gap:14px;
                    ">

                        <div style="
                            width:50px;
                            height:50px;

                            border-radius:18px;

                            background:
                            linear-gradient(
                                135deg,
                                #7c3aed,
                                #2563eb
                            );

                            display:flex;
                            align-items:center;
                            justify-content:center;

                            font-size:20px;

                            box-shadow:
                            0 0 24px rgba(124,58,237,0.35);
                        ">
                            MM
                        </div>

                        <div>

                            <div style="
                                color:white;

                                font-size:18px;

                                font-weight:700;

                                margin-bottom:5px;

                                letter-spacing:-0.3px;

                                overflow-wrap:break-word;
                                word-break:break-word;
                            ">
                                {title}
                            </div>

                            <div style="
                                color:#94a3b8;

                                font-size:13px;
                            ">
                                HELIOS contextual memory snapshot
                            </div>

                        </div>

                    </div>

                    <div style="
                        padding:7px 14px;

                        border-radius:999px;

                        background:
                        rgba(124,58,237,0.12);

                        border:
                        1px solid rgba(168,85,247,0.18);

                        color:#d8b4fe;

                        font-size:11px;

                        font-weight:700;

                        letter-spacing:0.6px;
                    ">
                        STORED
                    </div>

                </div>

                <div style="
                    position:relative;
                    z-index:2;

                    color:#cbd5e1;

                    line-height:1.95;

                    font-size:14px;

                    overflow-wrap:break-word;
                    word-break:break-word;

                    white-space:pre-wrap;
                ">
                    {summary}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )
