# modules/tts.py - 수정된 버전 (Import 문제 해결)
import os
import platform
import time
import re

# Google Cloud TTS 클라이언트 초기화
try:
    from google.cloud import texttospeech
    tts_client = texttospeech.TextToSpeechClient()
    print("✅ Google Cloud TTS 클라이언트 초기화 성공")
except Exception as e:
    print(f"❌ Google Cloud TTS 클라이언트 초기화 실패: {e}")
    print("💡 해결방법: GOOGLE_APPLICATION_CREDENTIALS 환경변수를 설정하세요")
    tts_client = None

def clean_text(text):
    """텍스트 정리 (TTS용)"""
    if not text:
        return ""
    
    try:
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='replace')
        
        text = str(text).encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'[^\w\s가-힣.,?!~\-]', '', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
        
    except Exception as e:
        print(f"텍스트 정리 오류: {e}")
        return str(text)[:100] if text else ""

def get_audio_player_command(filename):
    """운영체제별 오디오 재생 명령어 반환"""
    system = platform.system().lower()
    
    if system == "linux":
        players = [
            f"aplay {filename}",
            f"paplay {filename}",
            f"mpv --no-video {filename}",
            f"mpg123 {filename}"
        ]
        return players
        
    elif system == "darwin":
        return [f"afplay {filename}"]
        
    elif system == "windows":
        return [
            f'powershell -c "(New-Object Media.SoundPlayer \\"{filename}\\").PlaySync()"',
            f"start /wait wmplayer {filename}"
        ]
    else:
        print(f"지원하지 않는 운영체제: {system}")
        return []

def play_audio(filename):
    """운영체제별 오디오 재생"""
    if not os.path.exists(filename):
        print(f"❌ 오디오 파일을 찾을 수 없음: {filename}")
        return False
    
    commands = get_audio_player_command(filename)
    
    for cmd in commands:
        try:
            print(f"🔊 오디오 재생 시도: {cmd.split()[0]}")
            result = os.system(f"{cmd} 2>/dev/null")
            
            if result == 0:
                print("✅ 오디오 재생 성공")
                return True
            else:
                print(f"⚠️  명령어 실패 (code: {result})")
                
        except Exception as e:
            print(f"❌ 재생 오류: {e}")
            continue
    
    print("❌ 모든 오디오 플레이어 시도 실패")
    return False

def test_audio_system():
    """오디오 시스템 테스트"""
    system = platform.system().lower()
    print(f"🔊 오디오 시스템 테스트 (OS: {system})")
    
    if system == "linux":
        if os.system("which aplay >/dev/null 2>&1") != 0:
            print("❌ aplay가 설치되지 않았습니다.")
            print("💡 해결방법: sudo apt-get install alsa-utils")
            
            alternatives = ["paplay", "mpv", "mpg123"]
            available = []
            for player in alternatives:
                if os.system(f"which {player} >/dev/null 2>&1") == 0:
                    available.append(player)
            
            if available:
                print(f"✅ 대체 플레이어 사용 가능: {', '.join(available)}")
                return True
            else:
                print("❌ 사용 가능한 오디오 플레이어 없음")
                return False
        
        if os.system("aplay -l >/dev/null 2>&1") != 0:
            print("❌ 오디오 장치를 찾을 수 없습니다.")
            print("💡 해결방법: sudo usermod -a -G audio $USER")
            return False
            
    elif system == "darwin":
        if os.system("which afplay >/dev/null 2>&1") != 0:
            print("❌ afplay를 찾을 수 없습니다.")
            return False
            
    elif system == "windows":
        pass
    
    print("✅ 오디오 시스템 정상")
    return True

