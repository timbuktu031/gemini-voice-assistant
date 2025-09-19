from gtts import gTTS

def speak(text, filename="response.mp3"):
    try:
        tts = gTTS(text=text, lang="ko")
        tts.save(filename)
    except Exception as e:
        print(f"❌ TTS 오류: {e}")
