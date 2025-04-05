#!/usr/bin/env python
import requests
import argparse
import json
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import nltk

# NLTK 데이터 다운로드 체크
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords

class DuckDuckGoServer:
    """DuckDuckGo 검색 기능을 제공하는 서버 클래스"""
    
    def __init__(self, max_results: int = 5):
        """
        DuckDuckGoServer 초기화
        
        Args:
            max_results: 검색 결과 최대 개수 (기본값: 5)
        """
        self.max_results = max_results
        self.base_url = "https://html.duckduckgo.com/html/"
        
        # 검색 요청 헤더 설정
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        주어진 텍스트에서 중요 키워드를 추출합니다.
        
        Args:
            text: 키워드를 추출할 텍스트
            
        Returns:
            추출된 키워드 리스트 (최대 5개)
        """
        # 한국어와 영어 둘 다 처리할 수 있도록 합니다.
        stop_words = set(stopwords.words('english'))
        
        # 텍스트를 직접 토큰화합니다 (간단한 공백 기반 토큰화)
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
    
    def search(self, query: str) -> List[Dict[str, str]]:
        """
        DuckDuckGo 검색을 수행하여 검색 결과를 반환합니다.
        
        Args:
            query: 검색 쿼리 문자열
            
        Returns:
            검색 결과 목록 (딕셔너리 리스트)
        """
        try:
            # 검색 요청 실행
            response = requests.get(
                self.base_url,
                params={'q': query},
                headers=self.headers
            )
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # 검색 결과 추출
            for result in soup.select('.result'):
                title_elem = result.select_one('.result__title')
                snippet_elem = result.select_one('.result__snippet')
                link_elem = result.select_one('.result__url')
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text().strip()
                    snippet = snippet_elem.get_text().strip()
                    url = ""
                    
                    # URL이 있는 경우 추출
                    if link_elem:
                        url = link_elem.get_text().strip()
                    # a 태그에서 href 속성을 추출하는 방법 (일부 경우에 필요)
                    elif title_elem.find('a'):
                        url_href = title_elem.find('a').get('href', '')
                        # DuckDuckGo는 때로 URL을 리디렉션 형태로 제공
                        if url_href.startswith('/'):
                            url = "https://duckduckgo.com" + url_href
                        else:
                            url = url_href
                    
                    # 결과 추가
                    results.append({
                        "title": title,
                        "content": snippet,
                        "url": url
                    })
                    
                    # 최대 결과 수에 도달하면 중단
                    if len(results) >= self.max_results:
                        break
            
            return results
        
        except Exception as e:
            print(f"검색 중 오류 발생: {str(e)}")
            return []
    
    def format_results(self, results: List[Dict[str, str]]) -> str:
        """
        검색 결과를 문자열 형식으로 포맷팅합니다.
        
        Args:
            results: 검색 결과 목록
            
        Returns:
            포맷팅된 검색 결과 문자열
        """
        if not results:
            return "검색 결과가 없습니다."
            
        formatted_text = ""
        for i, result in enumerate(results, 1):
            title = result.get("title", "제목 없음")
            content = result.get("content", "내용 없음")
            url = result.get("url", "")
            
            formatted_text += f"[{i}] {title}\n{content}\n"
            if url:
                formatted_text += f"출처: {url}\n"
            formatted_text += "\n"
        
        return formatted_text


def main():
    """CLI 인터페이스로 DuckDuckGo 검색 기능 실행"""
    parser = argparse.ArgumentParser(description="DuckDuckGo 검색 CLI")
    parser.add_argument('query', help='검색할 쿼리')
    parser.add_argument('--max-results', type=int, default=5, help='최대 결과 수 (기본값: 5)')
    parser.add_argument('--json', action='store_true', help='JSON 형식으로 출력')
    
    args = parser.parse_args()
    
    server = DuckDuckGoServer(max_results=args.max_results)
    results = server.search(args.query)
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(server.format_results(results))

if __name__ == "__main__":
    main()
