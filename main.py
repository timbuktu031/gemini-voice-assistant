# main.py - 수정된 버전 (GUI 문제 해결)
import threading
import time
import sys
import io
import locale
import re
import queue
import os

# GUI 통신용 전역 큐
gui_queue = queue.Queue()

# 한글 입출력 설정
def setup_encoding():
    """한글 인코딩 설정"""
    try:
        locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass

    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stdin, 'buffer'):
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')

def safe_input(prompt):
    """안전한 입력"""
    try:
        user_input = input(prompt)
        if isinstance(user_input, bytes):
            user_input = user_input.decode('utf-8', errors='replace')
        
        return user_input.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore').strip()
    except Exception as e:
        print(f"입력 오류: {e}")
        return ""

def detect_real_time_query(prompt):
    """실시간 검색 필요 판단"""
    keywords = ["최신", "지금", "현재", "오늘", "뉴스", "날씨", "시간", "요즘"]
    return any(keyword in prompt.lower() for keyword in keywords)

# 초기 설정
setup_encoding()

# 모듈 import
from modules.searcher import RealTimeSearcher
from modules.history import ConversationHistory
from modules.gemini_client import GeminiClient
from modules.tts import speak_korean, test_tts

def send_to_gui(msg_type, content):
    """GUI에 메시지 전송"""
    try:
        gui_queue.put((msg_type, content), block=False)
        print(f"[GUI] {msg_type}: {content}")
    except Exception as e:
        print(f"GUI 전송 오류: {e}")

def check_display_available():
    """디스플레이 환경 확인"""
    try:
        if os.name == 'posix':  # Linux/Unix 시스템
            display = os.environ.get('DISPLAY')
            if not display:
                print("⚠️  DISPLAY 환경변수가 설정되지 않았습니다.")
                return False
        
        # tkinter 테스트
        import tkinter as tk
        test_root = tk.Tk()
        test_root.withdraw()  # 창을 숨김
        test_root.destroy()
        return True
    except Exception as e:
        print(f"⚠️  GUI 환경 확인 실패: {e}")
        return False

def start_gui(history):
    """GUI 시작 (별도 함수로 분리)"""
    try:
        from modules.gui import GeminiGUI
        gui = GeminiGUI(history)
        gui.run()
    except Exception as e:
        print(f"❌ GUI 시작 실패: {e}")
        print("💡 터미널 모드로 계속 실행됩니다.")

def get_real_time_info(searcher, prompt):
    """실시간 정보 수집"""
    results = []
    
    if any(word in prompt.lower() for word in ["시간", "지금", "현재"]):
        time_info = searcher.get_current_time_info()
        results.append(f"현재 시간: {time_info['current_time']} ({time_info['weekday']})")
    
    if "날씨" in prompt.lower():
        weather = searcher.get_weather()
        if isinstance(weather, dict):
            results.append(f"날씨: {weather['temperature']}°C, {weather['description']}, 체감온도 {weather['feels_like']}°C")
        elif isinstance(weather, list):
            results.extend(weather[:1])
    
    if "뉴스" in prompt.lower():
        news = searcher.search_news("한국")
        if news:
            results.extend([f"뉴스: {item}" for item in news[:2]])
    
    if not results or len(results) < 2:
        web_results = searcher.search_web(prompt)
        results.extend(web_results[:3-len(results)])
    
    return results

