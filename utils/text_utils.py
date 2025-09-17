# utils/text_utils.py
import re
import sys
import io
import locale

def setup_encoding():
    """한글 인코딩 설정"""
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

def extract_keywords(text, max_keywords=5):
    """텍스트에서 키워드 추출"""
    # 간단한 키워드 추출 (불용어 제거 후 빈도수 기반)
    stopwords = ['은', '는', '이', '가', '을', '를', '에', '의', '와', '과', '으로', '로', '에서']
    
    # 단어 분리
    words = re.findall(r'[가-힣]{2,}', text)
    
    # 불용어 제거 및 빈도 계산
    word_freq = {}
    for word in words:
        if word not in stopwords and len(word) >= 2:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # 빈도순 정렬
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, freq in sorted_words[:max_keywords]]

def truncate_text(text, max_length=500):
    """텍스트 길이 제한"""
    if len(text) <= max_length:
        return text
    
    # 문장 단위로 자르기
    sentences = re.split(r'[.!?]', text)
    result = ""
    
    for sentence in sentences:
        if len(result + sentence) <= max_length - 3:
            result += sentence + "."
        else:
            break
    
    return result.rstrip(".") + "..."

def is_korean_text(text):
    """한국어 텍스트 판단"""
    korean_chars = re.findall(r'[가-힣]', text)
    total_chars = re.findall(r'[가-힣a-zA-Z]', text)
    
    if not total_chars:
        return False
    
    korean_ratio = len(korean_chars) / len(total_chars)
    return korean_ratio > 0.3  # 30% 이상이 한글이면 한국어로 판단