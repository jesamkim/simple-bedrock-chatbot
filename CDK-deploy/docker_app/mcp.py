#!/usr/bin/env python
import os
import json
import sys
import importlib
from typing import Dict, Any, List, Optional

# MCP SDK 임포트
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
    print("MCP SDK가 설치되어 있지 않습니다. pip install modelcontextprotocol을 실행하세요.", file=sys.stderr)
    sys.exit(1)

class MCPServer:
    """통합 MCP 서버 클래스"""
    
    def __init__(self, config: Dict[str, Any] = None):
        # 기본 설정
        self.config = config or {}
        
        # MCP 서버 설정
        self.server = Server(
            {
                "name": "unified-mcp-server",
                "version": "1.0.0",
            },
            {
                "capabilities": {
                    "tools": {},
                },
            }
        )
        
        # 서비스 컨테이너 - 각 서비스의 인스턴스를 저장
        self.services = {}
        
        # 도구 매핑 - 도구 이름과 해당 서비스 연결
        self.tool_mapping = {}
        
        # 서비스 로드
        self._load_services()
        
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
    
    def _load_services(self):
        """설정된 서비스 로드"""
        # 기본 서비스 설정 - 날짜/시간 및 검색 서비스
        services_config = self.config.get("services", [
            {
                "name": "datetime",
                "module": "datetime_mcp_server",
                "class": "DatetimeServer",
                "params": {"timezone": "Asia/Seoul"}
            },
            {
                "name": "search",
                "module": "google_search_mcp_server", 
                "class": "GoogleSearchServer",
                "params": {"max_results": 5}
            }
        ])
        
        # 각 서비스 동적 로드
        for service_config in services_config:
            try:
                service_name = service_config["name"]
                module_name = service_config["module"]
                class_name = service_config["class"]
                params = service_config.get("params", {})
                
                # 모듈 동적 로드
                module = importlib.import_module(module_name)
                service_class = getattr(module, class_name)
                
                # 서비스 인스턴스 생성
                service_instance = service_class(**params)
                self.services[service_name] = service_instance
                
                print(f"서비스 '{service_name}' 로드 완료", file=sys.stderr)
                
                # 도구 매핑 설정
                tools = self._get_service_tools(service_name, service_instance)
                for tool_name in tools:
                    self.tool_mapping[tool_name] = service_name
                    
            except Exception as e:
                print(f"서비스 '{service_config.get('name', '알 수 없음')}' 로드 실패: {str(e)}", file=sys.stderr)
    
    def _get_service_tools(self, service_name: str, service_instance: Any) -> List[str]:
        """서비스가 제공하는 도구 이름 목록 반환"""
        # 날짜/시간 서비스 도구
        if service_name == "datetime":
            return ["get_current_time", "get_current_date", "get_datetime_info"]
        # 검색 서비스 도구
        elif service_name == "search":
            return ["search", "extract_keywords"]
        # 기타 서비스는 빈 목록 반환 (확장 가능)
        return []
    
    def setup_tool_handlers(self):
        """MCP 도구 핸들러 설정"""
        
        # 도구 목록 요청 처리
        self.server.set_request_handler(ListToolsRequestSchema, self._handle_list_tools)
        
        # 도구 호출 요청 처리
        self.server.set_request_handler(CallToolRequestSchema, self._handle_call_tool)
    
    async def _handle_list_tools(self, request):
        """사용 가능한 모든 도구 목록 반환"""
        tools = []
        
        # 날짜/시간 서비스 도구
        if "datetime" in self.services:
            tools.extend([
                {
                    "name": "get_current_time",
                    "description": "현재 시간 정보를 반환합니다",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_current_date",
                    "description": "현재 날짜 정보를 반환합니다",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_datetime_info",
                    "description": "현재 날짜와 시간의 종합 정보를 반환합니다",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ])
        
        # 검색 서비스 도구
        if "search" in self.services:
            tools.extend([
                {
                    "name": "search",
                    "description": "웹 검색을 수행합니다",
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
            ])
        
        # 여기에 추가 서비스의 도구 정의를 추가할 수 있습니다
        
        return {"tools": tools}
    
    async def _handle_call_tool(self, request):
        """도구 호출 처리 - 적절한 서비스로 라우팅"""
        tool_name = request.params.name
        args = request.params.arguments
        
        # 도구 이름으로 서비스 찾기
        service_name = self.tool_mapping.get(tool_name)
        if not service_name or service_name not in self.services:
            raise McpError(
                ErrorCode.MethodNotFound, 
                f"알 수 없는 도구: {tool_name}"
            )
        
        # 적절한 서비스 인스턴스 가져오기
        service = self.services[service_name]
        
        try:
            # 날짜/시간 서비스 도구 처리
            if service_name == "datetime":
                if tool_name == "get_current_time":
                    result = service.get_current_time()
                    formatted_result = service.format_time(result)
                    return {"content": [{"type": "text", "text": formatted_result}]}
                
                elif tool_name == "get_current_date":
                    result = service.get_current_date()
                    formatted_result = service.format_date(result)
                    return {"content": [{"type": "text", "text": formatted_result}]}
                
                elif tool_name == "get_datetime_info":
                    result = service.get_datetime_info()
                    formatted_result = service.format_datetime_info(result)
                    return {"content": [{"type": "text", "text": formatted_result}]}
            
            # 검색 서비스 도구 처리
            elif service_name == "search":
                if tool_name == "search":
                    if not isinstance(args, dict) or "query" not in args:
                        raise McpError(
                            ErrorCode.InvalidParams,
                            "검색 쿼리가 제공되지 않았습니다"
                        )
                    
                    query = args["query"]
                    max_results = args.get("max_results", 5)
                    
                    results = service.search(query)
                    formatted_results = service.format_results(results)
                    
                    return {"content": [{"type": "text", "text": formatted_results}]}
                
                elif tool_name == "extract_keywords":
                    if not isinstance(args, dict) or "text" not in args:
                        raise McpError(
                            ErrorCode.InvalidParams,
                            "키워드를 추출할 텍스트가 제공되지 않았습니다"
                        )
                    
                    text = args["text"]
                    keywords = service.extract_keywords(text)
                    
                    return {
                        "content": [
                            {"type": "text", "text": f"추출된 키워드: {', '.join(keywords)}"}
                        ]
                    }
            
            # 여기에 추가 서비스의 도구 처리 로직을 추가할 수 있습니다
            
            raise McpError(
                ErrorCode.MethodNotFound, 
                f"처리할 수 없는 도구: {tool_name}"
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
        print("통합 MCP 서버가 stdio에서 실행 중입니다.", file=sys.stderr)


def main():
    """메인 함수"""
    import asyncio
    
    # 설정 파일 로드 (있는 경우)
    config = {}
    config_file = os.environ.get("MCP_CONFIG", "mcp_config.json")
    try:
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                config = json.load(f)
    except Exception as e:
        print(f"설정 파일 로드 실패: {str(e)}", file=sys.stderr)
    
    server = MCPServer(config)
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\n서버를 종료합니다...", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()
