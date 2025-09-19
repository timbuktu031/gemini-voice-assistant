import os
from dotenv import load_dotenv
from modules import recorder, stt_google, gemini_api, tts_google, player

# 🔐 환경변수 로드
load_dotenv()

def run():
    print("🎤 Gemini 음성 비서 시작! 'Ctrl+C'로 종료하세요.\n")
    while True:
        try:
            # 1. 음성 녹음 (VAD 기반 자동 시작/종료)
            recorder.record_audio()

            # 2. STT로 텍스트 변환
            text = stt_google.recognize()

            # 3. 인식 실패 시 다시 시도
            if text is None or len(text.strip()) < 2:
                print("❗ 음성을 인식하지 못했어요. 다시 말씀해주세요.\n")
                continue

            print(f"🗣️ 질문: {text}")

            # 4. Gemini에게 질문
            reply = gemini_api.get_response(text)

            # 5. TTS로 음성 변환
            tts_google.speak(reply)

            # 6. 음성 출력
            player.play_response()

            print("✅ 응답 완료. 다음 질문을 해주세요!\n")

        except KeyboardInterrupt:
            print("\n👋 종료합니다. 다음에 또 만나요!")
            break
        except Exception as e:
            print(f"⚠️ 오류 발생: {e}")
            continue

if __name__ == "__main__":
    run()
