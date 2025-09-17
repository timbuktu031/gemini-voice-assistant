import google.generativeai as genai
from google.cloud import texttospeech
import os
import re
import platform
import time
import sys
import io
import locale
import tkinter as tk
from tkinter import scrolledtext
import threading
import queue
from datetime import datetime
import tkinter.font as tkFont
import json
import requests
from bs4 import BeautifulSoup
import pytz

# 한글 입출력 인코딩 설정
try:
    locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        pass

# 표준 입출력 UTF-8 설정
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stdin, 'buffer'):
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')

# API 설정
genai.configure()
model = genai.GenerativeModel("gemini-2.0-flash-exp")
tts_client = texttospeech.TextToSpeechClient()

# GUI 통신용 큐
gui_queue = queue.Queue()


class RealTimeSearcher:
    """실시간 정보 검색 클래스"""
    def __init__(self):
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        
        # 네이버 API 키
        self.naver_client_id = os.getenv("NAVER_CLIENT_ID")
        self.naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")

    def search_news(self, query, language="ko"):
        """뉴스 검색"""
        # 1순위: 네이버 뉴스 API
        naver_results = self.search_naver(query, search_type="news", display=3, sort="date")
        if naver_results:
            return naver_results

        # 2순위: 웹 검색 fallback
        return self.search_web(f"{query} 뉴스")

    def get_current_time_info(self):
        """현재 시간 정보"""
        try:
            # 한국 시간
            kst = pytz.timezone('Asia/Seoul')
            now = datetime.now(kst)
            
            return {
                'current_time': now.strftime('%Y년 %m월 %d일 %H시 %M분'),
                'weekday': now.strftime('%A'),
                'date': now.strftime('%Y-%m-%d'),
                'time': now.strftime('%H:%M:%S')
            }
        except Exception as e:
            print(f"시간 정보 오류: {e}")
            return {'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    def get_weather(self, city="Seoul"):
        """날씨 정보"""
        if not self.weather_api_key:
            return ["날씨 API 키가 설정되지 않았습니다."]
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': self.weather_api_key,
                'units': 'metric',
                'lang': 'kr'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                desc = data['weather'][0]['description']
                humidity = data['main']['humidity']
                
                return {
                    'temperature': temp,
                    'description': desc,
                    'humidity': humidity,
                    'city': city
                }
            else:
                return ["날씨 정보를 가져올 수 없습니다."]
                
        except Exception as e:
            print(f"날씨 정보 오류: {e}")
            return ["날씨 정보 조회 중 오류 발생"]

    def search_naver(self, query, search_type="news", display=3, sort="sim"):
        """네이버 검색 API 사용"""
        if not (self.naver_client_id and self.naver_client_secret):
            return None

        base_url = "https://openapi.naver.com/v1/search/"
        endpoint = "news.json" if search_type == "news" else "webkr.json"
        url = base_url + endpoint

        headers = {
            "X-Naver-Client-Id": self.naver_client_id,
            "X-Naver-Client-Secret": self.naver_client_secret
        }
        params = {"query": query, "display": display, "sort": sort}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                results = []
                for item in items:
                    title = item["title"].replace("<b>", "").replace("</b>", "")
                    link = item["link"]
                    desc = item["description"].replace("<b>", "").replace("</b>", "")
                    if search_type == "news":
                        results.append(f"[네이버뉴스] {title} - {desc}")
                    else:
                        results.append(f"{title} - {desc} ({link})")
                return results if results else None
            else:
                print(f"네이버 검색 오류: {response.status_code}")
                return None
        except Exception as e:
            print(f"네이버 검색 예외: {e}")
            return None

    def search_web(self, query):
        """웹 검색"""
        # 네이버 웹 검색 우선 시도
        naver_results = self.search_naver(query, search_type="web", display=3)
        if naver_results:
            return naver_results

        # 구글 검색 fallback
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}&hl=ko"
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            for result in soup.find_all('h3', limit=3):
                title = result.get_text()
                if title and len(title) > 10:
                    results.append(title)
            return results if results else [f"{query}에 대한 정보를 찾을 수 없습니다."]
        except Exception as e:
            print(f"웹 검색 오류: {e}")
            return [f"{query} 검색 중 오류 발생"]


