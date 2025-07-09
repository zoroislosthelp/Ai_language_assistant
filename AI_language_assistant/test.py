import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv

load_dotenv()

# 🔐 Hardcoded credentials — replace with your actual values
speech_key = os.getenv("AZURE_SPEECH_KEY")  # example: "your_speech_key_here    "
region = os.getenv("AZURE_SPEECH_REGION")  # example: "your_region_here"

# 🔊 Configure speech synthesis
config = speechsdk.SpeechConfig(subscription=speech_key, region=region)
config.speech_synthesis_voice_name = "en-US-AriaNeural"

synthesizer = speechsdk.SpeechSynthesizer(speech_config=config)

# 📢 Speak test text
result = synthesizer.speak_text_async("Hello! This is a test of Azure Text to Speech.").get()

if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("✅ Speech synthesis successful!")
else:
    print("❌ Failed to synthesize speech.")
    print("Reason:", result.reason)
    if result.cancellation_details:
        print("Details:", result.cancellation_details.reason)
        print("Error:", result.cancellation_details.error_details)
