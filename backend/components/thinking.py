import streamlit as st


def render_thinking():

    placeholder = st.empty()

    placeholder.markdown(
        """
        <div class="helios-thinking-card helios-motion-card">
            <div class="helios-thinking-orb">
                <span></span>
            </div>
            <div class="helios-thinking-main">
                <div class="helios-thinking-top">
                    <strong>HELIOS Cognitive Processing</strong>
                    <em>LIVE INFERENCE</em>
                </div>
                <p>
                    Routing intent, loading memory context, checking tools, and composing the response path.
                </p>
                <div class="helios-thinking-bars">
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    return placeholder


def render_processing_state(
    placeholder,
    stage,
    detail,
    *,
    agent="HELIOS",
    mode="Think"
):

    placeholder.markdown(
        f"""
        <div class="helios-thinking-card helios-motion-card">
            <div class="helios-thinking-orb">
                <span></span>
            </div>
            <div class="helios-thinking-main">
                <div class="helios-thinking-top">
                    <strong>{stage}</strong>
                    <em>{agent} • {mode}</em>
                </div>
                <p>{detail}</p>
                <div class="helios-processing-steps">
                    <span class="active">Routing</span>
                    <span class="active">Thinking</span>
                    <span>Using Tool</span>
                    <span>Writing</span>
                    <span>Done</span>
                </div>
                <div class="helios-thinking-bars">
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    return placeholder