def speak_korean(text, test_mode=False):
    """한국어 텍스트를 음성으로 변환 및 재생"""
    
    if not tts_client:
        if not test_mode:
            print("❌ Google Cloud TTS 클라이언트가 초기화되지 않았습니다.")
            print("💡 GOOGLE_APPLICATION_CREDENTIALS 환경변수를 설정하세요.")
        return False
    
    if not text or not text.strip():
        print("❌ 변환할 텍스트가 없습니다.")
        return False
    
    cleaned_text = clean_text(text)
    if not cleaned_text:
        print("❌ 정리된 텍스트가 없습니다.")
        return False
    
    if len(cleaned_text) > 4900:
        cleaned_text = cleaned_text[:4900] + "..."
        if not test_mode:
            print("⚠️  텍스트가 너무 길어서 일부만 재생됩니다.")
    
    timestamp = int(time.time())
    temp_filename = f"response_{timestamp}.wav"
    
    try:
        synthesis_input = texttospeech.SynthesisInput(text=cleaned_text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name="ko-KR-Wavenet-A",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=1.0,
            pitch=0.0,
            volume_gain_db=0.0
        )
        
        if not test_mode:
            print("🔄 음성 합성 중...")
        
        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        with open(temp_filename, "wb") as audio_file:
            audio_file.write(response.audio_content)
        
        if not test_mode:
            print(f"💾 음성 파일 저장: {temp_filename}")
        
        play_success = play_audio(temp_filename)
        
        if play_success:
            if not test_mode:
                print("✅ 음성 재생 성공")
            return True
        else:
            if not test_mode:
                print("❌ 음성 재생 실패")
            return False
            
    except Exception as e:
        error_msg = f"TTS 오류: {str(e)}"
        print(f"❌ {error_msg}")
        return False
        
    finally:
        cleanup_temp_file(temp_filename)

def cleanup_temp_file(filename, max_attempts=3):
    """임시 파일 안전하게 삭제"""
    if not os.path.exists(filename):
        return
    
    for attempt in range(max_attempts):
        try:
            time.sleep(0.5)
            os.remove(filename)
            print(f"🗑️  임시 파일 삭제: {filename}")
            return
        except Exception as e:
            if attempt < max_attempts - 1:
                print(f"⚠️  파일 삭제 재시도... ({attempt + 1}/{max_attempts})")
                time.sleep(1)
            else:
                print(f"❌ 임시 파일 삭제 실패: {e}")

def get_available_voices():
    """사용 가능한 한국어 음성 목록 조회"""
    if not tts_client:
        print("❌ TTS 클라이언트가 초기화되지 않음")
        return []
        
    try:
        print("🔍 사용 가능한 음성 목록 조회 중...")
        voices = tts_client.list_voices()
        korean_voices = []
        
        for voice in voices.voices:
            for lang_code in voice.language_codes:
                if lang_code.startswith('ko'):
                    korean_voices.append({
                        'name': voice.name,
                        'gender': voice.ssml_gender.name,
                        'language': lang_code
                    })
                    break
        
        return korean_voices
        
    except Exception as e:
        print(f"❌ 음성 목록 조회 오류: {e}")
        return []

def test_tts(test_text="안녕하세요. 음성 합성 테스트입니다."):
    """TTS 시스템 전체 테스트"""
    print("🧪 TTS 시스템 테스트 시작...")
    print("=" * 40)
    
    print("1️⃣ 오디오 시스템 테스트")
    if not test_audio_system():
        print("❌ 오디오 시스템 테스트 실패")
        return False
    
    print("\n2️⃣ Google Cloud TTS 인증 테스트")
    if not tts_client:
        print("❌ Google Cloud TTS 클라이언트 없음")
        return False
    
    print("\n3️⃣ 사용 가능한 음성 조회")
    voices = get_available_voices()
    if voices:
        print(f"✅ {len(voices)}개의 한국어 음성 발견:")
        for voice in voices[:3]:
            print(f"   - {voice['name']} ({voice['gender']})")
    else:
        print("⚠️  한국어 음성을 찾을 수 없음")
    
    print(f"\n4️⃣ 음성 합성 및 재생 테스트")
    print(f"📝 테스트 텍스트: '{test_text}'")
    
    success = speak_korean(test_text, test_mode=True)
    
    print("=" * 40)
    if success:
        print("🎉 TTS 시스템 테스트 성공!")
        return True
    else:
        print("❌ TTS 시스템 테스트 실패")
        return False

# 모듈 테스트용 메인 함수
if __name__ == "__main__":
    print("🎤 TTS 모듈 단독 테스트")
    print("=" * 50)
    
    print("🔧 환경 확인:")
    print(f"   - Google Cloud 인증: {'✅' if tts_client else '❌'}")
    print(f"   - 운영체제: {platform.system()}")
    
    test_result = test_tts()
    
    if test_result:
        print("\n🎯 추가 테스트를 원하면 다른 텍스트를 입력하세요:")
        while True:
            user_text = input("텍스트 입력 (종료: 'quit'): ").strip()
            if user_text.lower() in ['quit', '종료', 'exit']:
                break
            if user_text:
                speak_korean(user_text)
    
    print("👋 테스트 완료")
