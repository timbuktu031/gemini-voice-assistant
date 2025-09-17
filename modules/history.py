# modules/history.py
import json
import os
from datetime import datetime
from config import app_config

class ConversationHistory:
    """대화 히스토리 관리"""
    
    def __init__(self):
        self.history_file = app_config.history_file
        self.max_history = app_config.max_history
        self.conversations = []
        self.load_history()
    
    def add_conversation(self, question, answer):
        """대화 추가"""
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "question_length": len(question),
            "answer_length": len(answer)
        }
        self.conversations.append(conversation)
        
        # 최대 히스토리 수 제한
        if len(self.conversations) > self.max_history:
            self.conversations = self.conversations[-self.max_history:]
        
        self.save_history()
        print(f"📝 대화 저장됨 (총 {len(self.conversations)}개)")
    
    def get_context(self, max_conversations=3):
        """대화 컨텍스트 생성"""
        if not self.conversations:
            return ""
        
        context = "이전 대화 내용:\n"
        recent_conversations = self.conversations[-max_conversations:]
        
        for i, conv in enumerate(recent_conversations, 1):
            context += f"[{i}] Q: {conv['question']}\n"
            # 답변은 150자로 제한
            answer_preview = conv['answer'][:150]
            if len(conv['answer']) > 150:
                answer_preview += "..."
            context += f"    A: {answer_preview}\n\n"
        
        context += "위 대화 내용을 참고해서 답변해주세요.\n\n"
        return context
    
    def save_history(self):
        """히스토리 저장"""
        try:
            # 백업 파일 생성 (기존 파일이 있을 경우)
            if os.path.exists(self.history_file):
                backup_file = f"{self.history_file}.backup"
                try:
                    import shutil
                    shutil.copy2(self.history_file, backup_file)
                except:
                    pass
            
            # 새 히스토리 저장
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"히스토리 저장 오류: {e}")
    
    def load_history(self):
        """히스토리 로드"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    loaded_conversations = json.load(f)
                    
                    # 데이터 유효성 검사
                    valid_conversations = []
                    for conv in loaded_conversations:
                        if self._validate_conversation(conv):
                            valid_conversations.append(conv)
                    
                    self.conversations = valid_conversations
                    print(f"📚 {len(self.conversations)}개의 이전 대화를 불러왔습니다.")
            else:
                print("📁 새로운 히스토리 파일이 생성됩니다.")
                
        except Exception as e:
            print(f"히스토리 로드 오류: {e}")
            self.conversations = []
    
    def _validate_conversation(self, conv):
        """대화 데이터 유효성 검사"""
        required_fields = ['timestamp', 'question', 'answer']
        return all(field in conv for field in required_fields)
    
    def clear_history(self):
        """히스토리 초기화"""
        # 백업 생성
        if self.conversations:
            backup_data = {
                'cleared_at': datetime.now().isoformat(),
                'conversations': self.conversations
            }
            backup_file = f"history_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, ensure_ascii=False, indent=2)
                print(f"💾 기존 히스토리가 {backup_file}에 백업되었습니다.")
            except Exception as e:
                print(f"백업 저장 오류: {e}")
        
        self.conversations = []
        self.save_history()
        print("🗑️  히스토리가 초기화되었습니다.")
    
    def get_history_summary(self):
        """히스토리 요약 정보"""
        if not self.conversations:
            return "저장된 대화 없음"
        
        total = len(self.conversations)
        latest_conv = self.conversations[-1]
        latest_time = latest_conv['timestamp'][:19].replace('T', ' ')
        
        # 통계 계산
        total_questions = sum(1 for conv in self.conversations)
        avg_answer_length = sum(conv['answer_length'] for conv in self.conversations) // total
        
        return f"총 {total}개 대화 | 최근: {latest_time} | 평균 답변: {avg_answer_length}자"
    
    def search_history(self, keyword):
        """히스토리에서 키워드 검색"""
        results = []
        
        for i, conv in enumerate(self.conversations):
            if (keyword.lower() in conv['question'].lower() or 
                keyword.lower() in conv['answer'].lower()):
                
                results.append({
                    'index': i,
                    'timestamp': conv['timestamp'][:19].replace('T', ' '),
                    'question': conv['question'][:50] + "..." if len(conv['question']) > 50 else conv['question'],
                    'answer': conv['answer'][:100] + "..." if len(conv['answer']) > 100 else conv['answer']
                })
        
        return results
    
    def export_history(self, format='txt'):
        """히스토리 내보내기"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'txt':
            filename = f"history_export_{timestamp}.txt"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=" * 50 + "\n")
                    f.write("대화 히스토리 내보내기\n")
                    f.write(f"생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}\n")
                    f.write(f"총 대화 수: {len(self.conversations)}개\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for i, conv in enumerate(self.conversations, 1):
                        f.write(f"[{i}] {conv['timestamp'][:19].replace('T', ' ')}\n")
                        f.write(f"Q: {conv['question']}\n")
                        f.write(f"A: {conv['answer']}\n")
                        f.write("-" * 50 + "\n\n")
                
                return filename
            except Exception as e:
                print(f"텍스트 내보내기 오류: {e}")
                return None
                
        elif format == 'json':
            filename = f"history_export_{timestamp}.json"
            try:
                export_data = {
                    'export_info': {
                        'exported_at': datetime.now().isoformat(),
                        'total_conversations': len(self.conversations),
                        'app_version': '1.0.0'
                    },
                    'conversations': self.conversations
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                return filename
            except Exception as e:
                print(f"JSON 내보내기 오류: {e}")
                return None
        
        return None
    
    def get_statistics(self):
        """히스토리 통계"""
        if not self.conversations:
            return None
        
        total_conversations = len(self.conversations)
        total_questions = sum(len(conv['question']) for conv in self.conversations)
        total_answers = sum(len(conv['answer']) for conv in self.conversations)
        
        # 날짜별 통계
        from collections import defaultdict
        daily_stats = defaultdict(int)
        for conv in self.conversations:
            date = conv['timestamp'][:10]  # YYYY-MM-DD
            daily_stats[date] += 1
        
        # 최근 활동일
        recent_dates = sorted(daily_stats.keys(), reverse=True)[:7]
        
        return {
            'total_conversations': total_conversations,
            'avg_question_length': total_questions // total_conversations,
            'avg_answer_length': total_answers // total_conversations,
            'most_active_date': max(daily_stats.items(), key=lambda x: x[1]) if daily_stats else None,
            'recent_activity': [(date, daily_stats[date]) for date in recent_dates]
        }