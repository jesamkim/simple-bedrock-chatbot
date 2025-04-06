import os
import sys
from typing import Dict, Any, Optional
import json

# 로컬 서버 모듈 임포트
try:
    from datetime_mcp_server import DatetimeMCPServer
except ImportError as e:
    print(f"서버 모듈 로드 중 오류: {str(e)}")
    sys.exit(1)

class DatetimeMCPClient:
    """날짜/시간 정보를 제공하는 MCP 클라이언트"""
    
    def __init__(self, timezone: str = "Asia/Seoul"):
        """
        DatetimeMCPClient 초기화
        
        Args:
            timezone: 사용할 시간대 (기본값: "Asia/Seoul")
        """
        try:
            # 서버 클래스 인스턴스 생성
            self.server = DatetimeMCPServer(timezone=timezone)
            print("DateTime MCP 서버 초기화 완료")
        except Exception as e:
            print(f"DateTime MCP 서버 초기화 중 오류: {str(e)}")
            sys.exit(1)
    
    def get_current_time(self) -> Dict[str, Any]:
        """
        현재 시간 정보 가져오기
        
        Returns:
            시간 정보 딕셔너리
        """
        return self.server.get_current_time()
    
    def get_current_date(self) -> Dict[str, Any]:
        """
        현재 날짜 정보 가져오기
        
        Returns:
            날짜 정보 딕셔너리
        """
        return self.server.get_current_date()
    
    def get_datetime_info(self) -> Dict[str, Any]:
        """
        현재 날짜/시간 종합 정보 가져오기
        
        Returns:
            날짜/시간 정보 딕셔너리
        """
        return self.server.get_datetime_info()
    
    def format_time(self, time_info: Dict[str, Any]) -> str:
        """
        시간 정보 포맷팅
        
        Args:
            time_info: 시간 정보 딕셔너리
            
        Returns:
            포맷팅된 문자열
        """
        return self.server.format_time(time_info)
    
    def format_date(self, date_info: Dict[str, Any]) -> str:
        """
        날짜 정보 포맷팅
        
        Args:
            date_info: 날짜 정보 딕셔너리
            
        Returns:
            포맷팅된 문자열
        """
        return self.server.format_date(date_info)
    
    def format_datetime_info(self, dt_info: Dict[str, Any]) -> str:
        """
        날짜/시간 정보 포맷팅
        
        Args:
            dt_info: 날짜/시간 정보 딕셔너리
            
        Returns:
            포맷팅된 문자열
        """
        return self.server.format_datetime_info(dt_info)
    
    def calculate_time_difference(self, from_date: str, to_date: Optional[str] = None) -> Dict[str, Any]:
        """
        두 날짜 사이의 시간 차이 계산
        
        Args:
            from_date: 시작 날짜 (YYYY-MM-DD 형식)
            to_date: 끝 날짜 (YYYY-MM-DD 형식, 지정하지 않을 경우 현재)
            
        Returns:
            두 날짜 간의 차이 정보를 담은 딕셔너리
        """
        # 현재는 단순 전달 형태이지만 필요시 독자적인 구현 가능
        try:
            import datetime
            from datetime import datetime as dt
            
            # 시작 날짜 파싱
            try:
                from_date_obj = dt.strptime(from_date, "%Y-%m-%d")
            except ValueError:
                try:
                    # 다른 형식 시도
                    from_date_obj = dt.strptime(from_date, "%Y/%m/%d")
                except ValueError:
                    return {"error": "시작 날짜 형식이 올바르지 않습니다. YYYY-MM-DD 또는 YYYY/MM/DD 형식을 사용하세요."}
            
            # 종료 날짜 처리 (없으면 현재 날짜)
            if to_date:
                try:
                    to_date_obj = dt.strptime(to_date, "%Y-%m-%d")
                except ValueError:
                    try:
                        to_date_obj = dt.strptime(to_date, "%Y/%m/%d")
                    except ValueError:
                        return {"error": "종료 날짜 형식이 올바르지 않습니다. YYYY-MM-DD 또는 YYYY/MM/DD 형식을 사용하세요."}
            else:
                # 현재 날짜를 사용 (시간은 00:00:00으로 설정하여 정확히 날짜 단위만 비교)
                now = dt.now()
                to_date_obj = dt(now.year, now.month, now.day)
            
            # 차이 계산
            date_diff = to_date_obj - from_date_obj
            
            # 결과 생성
            diff_info = {
                "days": date_diff.days,
                "seconds": date_diff.seconds,
                "from_date": from_date_obj.strftime("%Y-%m-%d"),
                "to_date": to_date_obj.strftime("%Y-%m-%d"),
                "years": date_diff.days // 365,
                "months": date_diff.days // 30,  # 대략적인 계산
                "weeks": date_diff.days // 7,
            }
            
            return diff_info
            
        except Exception as e:
            return {"error": f"시간 차이 계산 중 오류 발생: {str(e)}"}


# 테스트용 코드
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="날짜/시간 정보 클라이언트")
    parser.add_argument('--timezone', default="Asia/Seoul", help='시간대 (기본값: Asia/Seoul)')
    parser.add_argument('--format', choices=['time', 'date', 'full', 'json'], default='full',
                       help='출력 형식 (time=시간만, date=날짜만, full=모두, json=JSON 형식)')
    parser.add_argument('--diff', nargs='+', help='날짜 차이 계산 (YYYY-MM-DD [YYYY-MM-DD])')
    
    args = parser.parse_args()
    
    client = DatetimeMCPClient(timezone=args.timezone)
    
    if args.diff:
        from_date = args.diff[0]
        to_date = args.diff[1] if len(args.diff) > 1 else None
        diff_result = client.calculate_time_difference(from_date, to_date)
        
        if "error" in diff_result:
            print(f"오류: {diff_result['error']}")
        else:
            print(f"날짜 차이 계산 결과:")
            print(f"- 시작 날짜: {diff_result['from_date']}")
            print(f"- 종료 날짜: {diff_result['to_date']}")
            print(f"- 일 수: {diff_result['days']}일")
            print(f"- 주 수: {diff_result['weeks']}주")
            print(f"- 월 수(약): {diff_result['months']}개월")
            print(f"- 년 수(약): {diff_result['years']}년")
    else:
        if args.format == 'time':
            time_info = client.get_current_time()
            if args.format == 'json':
                print(json.dumps(time_info, ensure_ascii=False, indent=2))
            else:
                print(client.format_time(time_info))
                
        elif args.format == 'date':
            date_info = client.get_current_date()
            if args.format == 'json':
                print(json.dumps(date_info, ensure_ascii=False, indent=2))
            else:
                print(client.format_date(date_info))
                
        elif args.format == 'json':
            dt_info = client.get_datetime_info()
            print(json.dumps(dt_info, ensure_ascii=False, indent=2))
            
        else:  # 'full'
            dt_info = client.get_datetime_info()
            print(client.format_datetime_info(dt_info))
