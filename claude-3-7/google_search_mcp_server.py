#!/usr/bin/env python
import requests
import os
import argparse
import json
from typing import List, Dict, Any, Optional
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

class GoogleSearchServer:
    """Google Custom Search API를 사용하는 검색 기능을 제공하는 서버 클래스"""
    
    def __init__(self, max_results: int = 5):
        """
        GoogleSearchServer 초기화
        
        Args:
            max_results: 검색 결과 최대 개수 (기본값: 5)
        """
        self.max_results = max_results
        self.api_key = os.environ.get('GOOGLE_API_KEY')
        self.search_engine_id = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')
        
        if not self.api_key or not self.search_engine_id:
            print("경고: Google API Key 또는 Search Engine ID가 설정되지 않았습니다. 환경 변수를 확인하세요.")
            print("GOOGLE_API_KEY와 GOOGLE_SEARCH_ENGINE_ID 환경 변수를 설정해야 합니다.")
            # 실제 검색 시에 오류 발생 처리
    
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
        Google Custom Search API를 사용해 검색을 수행하여 결과를 반환합니다.
        
        Args:
            query: 검색 쿼리 문자열
            
        Returns:
            검색 결과 목록 (딕셔너리 리스트)
        """
        # API 키와 검색 엔진 ID 확인
        if not self.api_key or not self.search_engine_id:
            return [{
                "title": "검색 설정 오류",
                "content": "Google API Key 또는 Search Engine ID가 설정되지 않았습니다. 환경 변수를 확인하세요.",
                "url": ""
            }]
        
        try:
            # Google Custom Search API 요청
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(self.max_results, 10)  # Google API는 최대 10개까지만 허용
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            search_results = response.json()
            results = []
            
            if 'items' in search_results:
                for item in search_results['items']:
                    title = item.get('title', '제목 없음')
                    snippet = item.get('snippet', '내용 없음')
                    link = item.get('link', '')
                    
                    results.append({
                        "title": title,
                        "content": snippet,
                        "url": link
                    })
                    
                    # 최대 결과 수에 도달하면 중단
                    if len(results) >= self.max_results:
                        break
            
            # 결과가 없을 경우 메시지 반환
            if not results:
                print(f"'{query}' 검색 결과가 없습니다.")
                return [{
                    "title": "검색 결과 없음",
                    "content": f"'{query}'에 대한 검색 결과를 찾을 수 없습니다.",
                    "url": ""
                }]
            
            return results
            
        except requests.exceptions.RequestException as e:
            error_msg = f"네트워크 요청 오류: {str(e)}"
            print(error_msg)
            return [{
                "title": "검색 오류",
                "content": f"Google 검색 중 네트워크 오류가 발생했습니다: {str(e)}",
                "url": ""
            }]
        except Exception as e:
            error_msg = f"검색 중 오류 발생: {str(e)}"
            print(error_msg)
            return [{
                "title": "검색 처리 오류",
                "content": f"검색 결과 처리 중 오류가 발생했습니다: {str(e)}",
                "url": ""
            }]
    
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
    """CLI 인터페이스로 Google 검색 기능 실행"""
    parser = argparse.ArgumentParser(description="Google Search CLI")
    parser.add_argument('query', help='검색할 쿼리')
    parser.add_argument('--max-results', type=int, default=5, help='최대 결과 수 (기본값: 5)')
    parser.add_argument('--json', action='store_true', help='JSON 형식으로 출력')
    
    args = parser.parse_args()
    
    server = GoogleSearchServer(max_results=args.max_results)
    results = server.search(args.query)
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(server.format_results(results))

if __name__ == "__main__":
    main()
