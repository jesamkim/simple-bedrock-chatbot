#!/usr/bin/env python
import os
import sys
import subprocess
import json
import time
import signal
import atexit
from typing import Dict, Any, List, Optional, Union

class UnifiedMCPClient:
    """통합 MCP 클라이언트 - 모든 MCP 서비스에 대한 인터페이스 제공"""
    
    def __init__(self, config_path: str = None):
        """
        UnifiedMCPClient 초기화
        
        Args:
            config_path: MCP 설정 파일 경로 (기본값: mcp_config.json)
        """
        self.config_path = config_path or os.environ.get("MCP_CONFIG", "mcp_config.json")
        self.services = {}
        self._server_process = None
        
        # 기존 MCP 서비스 동적 로드
        self._load_services()
    
    def _load_services(self):
        """설정된 서비스 로드"""
        try:
            # datetime 서비스 로드
            from datetime_mcp_server import DatetimeServer
            self.services["datetime"] = DatetimeServer(timezone="Asia/Seoul")
            
            # search 서비스 로드
            from google_search_mcp_server import GoogleSearchServer
            self.services["search"] = GoogleSearchServer(max_results=5)
            
        except Exception as e:
            print(f"서비스 로드 중 오류: {str(e)}", file=sys.stderr)
    
    # === 날짜/시간 서비스 메서드 ===
    def get_current_time(self):
        """현재 시간 정보 가져오기"""
        if "datetime" in self.services:
            return self.services["datetime"].get_current_time()
        raise ValueError("날짜/시간 서비스를 사용할 수 없습니다.")
    
    def get_current_date(self):
        """현재 날짜 정보 가져오기"""
        if "datetime" in self.services:
            return self.services["datetime"].get_current_date()
        raise ValueError("날짜/시간 서비스를 사용할 수 없습니다.")
    
    def get_datetime_info(self):
        """현재 날짜/시간 종합 정보 가져오기"""
        if "datetime" in self.services:
            return self.services["datetime"].get_datetime_info()
        raise ValueError("날짜/시간 서비스를 사용할 수 없습니다.")
    
    def format_time(self, time_info: Dict[str, Any]) -> str:
        """시간 정보 포맷팅"""
        if "datetime" in self.services:
            return self.services["datetime"].format_time(time_info)
        raise ValueError("날짜/시간 서비스를 사용할 수 없습니다.")
    
    def format_date(self, date_info: Dict[str, Any]) -> str:
        """날짜 정보 포맷팅"""
        if "datetime" in self.services:
            return self.services["datetime"].format_date(date_info)
        raise ValueError("날짜/시간 서비스를 사용할 수 없습니다.")
    
    def format_datetime_info(self, dt_info: Dict[str, Any]) -> str:
        """날짜/시간 정보 포맷팅"""
        if "datetime" in self.services:
            return self.services["datetime"].format_datetime_info(dt_info)
        raise ValueError("날짜/시간 서비스를 사용할 수 없습니다.")
    
    # === 검색 서비스 메서드 ===
    def search(self, query: str, max_results: int = None) -> List[Dict[str, str]]:
        """
        Google 검색 수행
        
        Args:
            query: 검색 쿼리 문자열
            max_results: 최대 결과 개수
            
        Returns:
            검색 결과 리스트 (딕셔너리)
        """
        if "search" in self.services:
            return self.services["search"].search(query)
        raise ValueError("검색 서비스를 사용할 수 없습니다.")
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        텍스트에서 중요 키워드 추출
        
        Args:
            text: 키워드를 추출할 텍스트
            
        Returns:
            추출된 키워드 리스트
        """
        if "search" in self.services:
            return self.services["search"].extract_keywords(text)
        raise ValueError("검색 서비스를 사용할 수 없습니다.")
    
    def format_results(self, results: List[Dict[str, str]]) -> str:
        """
        검색 결과 포맷팅
        
        Args:
            results: 검색 결과 리스트
            
        Returns:
            포맷팅된 문자열
        """
        if "search" in self.services:
            return self.services["search"].format_results(results)
        raise ValueError("검색 서비스를 사용할 수 없습니다.")
    
    # === 확장 가능한 구조로 새로운 서비스 메서드 추가 ===
    def get_service(self, service_name: str) -> Any:
        """
        서비스 인스턴스 직접 접근
        
        Args:
            service_name: 서비스 이름 ("datetime", "search" 등)
            
        Returns:
            서비스 인스턴스
        """
        if service_name in self.services:
            return self.services[service_name]
        raise ValueError(f"'{service_name}' 서비스를 찾을 수 없습니다.")
    
    def start_mcp_server(self):
        """별도 프로세스로 MCP 서버 시작 (필요한 경우)"""
        if self._server_process is not None:
            print("MCP 서버가 이미 실행 중입니다.", file=sys.stderr)
            return
        
        try:
            # mcp.py를 별도 프로세스로 실행
            script_path = os.path.join(os.path.dirname(__file__), "mcp.py")
            cmd = [sys.executable, script_path]
            
            # 환경 변수 설정
            env = os.environ.copy()
            if self.config_path:
                env["MCP_CONFIG"] = self.config_path
            
            # 서버 프로세스 시작
            self._server_process = subprocess.Popen(
                cmd, 
                env=env,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # 종료 시 정리를 위한 핸들러 등록
            atexit.register(self.stop_mcp_server)
            
            # 서버가 시작될 때까지 잠시 대기
            time.sleep(1.0)
            
            if self._server_process.poll() is not None:
                # 서버가 종료된 경우 오류 확인
                _, stderr = self._server_process.communicate()
                print(f"MCP 서버 시작 실패: {stderr}", file=sys.stderr)
                self._server_process = None
            else:
                print("MCP 서버가 시작되었습니다.", file=sys.stderr)
        
        except Exception as e:
            print(f"MCP 서버 시작 중 오류: {str(e)}", file=sys.stderr)
            self._server_process = None
    
    def stop_mcp_server(self):
        """MCP 서버 중지 (필요한 경우)"""
        if self._server_process is None:
            return
        
        try:
            # SIGINT 시그널 전송 (Ctrl+C와 동일)
            self._server_process.send_signal(signal.SIGINT)
            
            # 정상 종료 대기
            try:
                self._server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # 타임아웃된 경우 강제 종료
                self._server_process.terminate()
                try:
                    self._server_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self._server_process.kill()
            
            self._server_process = None
            print("MCP 서버가 중지되었습니다.", file=sys.stderr)
            
        except Exception as e:
            print(f"MCP 서버 중지 중 오류: {str(e)}", file=sys.stderr)


# 기존 코드와의 호환성을 위한 클래스
class DatetimeMCPClient:
    """날짜/시간 MCP 클라이언트 (호환성 유지)"""
    
    def __init__(self, timezone: str = "Asia/Seoul"):
        self._unified_client = UnifiedMCPClient()
    
    def get_current_time(self):
        return self._unified_client.get_current_time()
    
    def get_current_date(self):
        return self._unified_client.get_current_date()
    
    def get_datetime_info(self):
        return self._unified_client.get_datetime_info()
    
    def format_time(self, time_info):
        return self._unified_client.format_time(time_info)
    
    def format_date(self, date_info):
        return self._unified_client.format_date(date_info)
    
    def format_datetime_info(self, dt_info):
        return self._unified_client.format_datetime_info(dt_info)
    
    def calculate_time_difference(self, from_date: str, to_date: Optional[str] = None):
        # 필요하다면 이 메서드도 통합 클라이언트로 이동 가능
        return self._unified_client.get_service("datetime").calculate_time_difference(from_date, to_date)


class GoogleSearchMCPClient:
    """Google 검색 MCP 클라이언트 (호환성 유지)"""
    
    def __init__(self, max_results: int = 5):
        self._unified_client = UnifiedMCPClient()
        self._max_results = max_results
    
    def search(self, query: str, max_results: int = None):
        max_results = max_results or self._max_results
        return self._unified_client.search(query)
    
    def extract_keywords(self, text: str):
        return self._unified_client.extract_keywords(text)
    
    def format_results(self, results):
        return self._unified_client.format_results(results)


# 테스트 코드
if __name__ == "__main__":
    client = UnifiedMCPClient()
    
    # 날짜/시간 정보 가져오기
    print("===== 날짜/시간 정보 =====")
    dt_info = client.get_datetime_info()
    print(client.format_datetime_info(dt_info))
    
    # 검색 기능 테스트
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\n===== '{query}'에 대한 검색 =====")
        
        # 키워드 추출
        keywords = client.extract_keywords(query)
        print(f"추출된 키워드: {', '.join(keywords)}")
        
        # 검색 수행
        results = client.search(query)
        print(client.format_results(results))
