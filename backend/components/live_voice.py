import os
import tempfile
import subprocess
import re

import markdown  # type: ignore
import streamlit as st

from utils.ui_utils import sanitize_text

from dotenv import load_dotenv
import speech_recognition as sr

try:
    from gtts import gTTS
except Exception:
    gTTS = None

try:
    from streamlit_mic_recorder import mic_recorder
except ModuleNotFoundError:
    mic_recorder = None

from api.ai_provider import generate_ai_response

load_dotenv()


# =====================================
# CLEAN AI RESPONSE
# =====================================

def clean_ai_response(text):

    text = str(text)

    text = re.sub(
        r"```[a-zA-Z0-9_-]*[\s\S]*?```",
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


# =====================================
# SAFE MARKDOWN
# =====================================

def render_safe_markdown(text):
    escaped = sanitize_text(text)

    md_html = markdown.markdown(
        escaped.replace(
            "\n",
            "  \n"
        )
    )

    st.markdown(
        md_html,
        unsafe_allow_html=True
    )


# =====================================
# LIVE VOICE
# =====================================

def render_live_voice():

    if mic_recorder is None:

        st.warning(
            "Voice input is unavailable because streamlit-mic-recorder is not installed."
        )

        return

    st.markdown(
        """
        <div class="hero-card">

            <div style="
                display:flex;
                align-items:center;
                justify-content:space-between;
                flex-wrap:wrap;
                gap:24px;
            ">

                <div>

                    <div style="
                        color:#c084fc;
                        font-size:14px;
                        font-weight:700;
                        letter-spacing:1px;
                        margin-bottom:12px;
                    ">
                        HELIOS VOICE CORE
                    </div>

                    <h1 style="
                        margin:0;
                        font-size:42px;
                        font-weight:800;
                        line-height:1.08;
                        color:white;
                    ">
                        Realtime <br/>
                        Voice Intelligence
                    </h1>

                    <p style="
                        margin-top:18px;
                        max-width:680px;
                        color:#94a3b8;
                        font-size:15px;
                        line-height:1.8;
                    ">
                        Speak naturally with HELIOS using
                        realtime speech recognition,
                        conversational cognition,
                        and AI-generated voice responses.
                    </p>

                </div>

                <div style="
                    width:180px;
                    height:180px;

                    border-radius:40px;

                    background:
                    radial-gradient(
                        circle at top,
                        rgba(124,58,237,0.55),
                        rgba(37,99,235,0.15)
                    );

                    border:
                    1px solid rgba(255,255,255,0.08);

                    display:flex;
                    align-items:center;
                    justify-content:center;

                    backdrop-filter:blur(20px);

                    box-shadow:
                    0 0 50px rgba(124,58,237,0.25);
                ">

                    <div style="font-size:70px;">
                        🎤
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
            margin-top:24px;
            margin-bottom:18px;
        ">

            <h2 style="
                margin:0;
                color:white;
                font-size:24px;
                font-weight:700;
            ">
                ⚡ Voice Session
            </h2>

            <p style="
                margin-top:8px;
                color:#94a3b8;
                font-size:14px;
            ">
                Realtime conversational cognition
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    audio = mic_recorder(

        start_prompt="🎤 Start Conversation",

        stop_prompt="⏹ Stop Recording",

        just_once=True,

        use_container_width=True
    )

    if not audio:

        return

    temp_audio_path = None
    converted_path = None
    tts_path = None

    try:

        st.markdown(
            """
            <div style="
                padding:18px;

                border-radius:22px;

                background:
                rgba(255,255,255,0.03);

                border:
                1px solid rgba(255,255,255,0.06);

                margin-bottom:18px;

                color:#94a3b8;

                font-size:14px;
            ">
                ⚡ Processing voice input...
            </div>
            """,
            unsafe_allow_html=True
        )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".webm"
        ) as temp_audio:

            temp_audio.write(
                audio["bytes"]
            )

            temp_audio_path = temp_audio.name

        converted_path = (
            temp_audio_path + ".wav"
        )

        subprocess.run(

            [
                "ffmpeg",
                "-y",
                "-i",
                temp_audio_path,
                converted_path
            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL,

            check=True
        )

        recognizer = sr.Recognizer()

        with sr.AudioFile(converted_path) as source:

            audio_data = recognizer.record(source)

        user_text = recognizer.recognize_google(
            audio_data
        ).strip()

        if not user_text:

            st.error(
                "No speech detected."
            )

            return

        user_text_safe = sanitize_text(
            user_text
        )

        st.markdown(
            f"""
            <div style="
                position:relative;
                overflow:hidden;

                padding:22px;
                margin-top:20px;

                border-radius:28px;

                background:
                linear-gradient(
                    180deg,
                    rgba(30,64,175,0.18),
                    rgba(15,23,42,0.82)
                );

                border:
                1px solid rgba(59,130,246,0.18);

                backdrop-filter:blur(24px);
            ">

                <div style="
                    color:#93c5fd;

                    font-size:12px;

                    font-weight:700;

                    margin-bottom:10px;
                ">
                    YOU SAID
                </div>

                <div style="
                    color:white;

                    font-size:15px;

                    line-height:1.9;

                    white-space:pre-wrap;

                    overflow-wrap:break-word;
                    word-break:break-word;
                ">
                    {user_text_safe}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        prompt = f"""

You are HELIOS AI.

Behave like a futuristic AI assistant.

Keep responses:
- short
- sharp
- conversational
- modern
- intelligent

Never sound robotic.

User:
{user_text}

"""

        ai_response = generate_ai_response(
            prompt
        )

        cleaned_ai = clean_ai_response(
            ai_response
        )

        # render ai content in-place

        st.markdown(
            f"""
            <div style="
                position:relative;
                overflow:hidden;

                padding:24px;
                margin-top:22px;

                border-radius:28px;

                background:
                linear-gradient(
                    180deg,
                    rgba(76,29,149,0.18),
                    rgba(15,23,42,0.92)
                );

                border:
                1px solid rgba(168,85,247,0.18);

                backdrop-filter:blur(24px);

                box-shadow:
                0 12px 35px rgba(0,0,0,0.22);
            ">

                <div style="
                    display:flex;
                    align-items:center;
                    gap:14px;

                    margin-bottom:18px;
                ">

                    <div style="
                        width:46px;
                        height:46px;

                        border-radius:16px;

                        background:
                        linear-gradient(
                            135deg,
                            #7c3aed,
                            #2563eb
                        );

                        display:flex;
                        align-items:center;
                        justify-content:center;

                        font-size:18px;

                        color:white;

                        box-shadow:
                        0 0 22px rgba(124,58,237,0.35);
                    ">
                        ⚡
                    </div>

                    <div>

                        <div style="
                            color:white;
                            font-size:15px;
                            font-weight:700;
                            margin-bottom:4px;
                        ">
                            HELIOS
                        </div>

                        <div style="
                            color:#d8b4fe;
                            font-size:12px;
                        ">
                            Realtime Voice Intelligence
                        </div>

                    </div>

                </div>

                <div style="
                    color:#e9d5ff;

                    font-size:14px;

                    line-height:1.95;

                    overflow-wrap:break-word;
                    word-break:break-word;
                ">

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        if gTTS is None:

            from voice.voice_output import speak

            speak(
                cleaned_ai
            )

        else:

            tts = gTTS(
                text=cleaned_ai,
                lang="en",
                slow=False
            )

            tts_path = (
                temp_audio_path + ".mp3"
            )

            tts.save(tts_path)

            with open(tts_path, "rb") as audio_file:

                st.audio(
                    audio_file.read(),
                    format="audio/mp3"
                )

    except sr.UnknownValueError:

        st.error(
            "Speech could not be recognized."
        )

    except sr.RequestError as error:

        st.error(
            f"Speech recognition failed: {str(error)}"
        )

    except subprocess.CalledProcessError:

        st.error(
            "FFmpeg audio conversion failed."
        )

    except Exception as error:

        st.error(
            f"Voice system error: {str(error)}"
        )

    finally:

        for path in [

            temp_audio_path,
            converted_path,
            tts_path

        ]:

            try:

                if path and os.path.exists(path):

                    os.remove(path)

            except Exception:

                pass
