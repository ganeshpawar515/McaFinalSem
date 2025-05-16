#voice_command.py
import speech_recognition as sr
import music_control
import intruder_detection
import fall_detection
from speak import say

def recognize_speech(timeout=None, phrase_time_limit=5):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎧 Listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            text = recognizer.recognize_google(audio).lower()
            print("🗣️ Heard:", text)
            return text
        except:
            return ""

if __name__ == "__main__":
    say("Welcome to Smart Home System.")
    command_mode = False

    while True:
        if not command_mode:
            # Passive mode: Wait for wake word
            text = recognize_speech()
            if "hey buddy" in text or "are you there" in text:
                say("Yes, I am here.")
                command_mode = True
        else:
            # Active command mode
            say("What do you want to do?")
            while command_mode:
                cmd = recognize_speech()

                if "music" in cmd:
                    say("Launching Music Controller.")
                    print("🎵 Music Mode Activated")
                    music_control.run()
                    command_mode = False

                elif "intruder" in cmd:
                    say("Launching Intruder Detection.")
                    print("🚨 Intruder Detection Mode Activated")
                    intruder_detection.run()
                    command_mode = False

                elif any(word in cmd for word in ["help", "emergency", "danger", "accident", "fall"]):
                    say("Launching Fall Detection.")
                    print("🧍 Fall Detection Mode Activated")
                    fall_detection.run()
                    command_mode = False

                elif "exit" in cmd:
                    say("Exiting Smart Home System. Goodbye!")
                    print("👋 Exiting...")
                    exit()

                elif cmd == "":
                    print("...waiting for command...")
                    continue  # Keep listening

                else:
                    say("Unknown command. Please try again.")
                    print("⚠️ Unknown command.")
