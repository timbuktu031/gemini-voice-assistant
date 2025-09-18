# modules/searcher.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import os

class RealTimeSearcher:
    """실시간 정보 검색 클래스"""
    
    def __init__(self):
        # 환경변수에서 API 키 로드
        self.naver_client_id = os.getenv("NAVER_CLIENT_ID")
        self.naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        self.timeout = 10

    def search_news(self, query, language="ko"):
        """뉴스 검색"""
        # 네이버 뉴스 API 시도
        naver_results = self.search_naver(query, search_type="news", display=3, sort="date")
        if naver_results:
            return naver_results

        # 웹 검색 fallback
        return self.search_web(f"{query} 뉴스")

    def get_current_time_info(self):
        """현재 시간 정보"""
        try:
            kst = pytz.timezone('Asia/Seoul')
            now = datetime.now(kst)
            
            weekdays = {
                'Monday': '월요일',
                'Tuesday': '화요일', 
                'Wednesday': '수요일',
                'Thursday': '목요일',
                'Friday': '금요일',
                'Saturday': '토요일',
                'Sunday': '일요일'
            }
            
            return {
                'current_time': now.strftime('%Y년 %m월 %d일 %H시 %M분'),
                'weekday': weekdays.get(now.strftime('%A'), now.strftime('%A')),
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
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': self.weather_api_key,
                'units': 'metric',
                'lang': 'kr'
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                desc = data['weather'][0]['description']
                humidity = data['main']['humidity']
                feels_like = data['main']['feels_like']
                
                return {
                    'temperature': temp,
                    'description': desc,
                    'humidity': humidity,
                    'feels_like': feels_like,
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
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                results = []
                
                for item in items:
                    title = item["title"].replace("<b>", "").replace("</b>", "").replace("&quot;", '"')
                    desc = item["description"].replace("<b>", "").replace("</b>", "").replace("&quot;", '"')
                    
                    if search_type == "news":
                        # 뉴스의 경우 날짜 정보도 포함
                        pub_date = item.get("pubDate", "")
                        results.append(f"[네이버뉴스] {title} - {desc}")
                    else:
                        results.append(f"{title} - {desc}")
                
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
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}&hl=ko"
            response = requests.get(search_url, headers=headers, timeout=self.timeout)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # 구글 검색 결과에서 제목 추출
            for result in soup.find_all('h3', limit=3):
                title = result.get_text()
                if title and len(title) > 10:
                    results.append(f"[구글검색] {title}")
            
            return results if results else [f"{query}에 대한 정보를 찾을 수 없습니다."]
            
        except Exception as e:
            print(f"웹 검색 오류: {e}")
            return [f"{query} 검색 중 오류 발생"]

    def get_real_time_info(self, query):
        """통합 실시간 정보 수집"""
        results = []
        
        # 시간 관련 키워드
        if any(word in query.lower() for word in ["시간", "지금", "현재"]):
            time_info = self.get_current_time_info()
            results.append(f"현재 시간: {time_info['current_time']} ({time_info['weekday']})")
        
        # 날씨 관련 키워드
        if "날씨" in query.lower():
            weather = self.get_weather()
            if isinstance(weather, dict):
                results.append(f"날씨: {weather['temperature']}°C, {weather['description']}, 체감온도 {weather['feels_like']}°C")
            elif isinstance(weather, list):
                results.extend(weather[:1])
        
        # 뉴스 관련 키워드
        if "뉴스" in query.lower():
            # 키워드 추출해서 관련 뉴스 검색
            news_keywords = self._extract_news_keywords(query)
            news = self.search_news(news_keywords or "한국")
            if news:
                results.extend([f"뉴스: {item}" for item in news[:2]])
        
        # 일반 검색
        if not results or len(results) < 2:
            web_results = self.search_web(query)
            results.extend(web_results[:3-len(results)])
        
        return results
    
    def _extract_news_keywords(self, query):
        """뉴스 검색을 위한 키워드 추출"""
        # 뉴스 관련 단어 제거 후 핵심 키워드 추출
        import re
        
        # 불필요한 단어들 제거
        stopwords = ["뉴스", "최신", "오늘", "어제", "알려줘", "알려주세요", "검색", "찾아줘"]
        
        words = re.findall(r'[가-힣a-zA-Z]+', query)
        keywords = [word for word in words if word not in stopwords and len(word) >= 2]
        
        return " ".join(keywords[:2]) if keywords else None

    def test_apis(self):
        """API 연결 테스트"""
        print("🧪 API 연결 테스트 시작...")
        
        # 네이버 API 테스트
        if self.naver_client_id and self.naver_client_secret:
            test_result = self.search_naver("테스트", display=1)
            if test_result:
                print("✅ 네이버 API 연결 성공")
            else:
                print("❌ 네이버 API 연결 실패")
        else:
            print("⚠️  네이버 API 키가 설정되지 않음")
        
        # 날씨 API 테스트
        if self.weather_api_key:
            weather = self.get_weather("Seoul")
            if isinstance(weather, dict):
                print("✅ 날씨 API 연결 성공")
            else:
                print("❌ 날씨 API 연결 실패")
        else:
            print("⚠️  날씨 API 키가 설정되지 않음")
        
        print("🧪 API 테스트 완료")