class ConversationHistory:
    """대화 히스토리 관리"""
    def __init__(self, history_file="conversation_history.json", max_history=10):
        self.history_file = history_file
        self.max_history = max_history
        self.conversations = []
        self.load_history()
    
    def add_conversation(self, question, answer):
        """대화 추가"""
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer
        }
        self.conversations.append(conversation)
        
        if len(self.conversations) > self.max_history:
            self.conversations = self.conversations[-self.max_history:]
        
        self.save_history()
    
    def get_context(self):
        """대화 컨텍스트 생성"""
        if not self.conversations:
            return ""
        
        context = "이전 대화 내용:\n"
        for conv in self.conversations[-3:]:  # 최근 3개만 참조
            context += f"Q: {conv['question']}\nA: {conv['answer'][:150]}...\n\n"
        
        context += "위 내용을 참고해서 답변해주세요.\n\n"
        return context
    
    def save_history(self):
        """히스토리 저장"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"히스토리 저장 오류: {e}")
    
    def load_history(self):
        """히스토리 로드"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.conversations = json.load(f)
        except Exception as e:
            print(f"히스토리 로드 오류: {e}")
            self.conversations = []
    
    def clear_history(self):
        """히스토리 초기화"""
        self.conversations = []
        self.save_history()
    
    def get_history_summary(self):
        """히스토리 요약"""
        if not self.conversations:
            return "저장된 대화 없음"
        
        total = len(self.conversations)
        latest = self.conversations[-1]['timestamp'][:19].replace('T', ' ')
        return f"총 {total}개 대화, 최근: {latest}"


