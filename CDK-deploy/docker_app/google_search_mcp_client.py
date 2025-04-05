import os
import sys
from typing import Dict, List, Any, Optional

# 로컬 서버 모듈 임포트
try:
    from google_search_mcp_server import GoogleSearchServer
except ImportError as e:
    print(f"서버 모듈 로드 중 오류: {str(e)}")
    sys.exit(1)

class GoogleSearchMCPClient:
    """Google 검색을 위한 MCP 클라이언트"""
    
    def __init__(self, max_results: int = 5):
        """
        GoogleSearchMCPClient 초기화
        
        Args:
            max_results: 검색 결과 최대 개수 (기본값: 5)
        """
        try:
            # 서버 클래스 인스턴스 생성
            self.server = GoogleSearchServer(max_results=max_results)
            print("Google Search 서버 초기화 완료")
        except Exception as e:
            print(f"Google Search 서버 초기화 중 오류: {str(e)}")
            sys.exit(1)
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        텍스트에서 중요 키워드 추출
        
        Args:
            text: 키워드를 추출할 텍스트
            
        Returns:
            추출된 키워드 리스트
        """
        return self.server.extract_keywords(text)
    
    def search(self, query: str, max_results: int = None) -> List[Dict[str, str]]:
        """
        Google 검색 수행
        
        Args:
            query: 검색 쿼리 문자열
            max_results: 최대 결과 개수 (지정하지 않으면 초기화 시 설정값 사용)
            
        Returns:
            검색 결과 리스트 (딕셔너리)
        """
        # max_results가 지정되었을 경우 임시로 변경
        if max_results is not None:
            original_max = self.server.max_results
            self.server.max_results = max_results
            results = self.server.search(query)
            self.server.max_results = original_max  # 원래 값 복원
            return results
        
        return self.server.search(query)
    
    def format_results(self, results: List[Dict[str, str]]) -> str:
        """
        검색 결과 포맷팅
        
        Args:
            results: 검색 결과 리스트
            
        Returns:
            포맷팅된 문자열
        """
        return self.server.format_results(results)


# 테스트용 코드
if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        client = GoogleSearchMCPClient()
        
        print(f"'{query}' 키워드 추출 결과:", client.extract_keywords(query))
        
        print(f"\n'{query}' 검색 중...")
        results = client.search(query)
        
        print("\n검색 결과:")
        print(client.format_results(results))
    else:
        print("사용법: python google_search_mcp_client.py <검색어>")
