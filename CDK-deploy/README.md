# CDK 배포 - Claude 3.7 Sonnet MCP 챗봇

## 아키텍처 구성도

```mermaid
flowchart LR
    Client([사용자]) --> CloudFront[CloudFront - 분산 컨텐츠 전송 네트워크]
    CloudFront --> ALB[Application Load Balancer - 트래픽 분산]
    ALB --> ECS[Amazon ECS - Bedrock 챗봇 컨테이너]
    
    %% 서브그래프로 ECS 컨테이너 내부 구조 표현
    subgraph ECSContainer[ECS 컨테이너 내부]
        App[호스트 앱 : app.py / Streamlit] --> UnifiedClient[통합 MCP 클라이언트 : mcp_client.py]
        UnifiedClient --> UnifiedServer[통합 MCP 서버 : mcp.py]
        UnifiedServer --> Services[서비스 컨테이너]
        
        %% 서비스들
        Services --> DTService[날짜/시간 서비스 : datetime_mcp_server.py]
        Services --> SearchService[검색 서비스 : google_search_mcp_server.py]
        
        %% 외부 API 연결
        DTService --> SystemTime[시스템 날짜/시간]
        SearchService --> GoogleAPI[Google Search API]
    end
    
    ECS --> Bedrock[Amazon Bedrock - Claude 3.7 Sonnet]
    
    %% 스타일 정의
    classDef aws fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#232F3E;
    classDef client fill:#D4F4FA,stroke:#0078D4,stroke-width:2px,color:#000000;
    classDef mcp fill:#B9EDDD,stroke:#0B666A,stroke-width:2px,color:#000000;
    classDef service fill:#E8DAEF,stroke:#8E44AD,stroke-width:2px,color:#000000;
    classDef external fill:#F8F0E5,stroke:#35374B,stroke-width:1px,color:#000000;
    
    %% 스타일 적용
    class CloudFront,ALB,ECS,Bedrock aws;
    class Client client;
    class App,UnifiedClient,UnifiedServer mcp;
    class Services,DTService,SearchService service;
    class GoogleAPI,SystemTime external;
```

## 아키텍처 개요

이 프로젝트는 다음과 같은 AWS 클라우드 아키텍처를 기반으로 배포됩니다:

1. **사용자 접근**: 사용자는 CloudFront를 통해 웹 애플리케이션에 접속합니다.
2. **트래픽 분산**: CloudFront는 트래픽을 Application Load Balancer(ALB)로 전달하고, ALB는 이를 ECS 컨테이너로 분산시킵니다.
3. **챗봇 컨테이너**: ECS에서 실행되는 컨테이너 내부에는:
   - Streamlit 기반의 호스트 앱(app.py)
   - MCP 클라이언트 및 서버 컴포넌트
   - Google 검색 및 날짜/시간 정보 기능
4. **AI 모델**: 챗봇은 Amazon Bedrock의 Claude 3.7 Sonnet 모델을 사용하여 사용자 질의에 응답합니다.
5. **외부 서비스**: MCP 서버는 Google Search API 및 시스템 시간/날짜 기능과 같은 외부 서비스와 통신합니다.


이 프로젝트는 Amazon Bedrock의 Claude 3.7 Sonnet을 사용하여 구현된 지능형 챗봇으로, Model Context Protocol (MCP)를 통해 두 가지 추가 기능을 제공합니다:

1. Google 웹 검색 기능
2. 현재 날짜/시간 정보 제공 기능

## 주요 기능

### LLM 기반 의도 분석 (Intent Analysis)

- Claude 3.7의 추론 능력을 활용하여 사용자 질의의 의도를 분석
- 현재 시간/날짜 정보가 필요한지, 인터넷 검색이 필요한지를 자동으로 판단
- 복합적인 질의(예: "마비노기 모바일이 출시된지 얼마나 지났어?")도 정확하게 분석

### MCP 구조 

#### MCP 호출 흐름

Model Context Protocol(MCP)의 호출 흐름은 다음과 같은 계층 구조로 이루어집니다:

