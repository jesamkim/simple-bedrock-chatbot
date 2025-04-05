# AWS CDK로 Bedrock 챗봇 배포하기

Amazon Bedrock의 Claude 3.7 Sonnet 모델을 활용한 문서 기반 Q&A 챗봇을 AWS 클라우드 환경에 자동으로 배포하는 CDK 템플릿입니다.

## 아키텍처 개요

![Architecture diagram](/CDK-deploy/img/archi_streamlit_cdk.png)

### 주요 구성 요소
- **프론트엔드**: Streamlit 기반 웹 인터페이스
- **컨테이너 환경**: ECS Fargate
- **로드밸런싱**: Application Load Balancer (ALB)
- **콘텐츠 전송**: CloudFront
- **네트워크**: VPC, 보안 그룹, NAT Gateway

### 챗봇 주요 기능
1. **문서 처리 기능**
   - 다양한 문서 형식 지원 (PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, CSV, TXT, MD, HTML)
   - 실시간 문서 업로드 및 텍스트 추출
   - 문서 기반 Q&A 수행

2. **Amazon Bedrock 통합**
   - **모델**
     - Claude 3.7 Sonnet : 높은 정확도와 문맥 이해력
   - **Model reasoning 모드** (Claude 3.7 Sonnet 전용)
     - 복잡한 문제 해결을 위한 고급 추론 기능
     - 최대 64,000 길이 지원
     - 최대 4,096 토큰의 추론 과정 활용
     - Temperature 1.0 고정 및 Top-K/Top-P 비활성화
   - 스트리밍 방식의 실시간 응답
   - 한국어 응답 최적화

3. **사용자 인터페이스**
   - 직관적인 문서 업로드
   - 실시간 채팅 인터페이스
   - 모델 파라미터 조정 기능

### 아키텍처 특징
1. **고가용성**
   - 다중 가용 영역(AZ) 구성
   - ALB를 통한 로드 밸런싱
   - CloudFront를 통한 글로벌 배포

2. **보안**
   - VPC 내 프라이빗 서브넷에서 Fargate 작업 실행
   - 보안 그룹을 통한 트래픽 제어
   - CloudFront와 ALB 간 커스텀 헤더 검증

3. **확장성**
   - Fargate를 통한 자동 스케일링
   - CloudFront를 통한 글로벌 캐싱

## Model Context Protocol(MCP) 기능

이 프로젝트는 Claude와 같은 AI 모델이 외부 서비스와 상호작용할 수 있도록 Model Context Protocol(MCP)를 구현하고 있습니다.

### MCP 개요
- **Model Context Protocol**: AI 모델이 실시간 데이터 액세스, 외부 API 호출 등 다양한 기능을 활용할 수 있게 해주는 프로토콜
- **목적**: AI 모델의 기능 확장, 실시간 정보 접근성 향상, 외부 시스템과의 통합

### 구현된 MCP 서버
현재 다음 MCP 서버들이 구현되어 있습니다:

1. **Datetime MCP 서버**
   - **기능**: 현재 날짜/시간 정보 제공
   - **주요 도구**:
     - `get_current_time`: 현재 시간 정보 반환
     - `get_current_date`: 현재 날짜 정보 반환
     - `get_datetime_info`: 종합적인 날짜/시간 정보 제공
   - **특징**: 한국어 날짜/시간 표기, 시간대 설정, 시간 차이 계산

2. **DuckDuckGo MCP 서버**
   - **기능**: 실시간 웹 검색 결과 제공
   - **주요 기능**:
     - 검색 쿼리 처리 및 결과 반환
     - 텍스트에서 중요 키워드 추출
     - 검색 결과 포맷팅
   - **특징**: 검색 결과 개수 설정, JSON 형식 출력 지원

### MCP 활용 방법

#### 챗봇에서의 활용
- **실시간 정보**: 챗봇이 현재 날짜/시간 정보를 실시간으로 제공
- **웹 검색**: 사용자 질문에 대한 최신 정보를 웹에서 검색하여 답변에 활용
- **자연스러운 대화**: 시간 기반 인사말, 최신 정보를 반영한 응답 생성

#### MCP 서버 확장 방법
이 프로젝트의 MCP 구현은 다음과 같이 확장할 수 있습니다:

```python
# MCP 서버 생성 예시
class CustomMCPServer:
    def __init__(self):
        self.server = Server(
            {"name": "custom-server", "version": "1.0.0"},
            {"capabilities": {"tools": {}}}
        )
        # 도구 핸들러 설정 및 서버 기능 구현
```

## 사전 요구사항

### 시스템 요구사항
- Python 3.9 이상
- Docker
- Chrome 브라우저 (개발용)
- AWS CLI 구성 및 적절한 권한

