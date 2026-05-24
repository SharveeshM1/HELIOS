try:
    import pyttsx3
except Exception:
    pyttsx3 = None

import logging
import platform
import shutil
import subprocess


logger = logging.getLogger("helios")


def _create_engine():

    if pyttsx3 is None:

        return None

    try:

        engine = pyttsx3.init()

        voices = engine.getProperty(
            "voices"
        )

        if voices:

            voice = voices[17] if len(voices) > 17 else voices[0]

            engine.setProperty(
                "voice",
                voice.id
            )

        engine.setProperty(
            "rate",
            175
        )

        engine.setProperty(
            "volume",
            1.0
        )

        return engine

    except Exception:

        return None


engine = _create_engine()


def speak(text):

    if not text or engine is None:

        return _speak_with_system_voice(text)

    print(f"\n[HELIOS SPEAKING]\n{text}\n")

    try:

        engine.say(text)

        engine.runAndWait()

    except Exception:

        logger.exception(
            "pyttsx3 voice output failed"
        )

        return _speak_with_system_voice(text)


def _speak_with_system_voice(text):

    clean_text = str(text or "").strip()

    if not clean_text:

        return

    if platform.system() != "Darwin":

        return

    say_path = shutil.which("say") or "/usr/bin/say"

    if not say_path:

        return

    try:

        subprocess.run(
            [
                say_path,
                clean_text[:4000]
            ],
            check=False
        )

    except Exception:

        logger.exception(
            "System voice output failed"
        )
