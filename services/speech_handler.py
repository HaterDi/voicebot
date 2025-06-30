# services/speech_handler.py
import pyttsx3
import speech_recognition as sr

# Initialize TTS engine and set voice to Samantha
engine = pyttsx3.init()
engine.setProperty("rate", 160)
engine.setProperty("voice", "com.apple.speech.synthesis.voice.samantha")

def speak(text):
    print(f"🗣️ Bot says: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎧 Listening...")
        audio = recognizer.listen(source)

    try:
        recognized = recognizer.recognize_google(audio)
        print("👂 Recognized:", recognized)
        return recognized.strip()
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return ""
    except sr.RequestError:
        print("❌ Could not request results")
        return ""