```mermaid
flowchart LR
    HostApp[호스트 앱 - app.py] --> UnifiedClient[통합 MCP 클라이언트 - mcp_client.py]
    UnifiedClient --> UnifiedServer[통합 MCP 서버 - mcp.py]
    UnifiedServer --> Services[서비스 컨테이너]
    Services --> DTService[날짜/시간 서비스]
    Services --> SearchService[검색 서비스]
    Services --> OtherService[기타 서비스...]
    DTService --> ExternalAPI1[시스템 시간 API]
    SearchService --> ExternalAPI2[Google Search API]
    OtherService --> ExternalAPI3[기타 외부 API]
    
    %% 스타일 정의
    classDef host fill:#D4E6F1,stroke:#3498DB,stroke-width:2px,color:#000000;
    classDef client fill:#D5F5E3,stroke:#2ECC71,stroke-width:2px,color:#000000;
    classDef server fill:#FCF3CF,stroke:#F1C40F,stroke-width:2px,color:#000000;
    classDef service fill:#E8DAEF,stroke:#8E44AD,stroke-width:2px,color:#000000;
    classDef external fill:#FADBD8,stroke:#E74C3C,stroke-width:2px,color:#000000;
    
    %% 스타일 적용
    class HostApp host;
    class UnifiedClient client;
    class UnifiedServer server;
    class Services,DTService,SearchService,OtherService service;
    class ExternalAPI1,ExternalAPI2,ExternalAPI3 external;
```

1. **호스트 애플리케이션(app.py)**
   - Streamlit 기반 메인 애플리케이션
   - 통합 MCP 클라이언트를 초기화하고 필요시 해당 기능 호출
   - 사용자 질의 의도를 분석하여 적절한 MCP 서비스 선택

2. **통합 MCP 클라이언트**
   - `mcp_client.py` 파일로 구현
   - 호스트 앱과 통합 MCP 서버 간의 인터페이스 제공
   - 일관된 API를 통해 모든 서비스 접근 가능

3. **통합 MCP 서버**
   - `mcp.py`에서 여러 서비스를 통합 관리
   - 설정 파일(`mcp_config.json`)에 기반한 서비스 동적 로드
   - 도구 요청을 적절한 서비스로 라우팅
   - 비동기(asyncio) 방식으로 구현
   - stdio 기반 통신(`StdioServerTransport` 클래스 사용)

4. **서비스 구현**
   - `XXX_mcp_server.py` 파일에서 실제 기능 구현
   - 독립적인 서비스 클래스로 구현되어 쉽게 확장 가능

5. **외부 서비스/API**
   - Google Custom Search API, 시스템 날짜/시간 기능 등 실제 서비스

### MCP 구현 기능 설명 
#### 1. Google 웹 검색 기능
- 사용자 질문에서 관련 키워드를 추출하여 Google 검색 API를 통해 웹 검색 수행
- 검색 결과를 가독성 있게 포맷팅하여 모델에게 제공
- 최신 정보에 기반한 답변 제공 가능

#### 2. 날짜/시간 정보 기능
- 날짜/시간 질의에 대해 정확한 정보 제공 (한국어/영어 지원)
- 현재 시간, 날짜, 요일, 경과 일수 등 다양한 정보 제공
- 날짜 간 시간 계산 기능 (예: 특정 일자 이후 경과 시간 계산)

#### 3. 복합 기능
- 검색 결과와 시간 정보를 결합하여 분석
- "출시일로부터 지난 시간" 등의 복합적인 질의에 정확한 응답

### 작동 모드

1. **기본 모드**: 일반적인 AI 챗봇 기능
2. **MCP 모드**: 웹 검색 및 날짜/시간 정보 제공 기능 활성화
3. **Reasoning 모드**: Claude 3.7의 사고 과정(Thinking)을 볼 수 있는 모드

## 새로운 MCP 서비스 추가 가이드

통합 MCP 구조를 활용하여 새로운 서비스를 쉽게 추가할 수 있습니다:

### 1. 서비스 구현 클래스 생성
`XXX_mcp_server.py` 파일에 새 서비스를 구현합니다:

```python
class NewService:
    """새로운 MCP 서비스 구현"""
    
    def __init__(self, param1="default", param2="default"):
        """서비스 초기화"""
        self.param1 = param1
        self.param2 = param2
    
    def some_tool_method(self, arg1, arg2=None):
        """도구 기능 구현"""
        # 기능 구현 코드
        result = {"some_key": "some_value"}
        return result
    
    def format_result(self, result):
        """결과 포맷팅"""
        # 결과를 읽기 쉬운 형태로 변환
        return f"포맷된 결과: {result['some_key']}"
```

### 2. 설정 파일에 서비스 등록
`mcp_config.json` 파일에 새 서비스를 추가합니다:

```json
{
  "services": [
    {
      "name": "datetime",
      "module": "datetime_mcp_server",
      "class": "DatetimeServer",
      "params": {
        "timezone": "Asia/Seoul"
      }
    },
    {
      "name": "search",
      "module": "google_search_mcp_server",
      "class": "GoogleSearchServer",
      "params": {
        "max_results": 5
      }
    },
    {
      "name": "new_service_name",
      "module": "new_service_mcp_server",
      "class": "NewService",
      "params": {
        "param1": "value1",
        "param2": "value2"
      }
    }
  ]
}
```

### 3. 필요한 경우 MCP 서버 확장
특수한 처리 로직이 필요한 경우, `mcp.py` 파일을 수정합니다:

