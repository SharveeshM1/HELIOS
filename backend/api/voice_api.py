import os
import tempfile
import subprocess
import traceback
import shutil

try:
    import speech_recognition as sr
except Exception:
    sr = None

try:
    from gtts import gTTS
except Exception:
    gTTS = None

# =========================================
# AUDIO CONVERSION
# =========================================

def convert_audio_to_wav(

    input_path,
    output_path

):

    try:
        ffmpeg = next(
            (
                path
                for path in [
                    shutil.which("ffmpeg"),
                    "/opt/homebrew/bin/ffmpeg",
                    "/usr/local/bin/ffmpeg",
                    "ffmpeg"
                ]
                if path and (
                    path == "ffmpeg"
                    or os.path.exists(path)
                )
            ),
            "ffmpeg"
        )

        result = subprocess.run(

            [
                ffmpeg,
                "-y",
                "-i",
                input_path,
                output_path
            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL
        )

        return result.returncode == 0

    except Exception:

        traceback.print_exc()

        return False

# =========================================
# SPEECH TO TEXT
# =========================================

def transcribe_audio(

    audio_bytes

):

    if sr is None:

        return (
            "SpeechRecognition is not installed in the Python environment running Streamlit."
        )

    temp_path = None

    converted_path = None

    try:

        # =================================
        # SAVE AUDIO
        # =================================

        with tempfile.NamedTemporaryFile(

            delete=False,

            suffix=".webm"

        ) as temp_audio:

            temp_audio.write(
                audio_bytes
            )

            temp_path = temp_audio.name

        converted_path = (
            f"{temp_path}.wav"
        )

        # =================================
        # CONVERT AUDIO
        # =================================

        conversion_success = (
            convert_audio_to_wav(

                temp_path,

                converted_path
            )
        )

        if not conversion_success:

            return (
                "Audio conversion failed."
            )

        # =================================
        # TRANSCRIBE
        # =================================

        recognizer = sr.Recognizer()

        recognizer.energy_threshold = 300

        recognizer.dynamic_energy_threshold = True

        with sr.AudioFile(
            converted_path
        ) as source:

            audio_data = recognizer.record(
                source
            )

        transcript = recognizer.recognize_google(
            audio_data
        )

        if not transcript:

            return (
                "No speech detected."
            )

        return str(transcript).strip()

    except sr.UnknownValueError:

        return (
            "Speech could not be recognized."
        )

    except sr.RequestError:

        return (
            "Speech recognition service unavailable."
        )

    except Exception:

        traceback.print_exc()

        return (
            "Voice transcription failed."
        )

    finally:

        # =================================
        # CLEANUP
        # =================================

        try:

            if temp_path and os.path.exists(
                temp_path
            ):

                os.remove(temp_path)

        except Exception:

            pass

        try:

            if converted_path and os.path.exists(
                converted_path
            ):

                os.remove(converted_path)

        except Exception:

            pass

# =========================================
# TEXT TO SPEECH
# =========================================

def generate_voice(

    text,

    output_path="helios_reply.mp3"

):

    try:

        clean_text = str(text).strip()

        if not clean_text:

            return None

        if gTTS is None:

            return None

        tts = gTTS(

            text=clean_text,

            lang="en",

            slow=False
        )

        tts.save(output_path)

        if not os.path.exists(
            output_path
        ):

            return None

        return output_path

    except Exception:

        traceback.print_exc()

        return None

# =========================================
# FULL VOICE PIPELINE
# =========================================

def process_voice_interaction(

    audio_bytes,
    ai_callback

):

    # =====================================
    # TRANSCRIBE
    # =====================================

    user_text = transcribe_audio(
        audio_bytes
    )

    if not user_text:

        return {

            "success": False,

            "user_text": "",

            "ai_response":
            "Voice transcription failed.",

            "audio_path": None
        }

    # =====================================
    # GENERATE AI RESPONSE
    # =====================================

    try:

        ai_response = ai_callback(
            user_text
        )

        if not ai_response:

            ai_response = (
                "HELIOS could not generate a response."
            )

    except Exception:

        traceback.print_exc()

        ai_response = (
            "AI response generation failed."
        )

    # =====================================
    # GENERATE AUDIO
    # =====================================

    audio_path = generate_voice(
        ai_response
    )

    # =====================================
    # FINAL OUTPUT
    # =====================================

    return {

        "success": True,

        "user_text":
        str(user_text),

        "ai_response":
        str(ai_response),

        "audio_path":
        audio_path
    }
