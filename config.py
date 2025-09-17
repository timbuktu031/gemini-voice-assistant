# config.py
import os
from dataclasses import dataclass

@dataclass
class APIKeys:
    """API 키 관리"""
    naver_client_id: str = None
    naver_client_secret: str = None
    weather_api_key: str = None
    gemini_api_key: str = None
    google_cloud_credentials: str = None
    
    def __post_init__(self):
        """환경변수에서 자동 로드"""
        self.naver_client_id = os.getenv("NAVER_CLIENT_ID")
        self.naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.google_cloud_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        # Gemini API 키가 있으면 자동으로 configure
        if self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
            except ImportError:
                pass

@dataclass
class AppConfig:
    """애플리케이션 설정"""
    max_history: int = 10
    history_file: str = "conversation_history.json"
    temp_audio_prefix: str = "response_"
    gui_update_interval: int = 100
    request_timeout: int = 10
    max_summary_length: int = 300
    
    # TTS 설정
    tts_speaking_rate: float = 1.0
    tts_pitch: float = 0.0
    tts_volume_gain_db: float = 0.0
    tts_voice_name: str = "ko-KR-Wavenet-A"
    
    # GUI 설정
    gui_width: int = 900
    gui_height: int = 700
    gui_bg_color: str = '#f0f0f0'

# 전역 설정 객체
api_keys = APIKeys()
app_config = AppConfig()

def check_required_apis():
    """필수 API 키 확인"""
    missing_apis = []
    
    if not api_keys.gemini_api_key:
        missing_apis.append("GEMINI_API_KEY")
    
    if not api_keys.google_cloud_credentials:
        missing_apis.append("GOOGLE_APPLICATION_CREDENTIALS")
    
    if missing_apis:
        print("⚠️  다음 API 키가 설정되지 않았습니다:")
        for api in missing_apis:
            print(f"   - {api}")
        return False
    
    return True

def print_config_status():
    """설정 상태 출력"""
    print("📋 API 키 설정 상태:")
    print(f"   Gemini API: {'✅' if api_keys.gemini_api_key else '❌'}")
    print(f"   Google Cloud: {'✅' if api_keys.google_cloud_credentials else '❌'}")
    print(f"   네이버 API: {'✅' if api_keys.naver_client_id and api_keys.naver_client_secret else '❌'}")
    print(f"   날씨 API: {'✅' if api_keys.weather_api_key else '❌'}")