#!/bin/bash

echo "🔧 Gemini 음성 비서 설치 시작..."

# 시스템 패키지 설치
echo "📦 필수 시스템 패키지 설치 중..."
sudo apt update
sudo apt install -y python3 python3-pip portaudio19-dev

# 파이썬 패키지 설치
echo "🐍 Python 패키지 설치 중..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# .env 템플릿 생성
echo "🔐 .env 파일 생성 중..."
if [ ! -f .env ]; then
  echo "GEMINI_API_KEY=여기에_당신의_API_키를_입력하세요" > .env
  echo "✅ .env 파일이 생성되었습니다. API 키를 입력해주세요!"
else
  echo "⚠️ .env 파일이 이미 존재합니다. 건너뜁니다."
fi

echo "✅ 설치 완료! 이제 main.py를 실행하세요:"
echo "    python3 main.py"
