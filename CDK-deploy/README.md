# AWS CDK로 Bedrock 챗봇 배포하기

Amazon Bedrock의 Claude 3.5 Sonnet 모델을 활용한 챗봇을 AWS 클라우드 환경에 자동으로 배포하는 CDK 템플릿입니다.

## 아키텍처 개요

![Architecture diagram](/CDK-deploy/img/archi_streamlit_cdk.png)

### 주요 구성 요소
- **프론트엔드**: Streamlit 기반 웹 인터페이스
- **컨테이너 환경**: ECS Fargate
- **로드밸런싱**: Application Load Balancer (ALB)
- **콘텐츠 전송**: CloudFront
- **네트워크**: VPC, 보안 그룹, NAT Gateway

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

## 사전 요구사항

### 시스템 요구사항
- Python 3.9 이상
- Docker
- Chrome 브라우저 (개발용)
- AWS CLI 구성 및 적절한 권한

### Bedrock 모델 접근 권한
- [필수] Claude 3.5 Sonnet v2 (us-west-2 리전)
  - 모델 ID: anthropic.claude-3-5-sonnet-20241022-v2:0
- [필수] Claude 3.5 Sonnet v1 (다중 리전)
  - 모델 ID: anthropic.claude-3-5-sonnet-20240620-v1:0
  - 필요 리전: us-east-1, us-east-2, us-west-2, ap-northeast-1, ap-northeast-2

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
- 서울 리전(ap-northeast-2)에 배포 가능

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

## 참조
- [Streamlit CDK Fargate](https://github.com/tzaffi/streamlit-cdk-fargate.git)
- [AWS Bedrock Workshop](https://github.com/aws-samples/build-scale-generative-ai-applications-with-amazon-bedrock-workshop/)

## 라이선스
이 애플리케이션은 MIT-0 라이선스를 따릅니다. LICENSE 파일을 참조하세요.
