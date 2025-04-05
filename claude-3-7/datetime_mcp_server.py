#!/usr/bin/env python
import datetime
import pytz
import json
import argparse
from typing import Dict, Any

class DatetimeMCPServer:
    """현재 날짜/시간 정보를 제공하는 서버 클래스"""
    
    def __init__(self, timezone: str = "Asia/Seoul"):
        """
        DatetimeMCPServer 초기화
        
        Args:
            timezone: 사용할 기본 시간대 (기본값: "Asia/Seoul")
        """
        self.timezone = timezone
    
    def get_current_time(self) -> Dict[str, Any]:
        """
        현재 시간 정보를 가져옵니다.
        
        Returns:
            시간 정보를 담은 딕셔너리
        """
        # 현재 시간 정보 가져오기 (지정된 시간대 사용)
        try:
            tz = pytz.timezone(self.timezone)
            now = datetime.datetime.now(tz)
            
            return {
                "hour": now.hour,
                "minute": now.minute,
                "second": now.second,
                "ampm": "오전" if now.hour < 12 else "오후",
                "hour_12": now.hour % 12 if now.hour % 12 != 0 else 12,
                "timezone": self.timezone,
                "timezone_name": tz.tzname(now),
                "timezone_offset": int(tz.utcoffset(now).total_seconds() / 3600),
                "timestamp": now.timestamp()
            }
        except Exception as e:
            print(f"시간 정보 가져오기 중 오류: {str(e)}")
            # 기본 시간 정보 제공 (UTC)
            now = datetime.datetime.now(pytz.UTC)
            return {
                "hour": now.hour,
                "minute": now.minute,
                "second": now.second,
                "ampm": "AM" if now.hour < 12 else "PM",
                "hour_12": now.hour % 12 if now.hour % 12 != 0 else 12,
                "timezone": "UTC",
                "timezone_name": "UTC",
                "timezone_offset": 0,
                "timestamp": now.timestamp(),
                "error": str(e)
            }
    
    def get_current_date(self) -> Dict[str, Any]:
        """
        현재 날짜 정보를 가져옵니다.
        
        Returns:
            날짜 정보를 담은 딕셔너리
        """
        try:
            tz = pytz.timezone(self.timezone)
            now = datetime.datetime.now(tz)
            
            # 한국어 요일 변환
            weekday_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
            weekday_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            month_kr = ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"]
            
            return {
                "year": now.year,
                "month": now.month,
                "day": now.day,
                "weekday": now.weekday(),  # 0=월요일, 6=일요일
                "weekday_kr": weekday_kr[now.weekday()],
                "weekday_en": weekday_en[now.weekday()],
                "month_name_kr": month_kr[now.month - 1],
                "month_name_en": now.strftime("%B"),
                "day_of_year": now.timetuple().tm_yday,
                "week_of_year": int(now.strftime("%V")),
                "is_leap_year": self._is_leap_year(now.year),
                "days_in_month": self._days_in_month(now.year, now.month)
            }
        except Exception as e:
            print(f"날짜 정보 가져오기 중 오류: {str(e)}")
            # 기본 날짜 정보 제공 (UTC)
            now = datetime.datetime.now(pytz.UTC)
            return {
                "year": now.year,
                "month": now.month,
                "day": now.day,
                "weekday": now.weekday(),
                "weekday_en": now.strftime("%A"),
                "month_name_en": now.strftime("%B"),
                "error": str(e)
            }
    
    def get_datetime_info(self) -> Dict[str, Any]:
        """
        현재 날짜와 시간 정보를 모두 가져옵니다.
        
        Returns:
            날짜와 시간 정보를 담은 딕셔너리
        """
        date_info = self.get_current_date()
        time_info = self.get_current_time()
        
        # 추가 정보 계산
        try:
            tz = pytz.timezone(self.timezone)
            now = datetime.datetime.now(tz)
            
            # 오늘이 지난 시간 계산 (일 시작부터)
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elapsed_seconds = (now - start_of_day).total_seconds()
            
            # 오늘 남은 시간 계산
            end_of_day = start_of_day + datetime.timedelta(days=1)
            remaining_seconds = (end_of_day - now).total_seconds()
            
            # 올해 지난 일수와 남은 일수
            start_of_year = datetime.datetime(now.year, 1, 1, tzinfo=tz)
            end_of_year = datetime.datetime(now.year + 1, 1, 1, tzinfo=tz)
            elapsed_days = (now - start_of_year).days
            remaining_days = (end_of_year - now).days
            
            # ISO 표준 날짜/시간 문자열
            iso_format = now.isoformat()
            
            # 추가 정보 합치기
            additional_info = {
                "iso_format": iso_format,
                "elapsed_seconds_today": int(elapsed_seconds),
                "remaining_seconds_today": int(remaining_seconds),
                "elapsed_days_this_year": elapsed_days,
                "remaining_days_this_year": remaining_days,
                "datetime_kr": now.strftime("%Y년 %m월 %d일 ") + f"{time_info['ampm']} {time_info['hour_12']}시 {time_info['minute']}분"
            }
            
            # 딕셔너리 통합
            combined_info = {**date_info, **time_info, **additional_info}
            return combined_info
            
        except Exception as e:
            print(f"종합 날짜/시간 정보 생성 중 오류: {str(e)}")
            # 기본 정보만 반환
            combined_info = {**date_info, **time_info, "error": str(e)}
            return combined_info
    
    def _is_leap_year(self, year: int) -> bool:
        """윤년 여부 확인"""
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    
    def _days_in_month(self, year: int, month: int) -> int:
        """해당 월의 일 수 계산"""
        days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if month == 2 and self._is_leap_year(year):
            return 29
        return days[month]
    
    def format_time(self, time_info: Dict[str, Any]) -> str:
        """
        시간 정보를 가독성 좋게 포맷팅합니다.
        
        Args:
            time_info: 시간 정보 딕셔너리
            
        Returns:
            포맷팅된 시간 정보 문자열
        """
        formatted_text = f"## 현재 시간 정보\n\n"
        formatted_text += f"* **현재 시각:** {time_info['ampm']} {time_info['hour_12']}:{time_info['minute']:02d}:{time_info['second']:02d}\n"
        formatted_text += f"* **24시간제:** {time_info['hour']:02d}:{time_info['minute']:02d}:{time_info['second']:02d}\n"
        formatted_text += f"* **시간대:** {time_info['timezone']} (UTC{'+' if time_info['timezone_offset'] >= 0 else ''}{time_info['timezone_offset']})\n"
        
        return formatted_text
    
    def format_date(self, date_info: Dict[str, Any]) -> str:
        """
        날짜 정보를 가독성 좋게 포맷팅합니다.
        
        Args:
            date_info: 날짜 정보 딕셔너리
            
        Returns:
            포맷팅된 날짜 정보 문자열
        """
        formatted_text = f"## 현재 날짜 정보\n\n"
        formatted_text += f"* **오늘 날짜:** {date_info['year']}년 {date_info['month']}월 {date_info['day']}일 {date_info['weekday_kr']}\n"
        formatted_text += f"* **영문 표기:** {date_info['month_name_en']} {date_info['day']}, {date_info['year']} ({date_info['weekday_en']})\n"
        formatted_text += f"* **올해 정보:** {date_info['year']}년은 {'윤년' if date_info['is_leap_year'] else '평년'}입니다.\n"
        formatted_text += f"* **이번 달 일수:** {date_info['days_in_month']}일\n"
        formatted_text += f"* **올해 {date_info['day_of_year']}번째 날 / 제{date_info['week_of_year']}주차**\n"
        
        return formatted_text
    
    def format_datetime_info(self, dt_info: Dict[str, Any]) -> str:
        """
        날짜와 시간 정보를 가독성 좋게 포맷팅합니다.
        
        Args:
            dt_info: 날짜/시간 정보 딕셔너리
            
        Returns:
            포맷팅된 정보 문자열
        """
        formatted_text = f"## 현재 날짜/시간 정보\n\n"
        formatted_text += f"* **현재 시각:** {dt_info['year']}년 {dt_info['month']}월 {dt_info['day']}일 {dt_info['weekday_kr']} "
        formatted_text += f"{dt_info['ampm']} {dt_info['hour_12']}시 {dt_info['minute']}분 {dt_info['second']}초\n"
        formatted_text += f"* **시간대:** {dt_info['timezone']} (UTC{'+' if dt_info['timezone_offset'] >= 0 else ''}{dt_info['timezone_offset']})\n\n"
        
        # 오늘 정보
        formatted_text += f"**오늘 경과 시간:** {dt_info['elapsed_seconds_today'] // 3600}시간 {(dt_info['elapsed_seconds_today'] % 3600) // 60}분 {dt_info['elapsed_seconds_today'] % 60}초\n"
        formatted_text += f"**오늘 남은 시간:** {dt_info['remaining_seconds_today'] // 3600}시간 {(dt_info['remaining_seconds_today'] % 3600) // 60}분 {dt_info['remaining_seconds_today'] % 60}초\n\n"
        
        # 올해 정보
        formatted_text += f"**올해 정보:** {dt_info['year']}년은 {'윤년' if dt_info['is_leap_year'] else '평년'}입니다.\n"
        formatted_text += f"**올해 경과일:** {dt_info['elapsed_days_this_year']}일 (전체의 약 {dt_info['elapsed_days_this_year'] * 100 // 365}%)\n"
        formatted_text += f"**올해 남은일:** {dt_info['remaining_days_this_year']}일\n\n"
        
        # 표준 형식
        formatted_text += f"**ISO 형식:** {dt_info['iso_format']}\n"
        
        return formatted_text