def main():
    """메인 함수"""
    print("🤖 Gemini AI 음성 비서 시작")
    print("=" * 50)
    
    # 객체 초기화
    print("🔧 시스템 초기화 중...")
    
    try:
        searcher = RealTimeSearcher()
        history = ConversationHistory()
        gemini = GeminiClient()
        
        print(f"✅ 시스템 초기화 완료")
        print(f"📚 {len(history.conversations)}개의 이전 대화 기억 중")
        print("🔍 실시간 검색: 뉴스, 날씨, 시간 등")
        
        # GUI 시작 시도
        gui_available = check_display_available()
        gui_started = False
        
        if gui_available:
            try:
                print("🖥️  GUI 환경 감지됨, GUI 창을 시작합니다...")
                gui_thread = threading.Thread(target=start_gui, args=(history,), daemon=True)
                gui_thread.start()
                gui_started = True
                time.sleep(2)  # GUI 시작 대기
                print("✅ GUI 창이 시작되었습니다.")
            except Exception as e:
                print(f"⚠️  GUI 시작 실패: {e}")
                print("💡 터미널 모드로 계속 실행됩니다.")
        else:
            print("💻 터미널 모드로 실행됩니다.")
            print("💡 GUI를 사용하려면 다음을 확인하세요:")
            print("   - X11 디스플레이 환경")
            print("   - DISPLAY 환경변수")  
            print("   - tkinter 패키지 설치")
        
        print("")
        print("📝 명령어:")
        print("  - 히스토리 또는 history: 대화 기록 보기")
        print("  - 초기화 또는 clear: 히스토리 초기화") 
        print("  - 검색테스트: 실시간 검색 테스트")
        print("  - tts테스트: 음성 합성 테스트")
        print("  - 종료 또는 exit: 프로그램 종료")
        print("")
        
        # API 연결 테스트
        print("🧪 API 연결 테스트...")
        gemini.test_connection()
        searcher.test_apis()
        print("")
        
    except Exception as e:
        print(f"❌ 초기화 오류: {e}")
        print("상세 오류:", str(e))
        import traceback
        traceback.print_exc()
        return
    
    # 메인 루프
    while True:
        try:
            user_input = safe_input("💬 질문: ")
            
            if not user_input:
                continue
            
            # 종료 명령
            if user_input.lower() in ["exit", "종료", "quit"]:
                print("👋 프로그램을 종료합니다.")
                break
            
            # 명령어 처리
            if user_input.lower() in ["히스토리", "history"]:
                print(f"\n=== 대화 히스토리 ({len(history.conversations)}개) ===")
                if not history.conversations:
                    print("저장된 대화가 없습니다.")
                else:
                    for i, conv in enumerate(history.conversations[-5:], 1):
                        timestamp = conv['timestamp'][:19].replace('T', ' ')
                        print(f"{i}. [{timestamp}] Q: {conv['question'][:50]}...")
                        print(f"   A: {conv['answer'][:80]}...")
                        print()
                continue
            
            if user_input.lower() in ["초기화", "clear"]:
                confirm = safe_input("정말로 히스토리를 삭제하시겠습니까? (y/N): ")
                if confirm.lower() in ['y', 'yes']:
                    history.clear_history()
                    send_to_gui("history_update", "")
                    print("✅ 히스토리 초기화 완료")
                continue
            
            if user_input.lower() in ["검색테스트"]:
                print("🔍 실시간 검색 테스트...")
                time_info = searcher.get_current_time_info()
                print(f"⏰ {time_info['current_time']} ({time_info['weekday']})")
                
                weather = searcher.get_weather()
                if isinstance(weather, dict):
                    print(f"🌤️ {weather['temperature']}°C, {weather['description']}")
                
                news = searcher.search_news("AI")
                if news:
                    print(f"📰 뉴스: {news[0]}")
                continue
            
            if user_input.lower() in ["tts테스트"]:
                print("🎤 TTS 테스트...")
                test_result = test_tts()
                if test_result:
                    print("✅ TTS 테스트 성공")
                else:
                    print("❌ TTS 테스트 실패")
                continue
            
            # 일반 질문 처리
            print(f"\n❓ 질문: {user_input}")
            send_to_gui("질문", user_input)
            
            # 컨텍스트 생성
            context = history.get_context()
            full_prompt = context
            
            # 실시간 정보 추가
            if detect_real_time_query(user_input):
                print("🔍 실시간 정보 검색 중...")
                send_to_gui("status", "🔍 실시간 정보 검색 중...")
                real_time_info = get_real_time_info(searcher, user_input)
                
                if real_time_info:
                    full_prompt += "최신 정보:\n"
                    for info in real_time_info:
                        full_prompt += f"- {info}\n"
                    full_prompt += "\n위 정보를 참고해서 답변해주세요.\n\n"
                    print(f"✅ {len(real_time_info)}개의 실시간 정보 수집 완료")
            
            full_prompt += f"질문: {user_input}"
            
            # Gemini로 답변 생성
            print("🤔 답변 생성 중...")
            send_to_gui("status", "🤔 답변 생성 중...")
            answer = gemini.generate_response(full_prompt)
            
            # 대화 저장
            history.add_conversation(user_input, answer)
            send_to_gui("답변", answer)
            send_to_gui("history_update", "")
            
            print(f"\n🤖 답변: {answer}\n")
            
            # 음성 출력
            max_length = 300
            if len(answer) > max_length:
                print("📄 답변이 길어서 요약 중...")
                send_to_gui("status", "📄 요약 중...")
                summary = gemini.summarize_text(answer)
                print(f"📋 요약: {summary}")
                send_to_gui("요약", summary)
                
                # 요약본 음성 출력
                print("🔊 요약 음성 재생 중...")
                send_to_gui("status", "🔊 음성 재생 중...")
                speak_korean(summary)
            else:
                # 전체 답변 음성 출력
                print("🔊 음성 재생 중...")
                send_to_gui("status", "🔊 음성 재생 중...")
                speak_korean(answer)
            
            send_to_gui("status", "✅ 준비 완료")
            print("=" * 50)
                
        except KeyboardInterrupt:
            print("\n👋 프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            continue

if __name__ == "__main__":
    main()
