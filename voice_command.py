import speech_recognition as sr
import music_control
import intruder_detection
import fall_detection
from speak import say

def get_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        say("Say a command: music, intruder, fall or exit.")
        print("\n🎙️ Say a command:")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print("🗣️ You said:", command)
        return command
    except:
        say("Sorry, I didn't understand.")
        print("❌ Couldn't understand. Try again.")
        return ""

if __name__ == "__main__":
    say("Welcome to Smart Home System.")
    while True:
        cmd = get_command()

        if "music" in cmd:
            say("Launching Music Controller.")
            print("🎵 Music Mode Activated")
            music_control.run()

        elif "intruder" in cmd:
            say("Launching Intruder Detection.")
            print("🚨 Intruder Detection Mode Activated")
            intruder_detection.run()

        elif any(word in cmd for word in ["help", "emergency", "danger", "accident"]):
            say("Launching Fall Detection.")
            print("🧍 Fall Detection Mode Activated")
            fall_detection.run()

        elif "exit" in cmd:
            say("Exiting Smart Home System. Goodbye!")
            print("👋 Exiting...")
            break

        else:
            say("Unknown command. Please try again.")
            print("⚠️ Unknown command.")
