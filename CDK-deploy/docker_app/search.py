import os
from typing import List
from googleapiclient.discovery import build

#Google API 키와 검색 엔진 ID를 환경 변수에서 가져옵니다.
API_KEY = "YOUR_GOOGLE_API_KEY"
SEARCH_ENGINE_ID = "YOUR_GOOGLE_ENGINE_ID"


def google_search(query: str) -> List[str]:
    """
    주어진 쿼리에 대해 Google 검색을 수행하고 상위 5개 결과의 내용을 반환합니다.
    """
    service = build("customsearch", "v1", developerKey=API_KEY)
    result = service.cse().list(q=query, cx=SEARCH_ENGINE_ID, num=5).execute()

    summaries = []
    for item in result.get("items", []):
        snippet = item.get("snippet")
        if snippet:
            summaries.append(snippet)

    return summaries


#Google 검색 API를 사용하여 상위 5개 결과의 URL을 가져오는 함수
def get_top_urls(query: str) -> List[str]:
    service = build("customsearch", "v1", developerKey=API_KEY)
    result = service.cse().list(q=query, cx=SEARCH_ENGINE_ID, num=5).execute()
    urls = [item["link"] for item in result.get("items", [])]
    return urls
