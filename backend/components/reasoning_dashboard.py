import streamlit as st


def render_reasoning_dashboard():

    st.markdown(
        """

        <div style="
            position:relative;

            overflow:hidden;

            padding:38px;

            border-radius:34px;

            background:
            linear-gradient(
                180deg,
                rgba(15,23,42,0.98),
                rgba(2,6,23,0.99)
            );

            border:
            1px solid rgba(255,255,255,0.05);

            backdrop-filter:blur(24px);

            margin-bottom:30px;
        ">

            <div style="
                position:absolute;

                width:260px;
                height:260px;

                border-radius:999px;

                background:
                rgba(124,58,237,0.12);

                top:-120px;
                right:-100px;

                filter:blur(40px);
            "></div>

            <div style="
                position:relative;
                z-index:2;

                display:flex;
                align-items:center;
                justify-content:space-between;

                flex-wrap:wrap;

                gap:30px;
            ">

                <div>

                    <div style="
                        display:inline-flex;
                        align-items:center;
                        gap:10px;

                        padding:8px 16px;

                        border-radius:999px;

                        background:
                        rgba(124,58,237,0.12);

                        border:
                        1px solid rgba(168,85,247,0.18);

                        margin-bottom:22px;
                    ">

                        <div style="
                            width:10px;
                            height:10px;

                            border-radius:999px;

                            background:#22c55e;

                            box-shadow:
                            0 0 14px #22c55e;
                        "></div>

                        <span style="
                            color:#d8b4fe;

                            font-size:13px;
                            font-weight:800;

                            letter-spacing:0.5px;
                        ">
                            HELIOS REASONING CORE
                        </span>

                    </div>

                    <h1 style="
                        margin:0;

                        color:white;

                        font-size:52px;
                        font-weight:900;

                        line-height:1.05;

                        letter-spacing:-1px;
                    ">
                        Recursive <br/>
                        Reasoning Engine
                    </h1>

                    <p style="
                        margin-top:22px;

                        max-width:760px;

                        color:#94a3b8;

                        font-size:16px;

                        line-height:1.9;
                    ">
                        HELIOS performs recursive cognitive analysis, autonomous self-reflection, multi-stage inference expansion, reasoning refinement, and advanced self-improving execution orchestration.
                    </p>

                </div>

                <div style="
                    width:210px;
                    height:210px;

                    border-radius:44px;

                    background:
                    radial-gradient(
                        circle at top,
                        rgba(168,85,247,0.55),
                        rgba(37,99,235,0.12)
                    );

                    border:
                    1px solid rgba(255,255,255,0.08);

                    display:flex;
                    align-items:center;
                    justify-content:center;

                    backdrop-filter:blur(22px);

                    box-shadow:
                    0 0 60px rgba(124,58,237,0.30);
                ">

                    <div style="
                        font-size:84px;
                    ">
                        🧠
                    </div>

                </div>

            </div>

        </div>

        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """

        <div style="
            margin-top:8px;
            margin-bottom:20px;
        ">

            <h2 style="
                margin:0;

                color:white;

                font-size:30px;
                font-weight:900;
            ">
                ⚡ Cognitive Capabilities
            </h2>

            <p style="
                margin-top:10px;

                color:#94a3b8;

                font-size:15px;

                line-height:1.8;
            ">
                Advanced recursive cognition and autonomous reasoning infrastructure
            </p>

        </div>

        """,
        unsafe_allow_html=True
    )

    capabilities = [

        {
            "icon":"🔁",
            "title":"Recursive Optimization",
            "desc":"Iteratively improves reasoning quality and output refinement"
        },

        {
            "icon":"🧠",
            "title":"Self Critique",
            "desc":"Analyzes internal logic and critiques generated solutions"
        },

        {
            "icon":"⚡",
            "title":"Inference Expansion",
            "desc":"Performs deep multi-step reasoning chains autonomously"
        },

        {
            "icon":"📈",
            "title":"Adaptive Improvement",
            "desc":"Continuously optimizes cognitive execution strategies"
        }
    ]

    cols = st.columns(2)

    for index, item in enumerate(capabilities):

        with cols[index % 2]:

            st.markdown(
                f"""

                <div style="
                    position:relative;

                    overflow:hidden;

                    min-height:240px;

                    margin-bottom:22px;

                    padding:26px;

                    border-radius:30px;

                    background:
                    linear-gradient(
                        180deg,
                        rgba(15,23,42,0.98),
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
                    ">

                        <div style="
                            display:flex;
                            align-items:center;
                            justify-content:space-between;

                            margin-bottom:24px;
                        ">

                            <div style="
                                font-size:34px;
                            ">
                                {item['icon']}
                            </div>

                            <div style="
                                padding:7px 14px;

                                border-radius:999px;

                                background:
                                rgba(124,58,237,0.12);

                                border:
                                1px solid rgba(168,85,247,0.16);

                                color:#d8b4fe;

                                font-size:11px;
                                font-weight:800;

                                letter-spacing:0.5px;
                            ">
                                ACTIVE
                            </div>

                        </div>

                        <div style="
                            color:white;

                            font-size:22px;
                            font-weight:900;

                            margin-bottom:14px;
                        ">
                            {item['title']}
                        </div>

                        <div style="
                            color:#94a3b8;

                            font-size:15px;

                            line-height:1.9;
                        ">
                            {item['desc']}
                        </div>

                    </div>

                </div>

                """,
                unsafe_allow_html=True
            )

    st.markdown(
        """

        <div style="
            margin-top:10px;
            margin-bottom:20px;
        ">

            <h2 style="
                margin:0;

                color:white;

                font-size:30px;
                font-weight:900;
            ">
                📡 Reasoning Telemetry
            </h2>

            <p style="
                margin-top:10px;

                color:#94a3b8;

                font-size:15px;

                line-height:1.8;
            ">
                Realtime recursive cognition infrastructure and execution health
            </p>

        </div>

        """,
        unsafe_allow_html=True
    )

    telemetry = [

        "Recursive inference engine online",

        "Multi-pass cognition operational",

        "Autonomous refinement active",

        "Self-critique systems stable",

        "Reasoning orchestration healthy"
    ]

    for item in telemetry:

        st.markdown(
            f"""

            <div style="
                position:relative;

                overflow:hidden;

                margin-bottom:16px;

                padding:22px;

                border-radius:26px;

                background:
                linear-gradient(
                    180deg,
                    rgba(15,23,42,0.98),
                    rgba(2,6,23,0.99)
                );

                border:
                1px solid rgba(255,255,255,0.05);

                display:flex;
                align-items:center;

                gap:16px;
            ">

                <div style="
                    width:12px;
                    height:12px;

                    border-radius:999px;

                    background:#22c55e;

                    box-shadow:
                    0 0 16px #22c55e;
                "></div>

                <div style="
                    color:white;

                    font-size:15px;
                    font-weight:700;
                ">
                    {item}
                </div>

            </div>

            """,
            unsafe_allow_html=True
        )