class GeminiGUI:
    """GUI 인터페이스"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gemini AI 음성 비서")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        self.setup_fonts()
        self.create_widgets()
        self.check_queue()
    
    def setup_fonts(self):
        """폰트 설정"""
        available_fonts = list(tkFont.families())
        korean_fonts = ['NanumGothic', 'NanumBarunGothic', 'DejaVu Sans', 'TkDefaultFont']
        
        selected_font = 'TkDefaultFont'
        for font in korean_fonts:
            if font in available_fonts:
                selected_font = font
                break
        
        self.title_font = (selected_font, 18, 'bold')
        self.content_font = (selected_font, 11)
        self.bold_font = (selected_font, 11, 'bold')
        self.status_font = (selected_font, 10)
        self.small_font = (selected_font, 9)
    
    def create_widgets(self):
        """위젯 생성"""
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 제목
        title_label = tk.Label(
            main_frame, 
            text="🤖 Gemini AI 음성 비서", 
            font=self.title_font,
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 10))
        
        # 히스토리 정보
        history_frame = tk.Frame(main_frame, bg='#e8f4f8', relief=tk.RAISED, bd=1)
        history_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.history_info_label = tk.Label(
            history_frame,
            text=conversation_history.get_history_summary(),
            font=self.status_font,
            bg='#e8f4f8',
            fg='#2c3e50'
        )
        self.history_info_label.pack(pady=5)
        
        # 히스토리 버튼
        button_frame = tk.Frame(history_frame, bg='#e8f4f8')
        button_frame.pack(pady=5)
        
        tk.Button(
            button_frame,
            text="히스토리 초기화",
            command=self.clear_history,
            bg='#e74c3c',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="히스토리 내보내기",
            command=self.export_history,
            bg='#3498db',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        # 대화 영역
        self.text_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=self.content_font,
            bg='white'
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 상태 영역
        status_frame = tk.Frame(main_frame, bg='#f0f0f0')
        status_frame.pack(fill=tk.X)
        
        self.status_label = tk.Label(
            status_frame,
            text="💬 터미널에서 질문을 입력하세요",
            font=self.status_font,
            bg='#f0f0f0',
            fg='#7f8c8d'
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.time_label = tk.Label(
            status_frame,
            text="",
            font=self.status_font,
            bg='#f0f0f0',
            fg='#7f8c8d'
        )
        self.time_label.pack(side=tk.RIGHT)
        
        # 텍스트 태그 설정
        self.text_area.tag_configure("question", foreground="#2980b9", font=self.bold_font)
        self.text_area.tag_configure("answer", foreground="#2a2a2b")
        self.text_area.tag_configure("summary", foreground="#e67e22")
        self.text_area.tag_configure("status", foreground="#4d4d4d")
        self.text_area.tag_configure("search", foreground="#27ae60", font=self.bold_font)
        self.text_area.tag_configure("timestamp", foreground="#424242", font=self.small_font)
        
        self.add_message("시스템", "Gemini AI 음성 비서가 준비되었습니다.", "status")
    
    def add_message(self, msg_type, content, tag="answer"):
        """메시지 추가"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.text_area.insert(tk.END, f"[{current_time}] ", "timestamp")
        
        if msg_type == "질문":
            self.text_area.insert(tk.END, f"질문: {content}\n", "question")
        elif msg_type == "답변":
            self.text_area.insert(tk.END, f"답변: {content}\n", "answer")
        elif msg_type == "요약":
            self.text_area.insert(tk.END, f"요약: {content}\n", "summary")
        elif msg_type == "검색":
            self.text_area.insert(tk.END, f"🔍 {content}\n", "search")
        else:
            self.text_area.insert(tk.END, f"{content}\n", tag)
        
        self.text_area.insert(tk.END, "\n")
        self.text_area.see(tk.END)
        self.text_area.update()
    
    def update_status(self, status_text):
        """상태 업데이트"""
        self.status_label.config(text=status_text)
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.update()
    
    def update_history_info(self):
        """히스토리 정보 업데이트"""
        self.history_info_label.config(text=conversation_history.get_history_summary())
    
    def clear_history(self):
        """히스토리 초기화"""
        conversation_history.clear_history()
        self.update_history_info()
        self.add_message("시스템", "대화 히스토리가 초기화되었습니다.", "status")
    
    def export_history(self):
        """히스토리 내보내기"""
        try:
            export_file = f"history_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(export_file, 'w', encoding='utf-8') as f:
                f.write("=== 대화 히스토리 ===\n\n")
                for i, conv in enumerate(conversation_history.conversations, 1):
                    f.write(f"[{i}] {conv['timestamp']}\n")
                    f.write(f"Q: {conv['question']}\n")
                    f.write(f"A: {conv['answer']}\n")
                    f.write("-" * 50 + "\n\n")
            
            self.add_message("시스템", f"히스토리가 {export_file}로 저장되었습니다.", "status")
        except Exception as e:
            self.add_message("시스템", f"내보내기 실패: {e}", "status")
    
    def check_queue(self):
        """큐 확인"""
        try:
            while True:
                msg_type, content = gui_queue.get_nowait()
                if msg_type == "status":
                    self.update_status(content)
                elif msg_type == "history_update":
                    self.update_history_info()
                else:
                    self.add_message(msg_type, content)
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_queue)
    
    def run(self):
        """GUI 실행"""
        self.root.mainloop()


# 전역 객체 생성
real_time_searcher = RealTimeSearcher()
conversation_history = ConversationHistory()


def start_gui():
    """GUI 시작"""
    gui = GeminiGUI()
    gui.run()


def send_to_gui(msg_type, content):
    """GUI에 메시지 전송"""
    gui_queue.put((msg_type, content))


def clean_text(text):
    """텍스트 정리"""
    try:
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='replace')
        
        text = text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        cleaned = re.sub(r'[^\w\s가-힣.,?!]', '', text)
        return cleaned.strip()
    except Exception as e:
        print(f"텍스트 정리 오류: {e}")
        return ""


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


def get_real_time_info(prompt):
    """실시간 정보 수집"""
    results = []
    
    # 시간 정보
    if any(word in prompt.lower() for word in ["시간", "지금", "현재"]):
        time_info = real_time_searcher.get_current_time_info()
        results.append(f"현재 시간: {time_info['current_time']}")
    
    # 날씨 정보
    if "날씨" in prompt.lower():
        weather = real_time_searcher.get_weather()
        if isinstance(weather, dict):
            results.append(f"날씨: {weather['temperature']}°C, {weather['description']}")
        elif isinstance(weather, list):
            results.extend(weather[:2])
    
    # 뉴스 정보
    if "뉴스" in prompt.lower():
        news = real_time_searcher.search_news("한국")
        if news:
            results.extend([f"뉴스: {item}" for item in news[:2]])
    
    # 일반 검색
    if not results:
        web_results = real_time_searcher.search_web(prompt)
        results.extend(web_results[:2])
    
    return results


