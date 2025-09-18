# modules/gui.py
import tkinter as tk
from tkinter import scrolledtext
import tkinter.font as tkFont
import queue
import threading
from datetime import datetime

# GUI 통신용 큐
gui_queue = queue.Queue()

class GeminiGUI:
    """GUI 인터페이스"""
    def __init__(self, conversation_history):
        self.conversation_history = conversation_history
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
            text=self.conversation_history.get_history_summary(),
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
        self.history_info_label.config(text=self.conversation_history.get_history_summary())
    
    def clear_history(self):
        """히스토리 초기화"""
        self.conversation_history.clear_history()
        self.update_history_info()
        self.add_message("시스템", "대화 히스토리가 초기화되었습니다.", "status")
    
    def export_history(self):
        """히스토리 내보내기"""
        try:
            export_file = f"history_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(export_file, 'w', encoding='utf-8') as f:
                f.write("=== 대화 히스토리 ===\n\n")
                for i, conv in enumerate(self.conversation_history.conversations, 1):
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

def send_to_gui(msg_type, content):
    """GUI에 메시지 전송"""
    gui_queue.put((msg_type, content))