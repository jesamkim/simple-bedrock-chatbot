# Claude 3.7 Sonnet MCP 챗봇

이 프로젝트는 Amazon Bedrock의 Claude 3.7 Sonnet을 사용하여 구현된 지능형 챗봇으로, Model Context Protocol (MCP)를 통해 두 가지 추가 기능을 제공합니다:

1. DuckDuckGo 웹 검색 기능
2. 현재 날짜/시간 정보 제공 기능

## 주요 기능

### LLM 기반 의도 분석 (Intent Analysis)

- Claude 3.7의 추론 능력을 활용하여 사용자 질의의 의도를 분석
- 현재 시간/날짜 정보가 필요한지, 인터넷 검색이 필요한지를 자동으로 판단
- 복합적인 질의(예: "마비노기 모바일이 출시된지 얼마나 지났어?")도 정확하게 분석

### MCP 기능 

#### 1. DuckDuckGo 웹 검색 기능
- 사용자 질문에서 관련 키워드를 추출하여 웹 검색 수행
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

## 설치 및 실행 방법

1. 필요한 패키지 설치:
   ```bash
   pip install -r requirements.txt
   ```

2. 애플리케이션 실행:
   ```bash
   streamlit run app.py
   ```

3. 웹 브라우저에서 인터페이스 접속 (기본: http://localhost:8501)

## 프로젝트 구조

- `app.py`: 메인 Streamlit 애플리케이션
- `duckduckgo_mcp_server.py`: 웹 검색 기능 구현
- `duckduckgo_mcp_client.py`: 웹 검색 클라이언트 
- `datetime_mcp_server.py`: 날짜/시간 정보 서버 구현
- `datetime_mcp_client.py`: 날짜/시간 정보 클라이언트

## 사용 방법

1. 좌측 사이드바에서 원하는 모드 선택 (MCP 모드 권장)
2. MCP 모드에서는 질문하면 자동으로 모델이 필요한 정보(웹 검색/시간)를 판단하여 사용
3. 질문 예시:
   - "지금 몇 시야?"
   - "파이썬이란 무엇인가요?"
   - "마비노기 모바일이 출시된지 얼마나 지났어?"

## AWS 설정

이 프로젝트는 AWS Bedrock 서비스를 사용합니다. 다음 환경 변수가 필요합니다:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (기본값: us-west-2)
