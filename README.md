# Amazon Bedrock의 Claude 3.5 Sonnet을 활용한 간단한 Chatbot
Amazon Bedrock (Claude 3.5 Sonnet) & LangChain & Streamlit으로 구성하는 간단 챗봇 애플리케이션

## 프로젝트 구조
```
.
├── claude-3-5/              # Claude 3.5 Sonnet 챗봇 애플리케이션
│   ├── app.py              # Streamlit 기반 메인 애플리케이션
│   └── requirements.txt     # 필요한 패키지 목록
│
├── CDK-deploy/             # AWS CDK를 통한 인프라 배포
│   ├── cdk/               
│   │   └── cdk_stack.py    # CDK 스택 정의 (VPC, ECS, CloudFront 등)
│   ├── docker_app/         # Docker 컨테이너 애플리케이션
│   │   ├── app.py         # Docker 환경의 애플리케이션
│   │   ├── Dockerfile     # 컨테이너 이미지 정의
│   │   └── utils/         # 유틸리티 함수들
│   └── requirements.txt    # CDK 배포에 필요한 패키지 목록
```

## 주요 기능
1. **멀티 리전 지원**
   - Claude 3.5 Sonnet v1: us-east-1, us-east-2, us-west-2, ap-northeast-1, ap-northeast-2 리전 지원
   - Claude 3.5 Sonnet v2: us-west-2 리전 지원
   - RPM (Request per Minute) Quota 제한을 고려한 리전 순환 로직 구현

2. **대화 인터페이스**
   - Streamlit을 활용한 직관적인 웹 인터페이스
   - 실시간 스트리밍 응답
   - 대화 기록 유지 및 관리

3. **커스터마이징 가능한 파라미터**
   - Temperature, Top-P, Top-K 등 생성 파라미터 조정
   - 시스템 프롬프트 설정
   - 메모리 윈도우 크기 조정
   - 최대 토큰 수 설정

4. **인프라 자동화**
   - AWS CDK를 통한 인프라 자동 프로비저닝
   - ECS Fargate를 통한 컨테이너 실행
   - CloudFront를 통한 글로벌 배포
   - ALB를 통한 로드 밸런싱

## 환경 요구사항
- [중요 #1] AWS 계정에서 anthropic.claude-3-5-sonnet-20241022-v2:0 (Claude 3.5 Sonnet v2) 모델이 us-west-2 리전에 Access Granted 되어 있어야 합니다.
- [중요 #2] AWS 계정에서 anthropic.claude-3-5-sonnet-20240620-v1:0 (Claude 3.5 Sonnet v1) 모델이 us-east-1, us-east-2, us-west-2, ap-northeast-1, ap-northeast-2 리전에 모두 Access Granted 되어 있어야 합니다.

## 로컬 실행 방법
1. 패키지 설치
```bash
pip install -r ./claude-3-5/requirements.txt -U
```

2. Streamlit 앱 실행
```bash
streamlit run ./claude-3-5/app.py --server.port 8080
```

## AWS 배포 방법
1. CDK 패키지 설치
```bash
cd CDK-deploy
pip install -r requirements.txt
```

2. CDK 배포
```bash
cdk deploy
```

## 스크린샷
![screenshot1-1](./img/screenshot1-1.png)

## 참조
- [Bedrock-ChatBot-with-LangChain-and-Streamlit](https://github.com/davidshtian/Bedrock-ChatBot-with-LangChain-and-Streamlit)
- [aws-samples/deploy-streamlit-app](https://github.com/aws-samples/deploy-streamlit-app)