### Bedrock 모델 접근 권한
- [필수] Claude 3.7 Sonnet 모델에 대한 접근 권한 (us-west-2 리전)
  - 모델 ID: anthropic.claude-3-7-sonnet-20250219-v1:0

### 필요한 IAM 권한
- Amazon Bedrock 관련:
  - `bedrock:InvokeModel`
  - `bedrock:InvokeModelWithResponseStream`
- ECS/Fargate 관련 권한
- CloudFront 관련 권한
- ALB 관련 권한

## 배포 가이드

### 1. 프로젝트 설정
```bash
# 리포지토리 클론
git clone https://github.com/jesamkim/simple-bedrock-chatbot.git
cd simple-bedrock-chatbot/CDK-deploy

# (선택사항) 설정 커스터마이징
# docker_app/config_file.py 에서 STACK_NAME과 CUSTOM_HEADER_VALUE 수정
```

### 2. 개발 환경 설정
```bash
# 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. CDK 배포
```bash
# CDK 부트스트랩 (최초 1회)
cdk bootstrap

# 스택 배포
cdk deploy
```
- 배포 소요 시간: 약 10분
- 배포 완료 시 CloudFront URL 제공

### 4. 배포 확인
```bash
# 출력 예시
Outputs:
cdk-chatbot-claude3.CloudFrontDistributionURL = xxx2cj9ksuhwvn.cloudfront.net
```

## 로컬 개발 환경 설정 (선택사항)

### 1. 가상환경 전환
```bash
# CDK 가상환경 비활성화
deactivate

# 앱 디렉토리로 이동
cd docker_app

# 새 가상환경 설정
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 로컬 실행
```bash
# Streamlit 서버 실행
streamlit run app.py --server.port 8080
```

## 챗봇 사용 방법

1. **모델**
   - Claude 3.7 Sonnet

2. **문서 업로드**
   - 지원되는 파일 형식 중 하나를 선택하여 업로드
   - 업로드 성공 시 알림 메시지 확인

3. **파라미터 설정**
   - **Model reasoning 모드** (Claude 3.7 Sonnet 전용)
     - 복잡한 문제 해결이 필요할 때 활성화
     - 활성화 시 Temperature는 1.0으로 고정되며 Top-K/Top-P 설정이 비활성화됨
     - 최대 64,000 길이와 최대 4,096 토큰의 추론 과정 지원
   - Temperature: 응답의 창의성 조절 (0.0 ~ 1.0)
   - Top-P: 토큰 샘플링 확률 조절
   - Top-K: 고려할 최상위 토큰 수 설정
   - Max Token: 최대 응답 길이 설정 (기본 최대 8,192 토큰)
   - Memory Window: 대화 기억 범위 설정

4. **대화하기**
   - 업로드된 문서 내용에 대해 질문 입력
   - 실시간 스트리밍 방식으로 답변 확인
   - 새로운 문서로 시작하려면 'New Chat' 버튼 클릭

## 보안 고려사항

### 현재 구현된 보안 기능
- VPC 내 프라이빗 서브넷 사용
- 보안 그룹을 통한 트래픽 제어
- CloudFront-ALB 간 커스텀 헤더 검증

### 프로덕션 배포 시 고려사항
1. **네트워크 보안**
   - ALB-CloudFront 간 HTTPS 통신 구성
   - AWS WAF를 통한 웹 애플리케이션 보호
   - Network ACL을 통한 추가적인 네트워크 제어

2. **모니터링 및 감사**
   - AWS GuardDuty를 통한 위협 탐지
   - Amazon Inspector를 통한 보안 평가
   - CloudWatch를 통한 로깅 및 모니터링

3. **DDoS 보호**
   - AWS Shield 구성 검토
   - CloudFront 보안 헤더 설정

4. **문서 처리 보안**
   - 업로드된 문서의 안전한 처리
   - 임시 파일의 적절한 삭제
   - 파일 크기 제한 설정

## 스크린샷

### 챗봇 실행 화면
문서 업로드 및 Q&A 챗봇 인터페이스:

![Chatbot Screenshot](../img/screenshot2.png)


## 참조
- [Streamlit CDK Fargate](https://github.com/tzaffi/streamlit-cdk-fargate.git)
- [AWS Bedrock Workshop](https://github.com/aws-samples/build-scale-generative-ai-applications-with-amazon-bedrock-workshop/)
- [kyopark2014/mcp](https://github.com/kyopark2014/mcp.git)


## 라이선스
이 애플리케이션은 MIT-0 라이선스를 따릅니다. LICENSE 파일을 참조하세요.
