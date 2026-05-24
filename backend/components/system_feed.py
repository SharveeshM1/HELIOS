import streamlit as st


def render_system_feed():

    st.markdown(
        """
        <div style="
            margin-top:34px;
            margin-bottom:20px;
        ">

            <h2 style="
                margin:0;

                color:white;

                font-size:30px;
                font-weight:900;
            ">
                📡 Live Infrastructure Feed
            </h2>

            <p style="
                margin-top:10px;

                color:#94a3b8;

                font-size:15px;

                line-height:1.8;
            ">
                Realtime HELIOS infrastructure telemetry and distributed AI monitoring
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    feeds = [

        {
            "title":"Gemini Intelligence Connected",
            "desc":"Realtime inference engine operational",
            "icon":"🧠"
        },

        {
            "title":"Voice Systems Operational",
            "desc":"Speech recognition and synthesis active",
            "icon":"🎤"
        },

        {
            "title":"Agent Orchestrator Online",
            "desc":"Multi-agent coordination stable",
            "icon":"⚡"
        },

        {
            "title":"Memory Systems Healthy",
            "desc":"Persistent cognition architecture active",
            "icon":"📚"
        },

        {
            "title":"Recursive Reasoning Active",
            "desc":"Advanced inference loops running",
            "icon":"♾️"
        },

        {
            "title":"Workflow Engine Stable",
            "desc":"Autonomous execution systems healthy",
            "icon":"🛠️"
        }
    ]

    for item in feeds:

        st.markdown(
            f"""
            <div style="
                position:relative;
                overflow:hidden;

                margin-bottom:18px;

                padding:24px;

                border-radius:28px;

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
                0 12px 30px rgba(0,0,0,0.18);
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

                    display:flex;
                    align-items:center;
                    justify-content:space-between;

                    flex-wrap:wrap;

                    gap:20px;
                ">

                    <div style="
                        display:flex;
                        align-items:center;

                        gap:18px;
                    ">

                        <div style="
                            width:56px;
                            height:56px;

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

                            font-size:24px;

                            box-shadow:
                            0 0 24px rgba(124,58,237,0.35);
                        ">
                            {item['icon']}
                        </div>

                        <div>

                            <div style="
                                color:white;

                                font-size:18px;
                                font-weight:800;

                                margin-bottom:6px;
                            ">
                                {item['title']}
                            </div>

                            <div style="
                                color:#94a3b8;

                                font-size:14px;

                                line-height:1.7;
                            ">
                                {item['desc']}
                            </div>

                        </div>

                    </div>

                    <div style="
                        padding:10px 16px;

                        border-radius:999px;

                        background:
                        rgba(34,197,94,0.12);

                        border:
                        1px solid rgba(34,197,94,0.18);

                        display:flex;
                        align-items:center;

                        gap:10px;

                        color:#86efac;

                        font-size:12px;
                        font-weight:800;

                        letter-spacing:0.4px;
                    ">

                        <div style="
                            width:12px;
                            height:12px;

                            border-radius:999px;

                            background:#22c55e;

                            box-shadow:
                            0 0 16px #22c55e;
                        "></div>

                        ONLINE

                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )