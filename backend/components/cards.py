from utils.ui_utils import sanitize_text
import streamlit as st


def sanitize(value):

    return sanitize_text(value)


def render_glass_card(
    title,
    value,
    subtitle="",
    icon="AI"
):

    title = sanitize(title)
    value = sanitize(value)
    subtitle = sanitize(subtitle)
    icon = sanitize(icon)

    card_html = f"""
    <div class="metric-card helios-motion-card" style="
        position:relative;
        overflow:hidden;

        border-radius:28px;

        min-height:220px;

        padding:24px;

        background:
        linear-gradient(
            180deg,
            rgba(15,23,42,0.78),
            rgba(2,6,23,0.92)
        );

        border:
        1px solid rgba(255,255,255,0.06);

        backdrop-filter:blur(22px);

        box-shadow:
        0 10px 35px rgba(0,0,0,0.22);

        transition:all 0.25s ease;
    ">

        <div style="
            position:absolute;

            width:180px;
            height:180px;

            border-radius:999px;

            background:
            rgba(124,58,237,0.14);

            top:-80px;
            right:-80px;

            filter:blur(20px);
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

            margin-bottom:22px;
        ">

            <div style="
                width:52px;
                height:52px;

                border-radius:18px;

                display:flex;
                align-items:center;
                justify-content:center;

                font-size:24px;

                background:
                linear-gradient(
                    135deg,
                    #7c3aed,
                    #2563eb
                );

                box-shadow:
                0 0 24px rgba(124,58,237,0.35);
            ">
                {icon}
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
                font-weight:700;

                letter-spacing:0.6px;
            ">
                LIVE
            </div>

        </div>

        <div style="
            position:relative;
            z-index:2;

            color:#94a3b8;

            font-size:13px;

            margin-bottom:12px;

            font-weight:500;

            letter-spacing:0.3px;
        ">
            {title}
        </div>

        <div style="
            position:relative;
            z-index:2;

            color:white;

            font-size:38px;

            font-weight:800;

            line-height:1.1;

            margin-bottom:14px;

            overflow-wrap:break-word;
            word-break:break-word;
        ">
            {value}
        </div>

        <div style="
            position:relative;
            z-index:2;

            color:#94a3b8;

            font-size:13px;

            line-height:1.8;

            overflow-wrap:break-word;
            word-break:break-word;
        ">
            {subtitle}
        </div>

    </div>
    """

    st.markdown(
        card_html,
        unsafe_allow_html=True
    )