1. `_get_service_tools` 메서드에 도구 목록 추가:
   ```python
   elif service_name == "new_service_name":
       return ["some_tool_method", "another_tool_method"]
   ```

2. `_handle_list_tools` 메서드에 도구 정의 추가:
   ```python
   # 새 서비스 도구
   if "new_service_name" in self.services:
       tools.extend([
           {
               "name": "some_tool_method",
               "description": "도구에 대한 설명",
               "inputSchema": {
                   "type": "object",
                   "properties": {
                       "arg1": {
                           "type": "string",
                           "description": "매개변수 설명"
                       }
                   },
                   "required": ["arg1"]
               }
           }
       ])
   ```

3. `_handle_call_tool` 메서드에 도구 호출 처리 로직 추가:
   ```python
   elif service_name == "new_service_name":
       if tool_name == "some_tool_method":
           result = service.some_tool_method(args.get("arg1"))
           formatted_result = service.format_result(result)
           return {"content": [{"type": "text", "text": formatted_result}]}
   ```

### 4. 환경 변수 설정 (필요한 경우)
서비스에 외부 API 키 등이 필요한 경우 환경 변수를 설정합니다:

```bash
export NEW_SERVICE_API_KEY="your-api-key-here"
```

## CDK 배포 방법

1. 프로젝트 클론:
   ```bash
   git clone https://github.com/jesamkim/simple-bedrock-chatbot.git
   cd simple-bedrock-chatbot
   ```

2. CDK-deploy 디렉토리로 이동:
   ```bash
   cd CDK-deploy
   ```

3. 가상환경 생성 및 활성화:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   ```

4. 필요한 패키지 설치:
   ```bash
   pip install -r requirements.txt
   ```

5. 환경 변수 설정:
<b>Google 검색 기능을 사용하기 위해 GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID에 대한 환경변수 등록이 필요합니다.</b>

   ```bash
   export AWS_ACCESS_KEY_ID="your-aws-access-key"
   export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
   export AWS_REGION="us-west-2"
   
   export GOOGLE_API_KEY="your-api-key-here"
   export GOOGLE_SEARCH_ENGINE_ID="your-search-engine-id-here"
   ```

5-1. 또는 `.env` 파일을 생성해 환경 변수를 관리할 수도 있습니다:
   ```bash
   # .env 파일 생성
   cat > .env << EOL
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   AWS_REGION=us-west-2
   GOOGLE_API_KEY=your-api-key-here
   GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id-here
   EOL
   
   # .env 파일 로드
   source .env
   ```

6. CDK 부트스트랩 (AWS 계정/리전에서 최초 1회만 실행):
   ```bash
   cdk bootstrap
   ```

7. CDK 배포 실행:
   ```bash
   cdk deploy
   ```

8. 배포 완료 후 CloudFront URL 확인:
   ```bash
   # 출력 예시
   Outputs:
   cdk-chatbot-claude3.CloudFrontDistributionURL = xxx2cj9ksuhwvn.cloudfront.net
   ```

9. 생성된 CloudFront URL로 브라우저에서 접속하여 챗봇 사용


## 프로젝트 구조

### 핵심 파일
- `app.py`: 메인 Streamlit 애플리케이션

### 통합 MCP 파일
- `mcp.py`: 통합 MCP 서버 구현 (모든 서비스 관리)
- `mcp_client.py`: 통합 MCP 클라이언트 인터페이스
- `mcp_config.json`: MCP 서비스 구성 정의 파일

### 서비스 구현 파일
- `datetime_mcp_server.py`: 날짜/시간 정보 서비스 구현
- `google_search_mcp_server.py`: Google 검색 서비스 구현


## 사용 방법

1. 좌측 사이드바에서 원하는 모드 선택 (MCP 모드 권장)
2. MCP 모드에서는 질문하면 자동으로 모델이 필요한 정보(웹 검색/시간)를 판단하여 사용
3. 질문 예시:
   - "지금 몇 시야?"
   - "마비노기 모바일이 출시된지 얼마나 지났어?"


## 스크린샷

### 챗봇 실행 화면
문서 업로드 및 Q&A 챗봇 인터페이스:

![Chatbot Screenshot](../img/screenshot2.png)


## 참조
- [Streamlit CDK Fargate](https://github.com/tzaffi/streamlit-cdk-fargate.git)
- [AWS Bedrock Workshop](https://github.com/aws-samples/build-scale-generative-ai-applications-with-amazon-bedrock-workshop/)
- [kyopark2014/mcp](https://github.com/kyopark2014/mcp)

## 라이선스
이 애플리케이션은 MIT-0 라이선스를 따릅니다. LICENSE 파일을 참조하세요.
