from utils.ui_utils import sanitize_text
import streamlit as st


def render_workflow_dashboard(workflow_steps):

    st.markdown(
        """

        <div style="
            margin-top:30px;
            margin-bottom:22px;
        ">

            <h2 style="
                margin:0;

                color:white;

                font-size:30px;
                font-weight:900;
            ">
                🧭 Workflow Engine
            </h2>

            <p style="
                margin-top:10px;

                color:#94a3b8;

                font-size:15px;

                line-height:1.8;
            ">
                Autonomous workflow execution, distributed orchestration, and realtime cognitive task routing
            </p>

        </div>

        """,
        unsafe_allow_html=True
    )

    if not workflow_steps:

        st.markdown(
            """

            <div style="
                position:relative;

                overflow:hidden;

                padding:28px;

                border-radius:30px;

                background:
                linear-gradient(
                    180deg,
                    rgba(15,23,42,0.96),
                    rgba(2,6,23,0.99)
                );

                border:
                1px solid rgba(255,255,255,0.05);

                backdrop-filter:blur(24px);
            ">

                <div style="
                    position:absolute;

                    width:180px;
                    height:180px;

                    border-radius:999px;

                    background:
                    rgba(124,58,237,0.10);

                    top:-80px;
                    right:-80px;

                    filter:blur(28px);
                "></div>

                <div style="
                    position:relative;
                    z-index:2;

                    display:flex;
                    align-items:center;

                    gap:18px;
                ">

                    <div style="
                        width:60px;
                        height:60px;

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

                        font-size:28px;

                        box-shadow:
                        0 0 24px rgba(124,58,237,0.35);
                    ">
                        🧭
                    </div>

                    <div>

                        <div style="
                            color:white;

                            font-size:19px;
                            font-weight:800;

                            margin-bottom:8px;
                        ">
                            No Workflow Activity
                        </div>

                        <div style="
                            color:#94a3b8;

                            font-size:14px;

                            line-height:1.8;
                        ">
                            HELIOS workflow orchestration systems are currently idle
                        </div>

                    </div>

                </div>

            </div>

            """,
            unsafe_allow_html=True
        )

        return

    for index, step in enumerate(workflow_steps):

        agent = sanitize_text(
            step.get("agent", "Unknown")
        )

        output = sanitize_text(
            step.get("output", "")
        )

        st.markdown(
            f"""

            <div style="
                position:relative;

                overflow:hidden;

                margin-bottom:24px;

                padding:28px;

                border-radius:32px;

                background:
                linear-gradient(
                    180deg,
                    rgba(15,23,42,0.96),
                    rgba(2,6,23,0.99)
                );

                border:
                1px solid rgba(255,255,255,0.05);

                backdrop-filter:blur(24px);

                box-shadow:
                0 12px 28px rgba(0,0,0,0.18);
            ">

                <div style="
                    position:absolute;

                    width:200px;
                    height:200px;

                    border-radius:999px;

                    background:
                    rgba(124,58,237,0.10);

                    top:-90px;
                    right:-90px;

                    filter:blur(30px);
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

                        gap:18px;

                        margin-bottom:24px;
                    ">

                        <div style="
                            display:flex;
                            align-items:center;

                            gap:18px;
                        ">

                            <div style="
                                width:64px;
                                height:64px;

                                border-radius:20px;

                                background:
                                linear-gradient(
                                    135deg,
                                    #7c3aed,
                                    #2563eb
                                );

                                display:flex;
                                align-items:center;
                                justify-content:center;

                                color:white;

                                font-size:24px;
                                font-weight:900;

                                box-shadow:
                                0 0 28px rgba(124,58,237,0.35);
                            ">
                                {index + 1}
                            </div>

                            <div>

                                <div style="
                                    color:white;

                                    font-size:20px;
                                    font-weight:900;

                                    margin-bottom:6px;
                                ">
                                    {agent}
                                </div>

                                <div style="
                                    color:#94a3b8;

                                    font-size:14px;
                                ">
                                    Autonomous execution node
                                </div>

                            </div>

                        </div>

                        <div style="
                            padding:9px 16px;

                            border-radius:999px;

                            background:
                            rgba(34,197,94,0.12);

                            border:
                            1px solid rgba(34,197,94,0.18);

                            display:flex;
                            align-items:center;

                            gap:8px;

                            color:#86efac;

                            font-size:12px;
                            font-weight:800;

                            letter-spacing:0.5px;
                        ">

                            <div style="
                                width:10px;
                                height:10px;

                                border-radius:999px;

                                background:#22c55e;

                                box-shadow:
                                0 0 14px #22c55e;
                            "></div>

                            EXECUTED

                        </div>

                    </div>

                    <div style="
                        padding:22px;

                        border-radius:24px;

                        background:
                        rgba(255,255,255,0.03);

                        border:
                        1px solid rgba(255,255,255,0.05);

                        overflow-x:auto;
                    ">

                        <div style="
                            color:#cbd5e1;

                            font-size:14px;

                            line-height:1.9;

                            overflow-wrap:break-word;

                            white-space:pre-wrap;
                        ">

                            {output}

                        </div>

                    </div>

                </div>

            </div>

            """,
            unsafe_allow_html=True
        )