def ask_gemini(prompt):
    """Gemini에게 질문"""
    try:
        need_real_time = detect_real_time_query(prompt)
        context = conversation_history.get_context()
        
        full_prompt = ""
        
        # 히스토리 추가
        if context:
            full_prompt += context
            send_to_gui("검색", f"이전 대화 {len(conversation_history.conversations)}개 참조")
        
        # 실시간 정보 추가
        if need_real_time:
            send_to_gui("검색", "실시간 정보 검색 중...")
            real_time_info = get_real_time_info(prompt)
            
            if real_time_info:
                full_prompt += "최신 정보:\n"
                for info in real_time_info:
                    full_prompt += f"- {info}\n"
                full_prompt += "\n위 정보를 참고해서 답변해주세요.\n\n"
                
                send_to_gui("검색", f"검색 완료: {len(real_time_info)}개 정보")
        
        full_prompt += f"질문: {prompt}"
        
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        error_msg = f"Gemini API 오류: {e}"
        print(error_msg)
        send_to_gui("status", f"❌ {error_msg}")
        return "죄송합니다. 응답을 생성할 수 없습니다."


def summarize_text(text):
    """텍스트 요약"""
    try:
        prompt = f"다음 내용을 두 문장으로 요약해주세요:\n{text}"
        summary = model.generate_content(prompt)
        return summary.text
    except Exception as e:
        print(f"요약 오류: {e}")
        return text[:200] + "..." if len(text) > 200 else text


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
    
    temp_filename = f"response_{int(time.time())}.wav"
    
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


def main():
    """메인 함수"""
    # GUI 스레드 시작
    gui_thread = threading.Thread(target=start_gui, daemon=True)
    gui_thread.start()
    
    time.sleep(2)
    
    print("🤖 Gemini AI 음성 비서 시작")
    print(f"📚 {len(conversation_history.conversations)}개의 이전 대화 기억 중")
    print("🔍 실시간 검색: 뉴스, 날씨, 시간 등")
    print("\n명령어: 히스토리, 초기화, 검색테스트, 종료")
    
    while True:
        try:
            user_input = safe_input("\n질문: ")
            
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "종료"]:
                print("👋 프로그램을 종료합니다.")
                send_to_gui("status", "프로그램 종료")
                break
            
            # 명령어 처리
            if user_input.lower() in ["히스토리", "history"]:
                print(f"\n=== 대화 히스토리 ({len(conversation_history.conversations)}개) ===")
                for i, conv in enumerate(conversation_history.conversations[-3:], 1):
                    print(f"{i}. Q: {conv['question'][:30]}...")
                    print(f"   A: {conv['answer'][:50]}...")
                continue
            
            if user_input.lower() in ["초기화", "clear"]:
                conversation_history.clear_history()
                send_to_gui("history_update", "")
                print("✅ 히스토리 초기화 완료")
                continue
            
            if user_input.lower() in ["검색테스트"]:
                print("🔍 실시간 검색 테스트...")
                time_info = real_time_searcher.get_current_time_info()
                print(f"⏰ {time_info['current_time']}")
                
                weather = real_time_searcher.get_weather()
                if isinstance(weather, dict):
                    print(f"🌤️ {weather['temperature']}°C, {weather['description']}")
                continue
            
            # 일반 질문 처리
            send_to_gui("질문", user_input)
            send_to_gui("status", "🤔 답변 생성 중...")
            
            answer = ask_gemini(user_input)
            conversation_history.add_conversation(user_input, answer)
            send_to_gui("history_update", "")
            send_to_gui("답변", answer)
            
            print(f"\n📝 답변: {answer}\n")
            
            # 긴 답변은 요약 후 음성 출력
            if len(answer) > 300:
                send_to_gui("status", "📄 요약 중...")
                summary = summarize_text(answer)
                send_to_gui("요약", summary)
                print(f"📋 요약: {summary}")
                speak_korean(summary)
            else:
                speak_korean(answer)
                
        except KeyboardInterrupt:
            print("\n👋 프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 오류: {e}")
            send_to_gui("status", f"❌ 오류 발생")


if __name__ == "__main__":
    main()