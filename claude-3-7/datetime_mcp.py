#!/usr/bin/env python
import os
import json
import sys
from typing import Dict, Any, List

from datetime_mcp_server import DatetimeServer

# MCP SDK 임포트 (MCP 서버 구현에 필요)
try:
    from modelcontextprotocol.sdk.server import Server
    from modelcontextprotocol.sdk.server.stdio import StdioServerTransport
    from modelcontextprotocol.sdk.types import (
        CallToolRequestSchema,
        ListToolsRequestSchema,
        ErrorCode,
        McpError
    )
except ImportError:
    print("MCP SDK가 설치되어 있지 않습니다. pip install modelcontextprotocol을 실행하세요.")
    sys.exit(1)

class DatetimeMCPServer:
    def __init__(self):
        # MCP 서버 설정
        self.server = Server(
            {
                "name": "datetime-server",
                "version": "1.0.0",
            },
            {
                "capabilities": {
                    "tools": {},
                },
            }
        )
        
        # DatetimeServer 인스턴스 생성 (기본 시간대: Asia/Seoul)
        timezone = os.environ.get('TIMEZONE', 'Asia/Seoul')
        self.datetime_server = DatetimeServer(timezone=timezone)
        
        # 도구 핸들러 설정
        self.setup_tool_handlers()
        
        # 오류 처리
        self.server.onerror = lambda error: print(f"[MCP 오류] {error}", file=sys.stderr)
        
        # 종료 시그널 처리
        import signal
        signal.signal(signal.SIGINT, self._handle_sigint)
    
    def _handle_sigint(self, sig, frame):
        """Ctrl+C 처리"""
        print("\n서버를 종료합니다...", file=sys.stderr)
        self.server.close()
        sys.exit(0)
    
    def setup_tool_handlers(self):
        """MCP 도구 핸들러 설정"""
        
        # 도구 목록 요청 처리
        self.server.set_request_handler(ListToolsRequestSchema, self._handle_list_tools)
        
        # 도구 호출 요청 처리
        self.server.set_request_handler(CallToolRequestSchema, self._handle_call_tool)
    
    async def _handle_list_tools(self, request):
        """사용 가능한 도구 목록 반환"""
        return {
            "tools": [
                {
                    "name": "get_current_time",
                    "description": "현재 시간 정보를 반환합니다 (Asia/Seoul 기준)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_current_date",
                    "description": "현재 날짜 정보를 반환합니다 (Asia/Seoul 기준)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_datetime_info",
                    "description": "현재 날짜와 시간의 종합 정보를 반환합니다 (Asia/Seoul 기준)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
            ]
        }
    
    async def _handle_call_tool(self, request):
        """도구 호출 처리"""
        tool_name = request.params.name
        
        try:
            if tool_name == "get_current_time":
                result = self.datetime_server.get_current_time()
                formatted_result = result["formatted"]
                return {"content": [{"type": "text", "text": formatted_result}]}
            
            elif tool_name == "get_current_date":
                result = self.datetime_server.get_current_date()
                formatted_result = result["formatted"]
                return {"content": [{"type": "text", "text": formatted_result}]}
            
            elif tool_name == "get_datetime_info":
                result = self.datetime_server.get_datetime_info()
                formatted_result = result["formatted"]
                detailed_info = (
                    f"날짜: {result['date']}\n"
                    f"시간: {result['time']}\n"
                    f"요일: {result['weekday']}\n"
                    f"시간대: {result['timezone']}"
                )
                return {"content": [{"type": "text", "text": f"{formatted_result}\n\n{detailed_info}"}]}
            
            else:
                raise McpError(
                    ErrorCode.MethodNotFound, 
                    f"알 수 없는 도구: {tool_name}"
                )
        
        except Exception as e:
            raise McpError(
                ErrorCode.InternalError,
                f"도구 실행 중 오류 발생: {str(e)}"
            )
    
    async def run(self):
        """MCP 서버 실행"""
        transport = StdioServerTransport()
        await self.server.connect(transport)
        print("DatetimeMCP 서버가 stdio에서 실행 중입니다.", file=sys.stderr)

def main():
    """메인 함수"""
    import asyncio
    
    server = DatetimeMCPServer()
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\n서버를 종료합니다...", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()
