import speech_recognition as sr

def recognize(filename="input.wav"):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(filename) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language="ko-KR")
        return text.strip()
    except sr.UnknownValueError:
        print("❗ 음성을 인식하지 못했습니다.")
        return None
    except sr.RequestError as e:
        print(f"❌ STT 요청 오류: {e}")
        return None
