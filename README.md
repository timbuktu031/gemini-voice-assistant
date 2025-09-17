# 📄 README.md
# 🤖 Raspberry Pi Voice Assistant with Gemini AI

라즈베리파이용 한국어 음성 AI 비서입니다.

## 📋 기능
- 🎤 음성 인식 (Google Cloud Speech-to-Text)
- 🔊 한국어 음성 합성 (Google Cloud TTS)
- 🧠 AI 대화 (Gemini 2.0 Flash)
- 🔍 실시간 정보 검색 (네이버 API, 날씨 API)
- 💬 대화 히스토리 관리
- 🖥️ GUI 인터페이스

## 📁 프로젝트 구조
```
pi_voice_assistant/
├── main.py                 # 메인 실행 파일
├── config.py              # 설정 및 환경변수
├── modules/
│   ├── __init__.py
│   ├── searcher.py        # 실시간 검색
│   ├── history.py         # 대화 히스토리
│   ├── gui.py             # GUI 인터페이스
│   ├── tts.py             # 음성 합성
│   └── gemini_client.py   # Gemini API
├── utils/
│   ├── __init__.py
│   └── text_utils.py      # 텍스트 처리
├── requirements.txt
└── README.md
```

## 🚀 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/timbuktu031/PiVoiceAssistant.git
cd pi_voice_assistant
```

### 2. 가상환경 생성
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# 실제 API 키 입력
nano .env
```

### 5. Google Cloud 인증 설정
```bash
# 서비스 계정 키 파일 다운로드 후
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
```

## 🔧 API 키 발급

### Gemini API
1. [Google AI Studio](https://aistudio.google.com) 접속
2. API 키 발급
3. `GEMINI_API_KEY`에 설정

### 네이버 개발자 API
1. [네이버 개발자센터](https://developers.naver.com) 접속
2. 애플리케이션 등록
3. 검색 API 활용신청
4. `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` 설정

### Google Cloud TTS
1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 프로젝트 생성 및 Text-to-Speech API 활성화
3. 서비스 계정 생성 및 키 다운로드
4. `GOOGLE_APPLICATION_CREDENTIALS` 경로 설정

### OpenWeatherMap API (선택사항)
1. [OpenWeatherMap](https://openweathermap.org/api) 접속
2. 무료 API 키 발급
3. `WEATHER_API_KEY` 설정

## 🏃‍♂️ 실행 방법
```bash
python main.py
```

## 📝 사용법
- 터미널에서 질문 입력
- GUI 창에서 대화 내용 확인
- 음성으로 답변 재생

### 명령어
- `히스토리` 또는 `history`: 대화 기록 보기
- `초기화` 또는 `clear`: 히스토리 초기화
- `검색테스트`: 실시간 검색 테스트
- `종료` 또는 `exit`: 프로그램 종료

## 🔧 설정 변경
`config.py`에서 다음 설정을 변경할 수 있습니다:
- `max_history`: 최대 대화 기록 수 (기본 10개)
- `max_summary_length`: 요약할 텍스트 길이 (기본 300자)
- `request_timeout`: API 요청 타임아웃 (기본 10초)

## 🐛 문제 해결

### 한국어 폰트 문제
```bash
# Ubuntu/Debian
sudo apt-get install fonts-nanum

# 또는 시스템 설정에서 한국어 폰트 설치
```

### 오디오 재생 문제 (라즈베리파이)
```bash
# ALSA 오디오 시스템 설치
sudo apt-get install alsa-utils

# 오디오 장치 확인
aplay -l
```

### 권한 문제
```bash
# 오디오 그룹에 사용자 추가
sudo usermod -a -G audio $USER
```

## 📦 모듈별 설명

### `modules/searcher.py`
- 네이버 뉴스/웹 검색
- 날씨 정보 조회
- 현재 시간 정보

### `modules/history.py`
- JSON 파일로 대화 저장
- 컨텍스트 생성
- 히스토리 관리

### `modules/gui.py`
- Tkinter 기반 GUI
- 실시간 메시지 표시
- 히스토리 내보내기

### `modules/tts.py`
- Google Cloud TTS
- 한국어 음성 합성
- 오디오 파일 재생

### `modules/gemini_client.py`
- Gemini API 클라이언트
- 응답 생성
- 텍스트 요약

## 🤝 기여하기
1. Fork 프로젝트
2. Feature 브랜치 생성
3. 커밋 후 Push
4. Pull Request 생성

## 📄 라이선스
MIT License
