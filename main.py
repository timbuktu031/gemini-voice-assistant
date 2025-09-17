# ===========================================
# 📄 main.py - 메인 실행 파일
# ===========================================
import threading
import time
from utils.text_utils import setup_encoding, safe_input, detect_real_time_query
from modules.searcher import RealTimeSearcher
from modules.history import ConversationHistory
from modules.gemini_client import GeminiClient
from modules.gui import GeminiGUI, send_to_gui
from modules.tts import speak_korean
from config import app_config

def main():
    """메인 함수"""
    # 초기 설정
    setup_encoding()
    
    # 객체 초기화
    searcher = RealTimeSearcher()
    history = ConversationHistory()
    gemini = GeminiClient()
    
    # GUI 스레드 시작
    gui_thread = threading.Thread(target=lambda: GeminiGUI(history).run(), daemon=True)
    gui_thread.start()
    
    time.sleep(2)
    
    print("🤖 Gemini AI 음성 비서 시작")
    print(f"📚 {len(history.conversations)}개의 이전 대화 기억 중")
    print("🔍 실시간 검색: 뉴스, 날씨, 시간 등")
    print("\n명령어: 히스토리, 초기화, 검색테스트, 종료")
    
    while True:
        try:
            user_input = safe_input("\n질문: ")
            
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "종료"]:
                print("👋 프로그램을 종료합니다.")
                break
            
            # 명령어 처리
            if user_input.lower() in ["히스토리", "history"]:
                print(f"\n=== 대화 히스토리 ({len(history.conversations)}개) ===")
                for i, conv in enumerate(history.conversations[-3:], 1):
                    print(f"{i}. Q: {conv['question'][:30]}...")
                    print(f"   A: {conv['answer'][:50]}...")
                continue
            
            # 일반 질문 처리
            send_to_gui("질문", user_input)
            
            # 실시간 정보 수집
            full_prompt = history.get_context()
            if detect_real_time_query(user_input):
                real_time_info = get_real_time_info(searcher, user_input)
                if real_time_info:
                    full_prompt += "최신 정보:\n"
                    for info in real_time_info:
                        full_prompt += f"- {info}\n"
                    full_prompt += "\n위 정보를 참고해서 답변해주세요.\n\n"
            
            full_prompt += f"질문: {user_input}"
            
            # Gemini로 답변 생성
            answer = gemini.generate_response(full_prompt)
            history.add_conversation(user_input, answer)
            
            send_to_gui("답변", answer)
            print(f"\n📝 답변: {answer}\n")
            
            # 음성 출력
            if len(answer) > app_config.max_summary_length:
                summary = gemini.summarize_text(answer)
                send_to_gui("요약", summary)
                speak_korean(summary)
            else:
                speak_korean(answer)
                
        except KeyboardInterrupt:
            print("\n👋 프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 오류: {e}")

def get_real_time_info(searcher, prompt):
    """실시간 정보 수집"""
    results = []
    
    if any(word in prompt.lower() for word in ["시간", "지금", "현재"]):
        time_info = searcher.get_current_time_info()
        results.append(f"현재 시간: {time_info['current_time']}")
    
    if "날씨" in prompt.lower():
        weather = searcher.get_weather()
        if isinstance(weather, dict):
            results.append(f"날씨: {weather['temperature']}°C, {weather['description']}")
    
    if "뉴스" in prompt.lower():
        news = searcher.search_news("한국")
        if news:
            results.extend([f"뉴스: {item}" for item in news[:2]])
    
    if not results:
        web_results = searcher.search_web(prompt)
        results.extend(web_results[:2])
    
    return results

if __name__ == "__main__":
    main()