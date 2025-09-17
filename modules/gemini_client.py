# modules/gemini_client.py
import google.generativeai as genai
from config import api_keys, app_config
import time
import re

class GeminiClient:
    """Gemini API 클라이언트"""
    
    def __init__(self):
        # API 키 설정 (config.py에서 이미 설정됨)
        self.model_name = "gemini-2.0-flash-exp"
        
        # 모델 초기화
        try:
            self.model = genai.GenerativeModel(self.model_name)
            print(f"✅ Gemini 모델 ({self.model_name}) 초기화 완료")
        except Exception as e:
            print(f"❌ Gemini 모델 초기화 오류: {e}")
            self.model = None
        
        # 생성 설정
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        # 안전 설정
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    
    def generate_response(self, prompt, context="", max_retries=3):
        """응답 생성"""
        if not self.model:
            return "Gemini 모델이 초기화되지 않았습니다."
        
        # 전체 프롬프트 구성
        full_prompt = self._build_full_prompt(prompt, context)
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=self.generation_config,
                    safety_settings=self.safety_settings
                )
                
                # 응답 검증
                if response and response.text:
                    return self._post_process_response(response.text)
                else:
                    print(f"⚠️  빈 응답 (시도 {attempt + 1}/{max_retries})")
                    
            except Exception as e:
                print(f"❌ Gemini API 오류 (시도 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # 재시도 전 대기
                else:
                    return f"죄송합니다. {max_retries}번 시도 후에도 응답을 생성할 수 없습니다."
        
        return "죄송합니다. 응답을 생성할 수 없습니다."
    
    def _build_full_prompt(self, prompt, context):
        """전체 프롬프트 구성"""
        system_prompt = """당신은 한국어 음성 AI 비서입니다. 다음 가이드라인을 따라주세요:
1. 친근하고 자연스러운 한국어로 답변하세요
2. 음성으로 들었을 때 이해하기 쉽게 답변하세요
3. 가능한 간결하되 도움이 되는 정보를 제공하세요
4. 불확실한 정보는 명확히 표시하세요
5. 실시간 정보가 제공된 경우 이를 적극 활용하세요

"""
        
        full_prompt = system_prompt
        
        if context:
            full_prompt += f"{context}\n"
        
        full_prompt += f"사용자 질문: {prompt}\n\n답변:"
        
        return full_prompt
    
    def _post_process_response(self, response_text):
        """응답 후처리"""
        # 불필요한 문자 제거
        cleaned = response_text.strip()
        
        # 마크다운 형식 단순화 (음성 출력용)
        cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)  # **굵게** → 굵게
        cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)      # *기울임* → 기울임
        cleaned = re.sub(r'`(.*?)`', r'\1', cleaned)        # `코드` → 코드
        
        # 연속된 줄바꿈 정리
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        return cleaned
    
    def summarize_text(self, text, target_sentences=2):
        """텍스트 요약"""
        if len(text) <= app_config.max_summary_length:
            return text
        
        summary_prompt = f"""다음 텍스트를 {target_sentences}문장으로 요약해주세요. 
음성으로 들었을 때 핵심 내용을 이해할 수 있도록 간결하고 명확하게 요약하세요:

{text}

요약:"""
        
        try:
            response = self.model.generate_content(
                summary_prompt,
                generation_config={
                    "temperature": 0.3,  # 요약은 더 정확하게
                    "max_output_tokens": 200
                }
            )
            
            if response and response.text:
                return self._post_process_response(response.text)
            else:
                # 요약 실패시 단순 자르기
                return text[:200] + "..."
                
        except Exception as e:
            print(f"요약 오류: {e}")
            return text[:200] + "..." if len(text) > 200 else text
    
    def analyze_sentiment(self, text):
        """감정 분석"""
        sentiment_prompt = f"""다음 텍스트의 감정을 분석하고 간단히 답해주세요:

{text}

감정 분석 결과 (긍정/부정/중립 중 하나와 간단한 이유):"""
        
        try:
            response = self.model.generate_content(
                sentiment_prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 100
                }
            )
            
            if response and response.text:
                return self._post_process_response(response.text)
            else:
                return "감정 분석을 할 수 없습니다."
                
        except Exception as e:
            print(f"감정 분석 오류: {e}")
            return "감정 분석 중 오류가 발생했습니다."
    
    def generate_follow_up_questions(self, conversation_text, num_questions=3):
        """후속 질문 생성"""
        followup_prompt = f"""다음 대화를 바탕으로 자연스러운 후속 질문 {num_questions}개를 생성해주세요:

{conversation_text}

후속 질문들:"""
        
        try:
            response = self.model.generate_content(
                followup_prompt,
                generation_config={
                    "temperature": 0.8,
                    "max_output_tokens": 300
                }
            )
            
            if response and response.text:
                questions = self._post_process_response(response.text)
                # 질문들을 리스트로 분리
                question_list = [q.strip() for q in questions.split('\n') if q.strip()]
                return question_list[:num_questions]
            else:
                return []
                
        except Exception as e:
            print(f"후속 질문 생성 오류: {e}")
            return []
    
    def test_connection(self):
        """연결 테스트"""
        print("🧪 Gemini API 연결 테스트...")
        
        if not api_keys.gemini_api_key:
            print("❌ Gemini API 키가 설정되지 않음")
            return False
        
        try:
            test_response = self.generate_response("안녕하세요. 연결 테스트입니다.")
            
            if test_response and "죄송합니다" not in test_response:
                print("✅ Gemini API 연결 성공")
                print(f"📝 테스트 응답: {test_response[:50]}...")
                return True
            else:
                print("❌ Gemini API 연결 실패")
                return False
                
        except Exception as e:
            print(f"❌ Gemini API 테스트 오류: {e}")
            return False
    
    def get_model_info(self):
        """모델 정보 조회"""
        try:
            # 사용 가능한 모델 목록 조회
            models = genai.list_models()
            available_models = []
            
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
            
            return {
                'current_model': self.model_name,
                'available_models': available_models,
                'generation_config': self.generation_config
            }
            
        except Exception as e:
            print(f"모델 정보 조회 오류: {e}")
            return None
    
    def change_model(self, model_name):
        """모델 변경"""
        try:
            self.model = genai.GenerativeModel(model_name)
            self.model_name = model_name
            print(f"✅ 모델이 {model_name}로 변경되었습니다.")
            return True
        except Exception as e:
            print(f"❌ 모델 변경 오류: {e}")
            return False