def main():
    """CLI 인터페이스로 날짜/시간 정보 제공"""
    parser = argparse.ArgumentParser(description="날짜/시간 정보 CLI")
    parser.add_argument('--timezone', default="Asia/Seoul", help='사용할 시간대 (기본값: Asia/Seoul)')
    parser.add_argument('--format', choices=['time', 'date', 'full', 'json'], default='full', 
                       help='출력 형식 (time=시간만, date=날짜만, full=모두, json=JSON 형식)')
    
    args = parser.parse_args()
    
    server = DatetimeMCPServer(timezone=args.timezone)
    
    if args.format == 'time':
        time_info = server.get_current_time()
        if args.format == 'json':
            print(json.dumps(time_info, ensure_ascii=False, indent=2))
        else:
            print(server.format_time(time_info))
            
    elif args.format == 'date':
        date_info = server.get_current_date()
        if args.format == 'json':
            print(json.dumps(date_info, ensure_ascii=False, indent=2))
        else:
            print(server.format_date(date_info))
            
    elif args.format == 'json':
        dt_info = server.get_datetime_info()
        print(json.dumps(dt_info, ensure_ascii=False, indent=2))
        
    else:  # 'full'
        dt_info = server.get_datetime_info()
        print(server.format_datetime_info(dt_info))


if __name__ == "__main__":
    main()
