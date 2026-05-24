import speech_recognition as sr
import time

from voice.voice_output import speak

from core.cognitive_engine import (
    CognitiveEngine
)

recognizer = sr.Recognizer()

# instantiate engine
engine = CognitiveEngine()

def listen():

    with sr.Microphone() as source:

        print("\n[HELIOS LISTENING]\n")

        recognizer.adjust_for_ambient_noise(
            source,
            duration=0.8
        )

        audio = recognizer.listen(
            source,
            timeout=12,
            phrase_time_limit=15
        )

    try:

        text = recognizer.recognize_google(audio)

        if "helios" not in text.lower():
            print("[WAKE WORD NOT DETECTED]")
            return

        text = text.lower().replace("helios", "").strip()

        print(f"\nYOU SAID: {text}\n")

        response = engine.execute(text)

        print("\n[HELIOS RESPONSE]\n")

        print(response)

        speak(response)

        return None

    except sr.WaitTimeoutError:

        print("\n[HELIOS IDLE]\n")

        time.sleep(1)

        return

    except Exception as e:

        print(f"\n[ERROR]\n{e}\n")

        time.sleep(1) 


if __name__ == "__main__":

    speak("HELIOS online and operational.")

    while True:

        listen()
    
