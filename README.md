# 🎙️ Gemini 음성 비서

Google STT + Gemini + GTTS 기반의 자연스러운 한국어 음성 비서입니다.  
사용자가 말하면 자동으로 녹음하고, Gemini에게 질문을 전달해 음성으로 응답해줍니다.

---

## 🚀 기능

- 🎧 **VAD 기반 자동 녹음**: 말소리 감지 후 녹음 시작, 침묵 시 자동 종료
- 🧠 **Google STT**: 음성을 텍스트로 변환
- 🤖 **Gemini API**: 텍스트를 기반으로 응답 생성
- 🔈 **GTTS + 재생**: 응답을 음성으로 변환하고 출력
- 🔐 **환경변수 기반 API 키 관리**: 보안 강화

---

## 📦 설치 방법

먼저 가상환경을 만들어야 합니다.  
sudo apt update  
sudo apt install python3-full  
python3 -m venv venv  
source venv/bin/activate  

```bash
git clone https://github.com/timbuktu031/gemini-voice-assistant.git
cd gemini-voice-assistant
./install.sh
