#!/usr/bin/env python
import os
import json
import sys
from typing import Dict, Any, List

from google_search_mcp_server import GoogleSearchServer

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

class GoogleSearchMCP:
    def __init__(self):
        """GoogleSearchMCP 초기화"""
        # MCP 서버 설정
        self.server = Server(
            {
                "name": "google-search-server",
                "version": "1.0.0",
            },
            {
                "capabilities": {
                    "tools": {},
                },
            }
        )
        
        # Google 검색 서버 인스턴스 생성 
        self.search_server = GoogleSearchServer(max_results=5)  # 기본값 5개 결과
        
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
                    "name": "search",
                    "description": "Google Custom Search API를 사용하여 웹 검색을 수행합니다",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "검색 쿼리"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "최대 결과 수 (기본값: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "extract_keywords",
                    "description": "텍스트에서 중요 키워드를 추출합니다",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "키워드를 추출할 텍스트"
                            }
                        },
                        "required": ["text"]
                    }
                }
            ]
        }
    
    async def _handle_call_tool(self, request):
        """도구 호출 처리"""
        tool_name = request.params.name
        args = request.params.arguments
        
        try:
            if tool_name == "search":
                if not isinstance(args, dict) or "query" not in args:
                    raise McpError(
                        ErrorCode.InvalidParams,
                        "검색 쿼리가 제공되지 않았습니다"
                    )
                
                query = args["query"]
                max_results = args.get("max_results", 5)
                
                results = self.search_server.search(query)
                formatted_results = self.search_server.format_results(results)
                
                return {"content": [{"type": "text", "text": formatted_results}]}
            
            elif tool_name == "extract_keywords":
                if not isinstance(args, dict) or "text" not in args:
                    raise McpError(
                        ErrorCode.InvalidParams,
                        "키워드를 추출할 텍스트가 제공되지 않았습니다"
                    )
                
                text = args["text"]
                keywords = self.search_server.extract_keywords(text)
                
                return {
                    "content": [
                        {"type": "text", "text": f"추출된 키워드: {', '.join(keywords)}"}
                    ]
                }
            
            else:
                raise McpError(
                    ErrorCode.MethodNotFound, 
                    f"알 수 없는 도구: {tool_name}"
                )
        
        except McpError:
            raise
        except Exception as e:
            raise McpError(
                ErrorCode.InternalError,
                f"도구 실행 중 오류 발생: {str(e)}"
            )
    
    async def run(self):
        """MCP 서버 실행"""
        transport = StdioServerTransport()
        await self.server.connect(transport)
        print("Google Search MCP 서버가 stdio에서 실행 중입니다.", file=sys.stderr)


def main():
    """메인 함수"""
    import asyncio
    
    server = GoogleSearchMCP()
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\n서버를 종료합니다...", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()
