import azure.cognitiveservices.speech as speechsdk
import os
import tempfile
from pydub import AudioSegment
from io import BytesIO
import io

# Language code mapping: short code to Azure locale
LANG_MAP = {
    "en": "en-US",
    "fr": "fr-FR",
    "es": "es-ES",
    "de": "de-DE",
    "hi": "hi-IN",
    "ta": "ta-IN",
    "te": "te-IN"
}

def transcribe_from_bytes(audio_bytes, lang="en", auto_detect=False):
    """
    Transcribe audio bytes to text using Azure Speech-to-Text.
    Supports optional language auto-detection.
    """
    audio = AudioSegment.from_file(BytesIO(audio_bytes), format="wav")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        audio.export(tmp.name, format="wav")
        path = tmp.name

    config = speechsdk.SpeechConfig(
        subscription=os.getenv("AZURE_SPEECH_KEY"),
        region=os.getenv("AZURE_SPEECH_REGION")
    )
    if auto_detect:
        config.set_property(speechsdk.PropertyId.SpeechServiceConnection_SingleLanguageIdPriority, "Latency")
        config.set_property(speechsdk.PropertyId.SpeechServiceConnection_SingleLanguageId, "auto")
    else:
        azure_lang = LANG_MAP.get(lang, "en-US")
        config.speech_recognition_language = azure_lang

    audio_input = speechsdk.AudioConfig(filename=path)
    recognizer = speechsdk.SpeechRecognizer(speech_config=config, audio_config=audio_input)
    result = recognizer.recognize_once()
    return result.text if result.reason == speechsdk.ResultReason.RecognizedSpeech else "Unable to recognize speech."

def pronunciation_assessment(audio_bytes, expected_text, lang="en"):
    """
    Assess pronunciation accuracy, fluency, and completeness using Azure.
    """
    audio = AudioSegment.from_file(BytesIO(audio_bytes), format="wav")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        audio.export(tmp.name, format="wav")
        path = tmp.name

    config = speechsdk.SpeechConfig(
        subscription=os.getenv("AZURE_SPEECH_KEY"),
        region=os.getenv("AZURE_SPEECH_REGION")
    )
    azure_lang = LANG_MAP.get(lang, "en-US")
    config.speech_recognition_language = azure_lang

    audio_input = speechsdk.AudioConfig(filename=path)
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=expected_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Word,
        enable_miscue=True,
    )
    recognizer = speechsdk.SpeechRecognizer(speech_config=config, audio_config=audio_input)
    pronunciation_config.apply_to(recognizer)
    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        json_result = speechsdk.PronunciationAssessmentResult(result)
        return {
            "accuracy": json_result.accuracy_score,
            "fluency": json_result.fluency_score,
            "completeness": json_result.completeness_score,
            "text": result.text
        }
    else:
        return {"error": "Unable to assess pronunciation."}
    
def speak_text(text, lang="en"):
    import azure.cognitiveservices.speech as speechsdk
    import os

    lang_map = {
        "en": "en-US-AriaNeural",
        "fr": "fr-FR-DeniseNeural",
        "es": "es-ES-ElviraNeural",
        "de": "de-DE-KatjaNeural",
        "hi": "hi-IN-SwaraNeural",
        "ta": "ta-IN-PallaviNeural",
        "te": "te-IN-MohanNeural"
    }

    voice_name = lang_map.get(lang, "en-US-AriaNeural")
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    region = os.getenv("AZURE_SPEECH_REGION")

    if not speech_key or not region:
        print("❌ Missing Azure credentials.")
        return None

    config = speechsdk.SpeechConfig(subscription=speech_key, region=region)
    config.speech_synthesis_voice_name = voice_name

    synthesizer = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=None)
    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        stream = speechsdk.AudioDataStream(result)
        audio_data = bytearray()

        chunk_size = 4096
        while True:
            buffer = bytes(chunk_size)
            read = stream.read_data(buffer)
            if read == 0:
                break
            audio_data += buffer[:read]
        print("Audio data size (bytes):", len(audio_data))

        return bytes(audio_data)

    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        print("❌ Speech synthesis canceled:", cancellation.reason)
        print("🔎 Error details:", cancellation.error_details)
        return None

    else:
        print("⚠️ Unexpected result:", result.reason)
        return None
