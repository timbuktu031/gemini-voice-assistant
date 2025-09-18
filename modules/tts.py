# modules/tts.py
from google.cloud import texttospeech
import os
import platform
import time
from .utils.text_utils import clean_text
from .gui import send_to_gui
from modules.config import app_config

# TTS 클라이언트 초기화
tts_client = texttospeech.TextToSpeechClient()

def play_audio(filename):
    """오디오 재생"""
    system = platform.system()
    try:
        if system == "Linux":
            os.system(f"aplay {filename}")
        elif system == "Darwin":
            os.system(f"afplay {filename}")
        elif system == "Windows":
            os.system(f"start {filename}")
        return True
    except Exception as e:
        print(f"오디오 재생 오류: {e}")
        return False

def speak_korean(text):
    """한국어 TTS"""
    cleaned_text = clean_text(text)
    if not cleaned_text:
        return
    
    synthesis_input = texttospeech.SynthesisInput(text=cleaned_text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        name="ko-KR-Wavenet-A",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )
    
    temp_filename = f"{app_config.temp_audio_prefix}{int(time.time())}.wav"
    
    try:
        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        with open(temp_filename, "wb") as out:
            out.write(response.audio_content)
        
        send_to_gui("status", "🔊 음성 재생 중...")
        play_success = play_audio(temp_filename)
        
        if play_success:
            send_to_gui("status", "✅ 음성 재생 완료")
        else:
            send_to_gui("status", "⚠️ 음성 재생 실패")
            
    except Exception as e:
        print(f"TTS 오류: {e}")
        send_to_gui("status", f"❌ TTS 오류")
    finally:
        try:
            if os.path.exists(temp_filename):
                time.sleep(0.5)
                os.remove(temp_filename)
        except Exception as e:
            print(f"파일 삭제 오류: {e}")
