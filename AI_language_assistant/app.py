import streamlit as st
from streamlit_mic_recorder import mic_recorder
from utils.speech_stream import transcribe_from_bytes, pronunciation_assessment, speak_text
from utils.translator import translate
from utils.evaluator import evaluate_user_phrase
from dotenv import load_dotenv
import random
import os
import io
import wave
import atexit
import csv

load_dotenv()

AUDIO_DIR = "audio_output"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Clean up all .wav files in the directory on exit
def cleanup_audio_files():
    for file in os.listdir(AUDIO_DIR):
        if file.endswith(".wav"):
            try:
                os.remove(os.path.join(AUDIO_DIR, file))
            except Exception as e:
                print(f"Cleanup failed for {file}: {e}")

atexit.register(cleanup_audio_files)

# Utility function to save and return a playable audio file
def play_and_save_audio(audio_bytes, filename):
    filepath = os.path.join(AUDIO_DIR, filename)
    try:
        with wave.open(filepath, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_bytes)

        with open(filepath, "rb") as f:
            st.audio(f.read(), format="audio/wav")
    except Exception as e:
        st.warning(f"Audio error: {e}")

st.set_page_config(page_title="🎧 Smart Language Learning Assistant", layout="centered")

st.title("🎧 Smart Language Assistant")
st.markdown("Practice or play quiz games to improve your language skills. Powered by Azure AI.")

lang_dict = {
    "French": "fr-FR",
    "Spanish": "es-ES",
    "German": "de-DE",
    "Hindi": "hi-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "English": "en-US"
}
lang_short = {
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "English": "en"
}

mode = st.radio("Select Mode", ["Practice", "Game"], horizontal=True)
challenge_mode = st.radio("Challenge Level", ["Normal", "Hard"], horizontal=True)

if mode == "Practice":
    lang_name = st.selectbox("🎯 Target Language", list(lang_dict.keys()), index=0)
    target_lang = lang_short[lang_name]
    target_locale = lang_dict[lang_name]
    expected = st.text_input("Expected Phrase (in English)", "I want to learn French")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🔈 Hear Question (English)", key="hear_question"):
            tts_audio = speak_text(expected, lang="en")
            if tts_audio:
                play_and_save_audio(tts_audio, "question_tts.wav")
            else:
                st.warning("❌ Audio could not be generated.")

    with col2:
        if challenge_mode == "Normal":
            if st.button("🔈 Hear in Target Language", key="hear_target"):
                translation = translate(expected, target_lang)
                st.markdown(f"**📝 Translated Text:** {translation}")
                tts_audio = speak_text(translation, lang=target_locale)
                if tts_audio:
                    play_and_save_audio(tts_audio, "translation_tts.wav")
                else:
                    st.warning("Audio could not be generated.")

    audio = mic_recorder(start_prompt="🎙️ Start Recording", stop_prompt="🛑 Stop Recording", just_once=True, format="wav", key="practice_recorder")
    if audio:
        transcript = transcribe_from_bytes(audio['bytes'])
        score_str = evaluate_user_phrase(transcript, expected)
        try:
            score = float(score_str)
        except:
            score = 0.0

        pronunciation = pronunciation_assessment(audio['bytes'], expected)

        st.subheader("📝 Transcription")
        st.success(transcript)

        st.subheader("✅ Match Score")
        st.progress(score / 100)
        st.caption(f"{score}% match with expected phrase.")

        st.subheader("🧠 Pronunciation Details")
        if "error" not in pronunciation:
            st.metric("Accuracy", f"{pronunciation['accuracy']:.2f}")
            st.metric("Fluency", f"{pronunciation['fluency']:.2f}")
            st.metric("Completeness", f"{pronunciation['completeness']:.2f}")
        else:
            st.warning(pronunciation["error"])

else:
    st.markdown("### 🎮 Language Quiz Game")

    lang_name = st.selectbox("🗣️ Choose Quiz Language", ["French", "Spanish", "German", "Hindi", "Tamil"], index=0)
    target_locale = lang_dict[lang_name]

    quiz_questions = []
    with open("game_phrases.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["lang"] == target_locale:
                quiz_questions.append(row)

    if not quiz_questions:
        st.warning("No quiz phrases found for this language.")
    else:
        if "quiz_index" not in st.session_state:
            st.session_state.quiz_index = 0
            random.shuffle(quiz_questions)
        if "quiz_score" not in st.session_state:
            st.session_state.quiz_score = 0
        if "quiz_round" not in st.session_state:
            st.session_state.quiz_round = 1
        if "quiz_done" not in st.session_state:
            st.session_state.quiz_done = False

        if st.session_state.quiz_round <= len(quiz_questions):
            current = quiz_questions[st.session_state.quiz_index]
            expected = current["answer"]
            st.markdown(f"### 🎯 Round {st.session_state.quiz_round}: {current['question']}")

            if challenge_mode == "Normal":
                if st.button("🔈 Hear the Answer", key=f"hear_answer_{st.session_state.quiz_round}"):
                    tts_audio = speak_text(expected, lang=current["lang"])
                    if tts_audio:
                        play_and_save_audio(tts_audio, f"quiz_answer_{st.session_state.quiz_round}.wav")
                    else:
                        st.warning("Audio could not be generated.")

            audio = mic_recorder(start_prompt="🎙️ Start Recording", stop_prompt="🛑 Stop Recording", just_once=True, format="wav", key=f"recorder_{st.session_state.quiz_round}")
            if audio:
                transcript = transcribe_from_bytes(audio['bytes'])
                score_str = evaluate_user_phrase(transcript, expected)
                try:
                    score = float(score_str)
                except:
                    score = 0.0

                pronunciation = pronunciation_assessment(audio['bytes'], expected)

                st.subheader("📝 Transcription")
                st.success(transcript)

                st.subheader("✅ Match Score")
                st.progress(score / 100)
                st.caption(f"{score}% match with expected phrase.")

                st.subheader("🧠 Pronunciation Details")
                if "error" not in pronunciation:
                    st.metric("Accuracy", f"{pronunciation['accuracy']:.2f}")
                    st.metric("Fluency", f"{pronunciation['fluency']:.2f}")
                    st.metric("Completeness", f"{pronunciation['completeness']:.2f}")
                else:
                    st.warning(pronunciation["error"])

            if st.button("➡️ Next", key=f"next_{st.session_state.quiz_round}"):
                st.session_state.quiz_score += score if 'score' in locals() else 0
                st.session_state.quiz_round += 1
                st.session_state.quiz_index += 1
                st.rerun()

        elif st.session_state.quiz_done:
            final = st.session_state.quiz_score / len(quiz_questions)
            st.success(f"🏁 Quiz Over! Your average score: {final:.2f}")
            if st.button("🔁 Play Again"):
                st.session_state.quiz_index = 0
                st.session_state.quiz_score = 0
                st.session_state.quiz_round = 1
                st.session_state.quiz_done = False
                random.shuffle(quiz_questions)
                st.rerun()
