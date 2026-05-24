import streamlit as st


def render_realtime_voice(mic_available, transcript=""):

    st.markdown(
        """
        <section class="helios-voice-launch helios-motion-card">
            <div class="helios-voice-launch-orb" aria-hidden="true">
                <span></span>
            </div>
            <div>
                <span>HELIOS LIVE VOICE</span>
                <strong>Use the clean Voice Room.</strong>
                <p>This Streamlit panel is retired for realtime conversation. The live speech-to-speech interface now runs in the Next frontend.</p>
                <a href="http://localhost:3000" target="_blank">Open Voice Room</a>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )
