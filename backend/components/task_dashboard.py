import streamlit as st
from utils.ui_utils import sanitize_text


def render_task_dashboard(tasks):

    st.markdown(
        """
        <div style="
            margin-top:22px;
            margin-bottom:20px;
        ">

            <div style="
                display:flex;
                align-items:center;
                justify-content:space-between;

                flex-wrap:wrap;
                gap:16px;
            ">

                <div>

                    <div style="
                        color:white;

                        font-size:28px;
                        font-weight:800;

                        margin-bottom:8px;
                    ">
                        Task Center
                    </div>

                    <div style="
                        color:#94a3b8;

                        font-size:14px;
                    ">
                        Autonomous execution monitoring and orchestration
                    </div>

                </div>

                <div style="
                    padding:10px 16px;

                    border-radius:16px;

                    background:
                    rgba(124,58,237,0.10);

                    border:
                    1px solid rgba(168,85,247,0.18);

                    color:#d8b4fe;

                    font-size:13px;
                    font-weight:700;
                ">
                    REALTIME PIPELINE
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================
    # EMPTY STATE
    # =====================================

    if not tasks:

        st.markdown(
            """
            <div style="
                padding:28px;

                border-radius:26px;

                background:
                linear-gradient(
                    180deg,
                    rgba(15,23,42,0.92),
                    rgba(2,6,23,0.95)
                );

                border:
                1px solid rgba(255,255,255,0.05);

                color:#94a3b8;

                text-align:center;

                font-size:15px;

                line-height:1.8;
            ">
                No active HELIOS tasks detected.
            </div>
            """,
            unsafe_allow_html=True
        )

        return

    # =====================================
    # TASKS
    # =====================================

    for task in reversed(tasks[-6:]):

        title = sanitize_text(
            task.get("title", "Untitled Task")
        )

        agent = sanitize_text(
            task.get("agent", "Unknown Agent")
        )

        status = sanitize_text(
            task.get("status", "running")
        ).lower()

        progress = int(
            task.get("progress", 68)
        )

        if status == "completed":

            status_color = "#22c55e"
            status_bg = "rgba(34,197,94,0.12)"

        elif status == "failed":

            status_color = "#ef4444"
            status_bg = "rgba(239,68,68,0.12)"

        else:

            status_color = "#f59e0b"
            status_bg = "rgba(245,158,11,0.12)"

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
                    rgba(15,23,42,0.94),
                    rgba(2,6,23,0.98)
                );

                border:
                1px solid rgba(255,255,255,0.05);

                backdrop-filter:blur(24px);

                box-shadow:
                0 12px 30px rgba(0,0,0,0.20);
            ">

                <div style="
                    position:absolute;

                    width:180px;
                    height:180px;

                    border-radius:999px;

                    background:
                    rgba(124,58,237,0.08);

                    top:-90px;
                    right:-90px;

                    filter:blur(28px);
                "></div>

                <div style="
                    position:relative;
                    z-index:2;
                ">

                    <div style="
                        display:flex;
                        align-items:center;
                        justify-content:space-between;

                        flex-wrap:wrap;

                        gap:16px;

                        margin-bottom:20px;
                    ">

                        <div>

                            <div style="
                                color:white;

                                font-size:20px;
                                font-weight:800;

                                margin-bottom:8px;
                            ">
                                {title}
                            </div>

                            <div style="
                                color:#94a3b8;

                                font-size:14px;
                            ">
                                Executed by
                                <span style="
                                    color:#d8b4fe;
                                    font-weight:700;
                                ">
                                    {agent}
                                </span>
                            </div>

                        </div>

                        <div style="
                            padding:10px 16px;

                            border-radius:999px;

                            background:{status_bg};

                            border:
                            1px solid rgba(255,255,255,0.06);

                            display:flex;
                            align-items:center;

                            gap:10px;

                            color:white;

                            font-size:13px;
                            font-weight:700;
                        ">

                            <div style="
                                width:11px;
                                height:11px;

                                border-radius:999px;

                                background:{status_color};

                                box-shadow:
                                0 0 14px {status_color};
                            "></div>

                            {status.upper()}

                        </div>

                    </div>

                    <div style="
                        width:100%;
                        height:10px;

                        border-radius:999px;

                        overflow:hidden;

                        background:
                        rgba(255,255,255,0.05);

                        margin-bottom:12px;
                    ">

                        <div style="
                            height:100%;
                            width:{progress}%;

                            border-radius:999px;

                            background:
                            linear-gradient(
                                90deg,
                                {status_color},
                                #2563eb
                            );

                            box-shadow:
                            0 0 20px {status_color};
                        "></div>

                    </div>

                    <div style="
                        display:flex;
                        justify-content:space-between;
                        align-items:center;

                        color:#94a3b8;

                        font-size:12px;
                    ">

                        <div>
                            HELIOS execution pipeline active
                        </div>

                        <div>
                            {progress}% complete
                        </div>

                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )
