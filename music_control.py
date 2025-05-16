# music_control.py
import cv2
import mediapipe as mp
import pygame
import os
import time
import math

def run():
    # Initialize Pygame for music
    pygame.init()
    pygame.mixer.init()

    # Load songs
    song_folder = "songs"
    songs = [os.path.join(song_folder, f) for f in os.listdir(song_folder) if f.endswith(".mp3")]
    if not songs:
        raise Exception("No MP3 files found in 'songs' folder!")

    current_song = 0
    playing = False

    def play_music():
        nonlocal playing
        if not playing:
            pygame.mixer.music.load(songs[current_song])
            pygame.mixer.music.play()
            playing = True

    def stop_music():
        nonlocal playing
        pygame.mixer.music.stop()
        playing = False

    def next_music():
        nonlocal current_song, playing
        current_song = (current_song + 1) % len(songs)
        pygame.mixer.music.load(songs[current_song])
        pygame.mixer.music.play()
        playing = True

    def prev_music():
        nonlocal current_song, playing
        current_song = (current_song - 1 + len(songs)) % len(songs)
        pygame.mixer.music.load(songs[current_song])
        pygame.mixer.music.play()
        playing = True

    # MediaPipe setup
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils
    tip_ids = [4, 8, 12, 16, 20]

    cap = cv2.VideoCapture(0)
    last_action_time = 0
    last_gesture = ""

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = hands.process(img_rgb)

        left_hand = None
        right_hand = None
        h, w, _ = img.shape

        if result.multi_hand_landmarks and result.multi_handedness:
            for idx, hand_handedness in enumerate(result.multi_handedness):
                label = hand_handedness.classification[0].label
                '''result.multi_handedness
                [ classification {
                    index: 0
                    score: 0.9987
                    label: "Right"
                    display_name: "Right"
                } ]

                '''
                landmarks = result.multi_hand_landmarks[idx]
                lm_list = []

                for id, lm in enumerate(landmarks.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append((id, cx, cy))

                mp_draw.draw_landmarks(img, landmarks, mp_hands.HAND_CONNECTIONS)

                if label == "Left":
                    left_hand = lm_list
                else:
                    right_hand = lm_list

        # === RIGHT HAND for MUSIC CONTROL ===
        if right_hand:
            fingers = []
            fingers.append(1 if right_hand[tip_ids[0]][1] < right_hand[tip_ids[0] - 1][1] else 0)
            for i in range(1, 5):
                fingers.append(1 if right_hand[tip_ids[i]][2] < right_hand[tip_ids[i] - 2][2] else 0)
            total = fingers.count(1)

            cv2.putText(img, f'Fingers: {total}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

           
            if total == 0:
                if last_gesture != "Fist":
                    fist_start_time = time.time()
                    last_gesture = "Fist"
                elif time.time() - fist_start_time >= 5:
                    cv2.putText(img, "Exiting in 5s...", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    stop_music()
                    break
                else:
                    remaining = 5 - int(time.time() - fist_start_time)
                    cv2.putText(img, f"Hold fist to exit: {remaining}s", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                if last_gesture == "Fist":
                    last_gesture = ""  # Reset if gesture changes


            if time.time() - last_action_time > 2:
                if total == 1:
                    play_music()
                    last_gesture = "Play"
                elif total == 3:
                    next_music()
                    last_gesture = "Next"
                elif total == 4:
                    prev_music()
                    last_gesture = "Previous"
                elif total == 5:
                    stop_music()
                    last_gesture = "Stop"
                elif total == 2:
                    last_gesture = "No action"
                last_action_time = time.time()

            cv2.putText(img, f'Right Hand: {last_gesture}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        # === LEFT HAND for VOLUME CONTROL ===
        if left_hand:
            x1, y1 = left_hand[4][1], left_hand[4][2]
            x2, y2 = left_hand[8][1], left_hand[8][2]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

            length = math.hypot(x2 - x1, y2 - y1)
            vol = int(min(max(length, 30), 200))
            volume_percent = int((vol - 30) / (200 - 30) * 100)
            pygame.mixer.music.set_volume(volume_percent / 100)

            cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 2)
            bar = int((volume_percent / 100) * 250)
            cv2.rectangle(img, (50, 400 - bar), (85, 400), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{volume_percent}%', (40, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        cv2.imshow("Gesture Music Controller", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
