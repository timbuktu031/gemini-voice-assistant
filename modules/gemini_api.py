import os
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ 환경변수 'GEMINI_API_KEY'가 설정되지 않았습니다.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def get_response(text):
    try:
        response = model.generate_content(text)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Gemini 오류: {e}")
        return "죄송합니다. 응답을 생성하지 못했어요."
