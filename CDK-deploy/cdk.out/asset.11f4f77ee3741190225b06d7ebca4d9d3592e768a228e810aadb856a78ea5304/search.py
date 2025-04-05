import requests
from typing import List, Dict
from bs4 import BeautifulSoup
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def extract_keywords(text: str) -> List[str]:
    """
    주어진 텍스트에서 중요 키워드를 추출합니다.
    """
    # 한국어와 영어 둘 다 처리할 수 있도록 합니다.
    stop_words = set(stopwords.words('english'))
    
    # 텍스트를 직접 토큰화합니다 (punkt_tab 의존성 우회)
    # 간단한 공백 기반 토큰화를 사용
    word_tokens = text.lower().split()
    
    # 불용어를 제거하고 길이가 2 이상인 단어만 선택합니다.
    keywords = [word for word in word_tokens if word not in stop_words and len(word) > 2 and word.isalnum()]
    
    # 중복 제거 및 빈도 기반 정렬
    keyword_freq = {}
    for word in keywords:
        keyword_freq[word] = keyword_freq.get(word, 0) + 1
    
    # 빈도수 기준 상위 5개 키워드 반환
    sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_keywords[:5]]

def duckduckgo_search(query: str) -> List[Dict]:
    """
    DuckDuckGo 검색을 수행하여 검색 결과를 반환합니다.
    """
    # DuckDuckGo 검색 URL
    url = f"https://html.duckduckgo.com/html/?q={query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # DuckDuckGo 검색 결과 파싱
        for result in soup.select('.result'):
            title_elem = result.select_one('.result__title')
            snippet_elem = result.select_one('.result__snippet')
            link_elem = result.select_one('.result__url')
            
            if title_elem and snippet_elem:
                title = title_elem.get_text().strip()
                snippet = snippet_elem.get_text().strip()
                link = link_elem.get_text().strip() if link_elem else ""
                
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "link": link
                })
                
                # 최대 5개 결과만 반환
                if len(results) >= 5:
                    break
        
        return results
    
    except Exception as e:
        print(f"검색 중 오류 발생: {e}")
        return []

def format_search_results(results: List[Dict]) -> str:
    """
    검색 결과를 문자열 형태로 포맷팅합니다.
    검색 결과에 명확한 인용 번호([1], [2]...)를 추가합니다.
    """
    if not results:
        return "검색 결과가 없습니다."
    
    formatted_text = "### 검색 결과\n\n"
    for i, result in enumerate(results, 1):
        formatted_text += f"**[{i}] {result['title']}**\n"
        formatted_text += f"{result['snippet']}\n"
        if result.get('link'):
            formatted_text += f"출처: {result['link']}\n"
        formatted_text += "\n"
    
    return formatted_text