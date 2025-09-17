#!/bin/bash

# 프로젝트 폴더 생성 스크립트
# 사용법: bash create_project.sh

echo "🚀 라즈베리파이 음성 AI 비서 프로젝트 폴더 생성 중..."

# 메인 프로젝트 폴더 생성
mkdir -p pi_voice_assistant
cd pi_voice_assistant

# 서브 폴더 생성
mkdir -p modules
mkdir -p utils

# __init__.py 파일 생성
touch modules/__init__.py
touch utils/__init__.py

echo "📁 폴더 구조 생성 완료!"
echo ""
echo "📝 이제 다음 파일들을 생성해야 합니다:"
echo ""
echo "1️⃣  config.py"
echo "2️⃣  main.py"
echo "3️⃣  utils/text_utils.py"
echo "4️⃣  modules/searcher.py"
echo "5️⃣  modules/history.py"
echo "6️⃣  modules/gemini_client.py"
echo "7️⃣  modules/gui.py"
echo "8️⃣  modules/tts.py"
echo "9️⃣  requirements.txt"
echo "🔟 .env.example"
echo ""
echo "📋 생성된 폴더 구조:"
tree . 2>/dev/null || find . -type d | sed 's/[^/]*\//|  /g;s/| *\([^| ]\)/+--\1/'

echo ""
echo "✅ 프로젝트 폴더 생성 완료!"
echo "이제 각 파일에 코드를 복사해 넣으세요."