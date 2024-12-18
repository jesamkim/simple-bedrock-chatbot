# Simple Bedrock Chatbot

Amazon Bedrock을 활용한 문서 기반 Q&A 챗봇 프로젝트입니다.

## 주요 기능

### Amazon Bedrock 통합
- **모델**: Claude 3.5 Sonnet v2 (us-west-2 리전)
  - 최신 버전의 Claude 모델 사용
  - 향상된 문맥 이해 및 응답 생성 능력
  - 한국어 응답 생성 최적화
- **스트리밍 응답**: 실시간 응답 생성 지원
- **문서 처리**: 다양한 형식의 문서 파일 처리 및 텍스트 추출
- **모델 파라미터 제어**:
  - Temperature 조절을 통한 응답 다양성 제어
  - Top-P, Top-K를 통한 토큰 샘플링 최적화
  - 최대 토큰 수 제한으로 응답 길이 조절

### Amazon Bedrock 특징
- **고성능 LLM 액세스**: 
  - Claude 3.5 Sonnet의 강력한 자연어 처리 능력 활용
  - 문서 내용에 대한 정확한 이해와 관련 정보 추출
  - 맥락을 고려한 응답 생성
- **보안 및 규정 준수**:
  - AWS의 엔터프라이즈급 보안 인프라 활용
  - 데이터 프라이버시 보호
  - IAM을 통한 접근 제어
- **확장성**:
  - 대용량 문서 처리 가능
  - 다양한 문서 형식 지원
  - 실시간 응답 처리

### 지원되는 문서 형식
- **문서 파일**: PDF, DOC, DOCX
- **프레젠테이션**: PPT, PPTX
- **스프레드시트**: XLS, XLSX, CSV
- **텍스트 기반**: TXT, MD, HTML

### 사용자 인터페이스
- **Streamlit 기반** 웹 인터페이스
- 직관적인 문서 업로드 기능
- 실시간 채팅 인터페이스
- 대화 기록 관리

### 추가 기능
- 시스템 프롬프트 커스터마이징
- 모델 파라미터 조정 (Temperature, Top-P, Top-K 등)
- 메모리 윈도우 크기 조정
- 새로운 채팅 세션 시작

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/jesamkim/simple-bedrock-chatbot.git
cd simple-bedrock-chatbot
```

2. 가상환경 생성 및 활성화 (선택사항)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

3. 필요한 패키지 설치
```bash
cd chatbot-with-doc
pip install -r requirements.txt -U
```

## 실행 방법

```bash
streamlit run chatbot.py --server.port 8080
```

## 사용 방법

1. 웹 브라우저에서 `http://localhost:8080` 접속

2. 사이드바의 "Document Upload" 섹션에서 문서 파일 업로드
   - 지원되는 모든 형식의 파일 업로드 가능
   - 업로드 성공 시 알림 메시지 표시

3. 필요한 경우 추론 파라미터 조정
   - Temperature: 응답의 창의성 조절 (0.0 ~ 1.0)
   - Top-P: 토큰 샘플링 확률 조절
   - Top-K: 고려할 최상위 토큰 수 설정
   - Max Token: 최대 응답 길이 설정
   - Memory Window: 대화 기억 범위 설정

4. 채팅 입력창에 질문 입력
   - 업로드된 문서 내용을 기반으로 답변 생성
   - 실시간 스트리밍 방식으로 응답 표시

5. 새로운 문서로 시작하려면 'New Chat' 버튼 클릭

## 파일 처리 기능

각 파일 형식별 최적화된 처리:

- **PDF 파일**
  - 페이지별 텍스트 추출
  - 이미지 포함 PDF 지원

- **Word 문서 (DOC/DOCX)**
  - 문단 단위 텍스트 추출
  - 서식 정보 제거 및 순수 텍스트 추출

- **파워포인트 (PPT/PPTX)**
  - 슬라이드별 텍스트 추출
  - 도형 및 텍스트 상자 내용 추출

- **엑셀/CSV**
  - 표 형식 데이터를 텍스트로 변환
  - 데이터 구조 보존

- **텍스트 기반 파일**
  - 원본 텍스트 유지
  - 인코딩 자동 감지

## Amazon Bedrock 설정

1. AWS 계정 설정
   - AWS 계정이 필요합니다
   - Amazon Bedrock 서비스 접근 권한 필요

2. IAM 권한 설정
   - Amazon Bedrock 관련 권한 필요:
     - `bedrock:InvokeModel`
     - `bedrock:InvokeModelWithResponseStream`
   - 적절한 IAM 역할 또는 사용자 생성

3. 리전 설정
   - Claude 3.5 Sonnet v2는 us-west-2 리전에서 사용 가능
   - AWS CLI 또는 환경 변수를 통한 리전 설정

4. 자격 증명 설정
```bash
# AWS CLI 설정
aws configure

# 또는 환경 변수 설정
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2
```

## 오류 처리

- 파일 형식별 적절한 에러 메시지 제공
- 파일 처리 실패 시 명확한 피드백
- 임시 파일의 안전한 처리
- API 호출 실패 시 재시도 안내

## 주의사항

1. AWS 자격 증명 설정 필요
   - AWS CLI 설정 또는 환경 변수 사용
   - 적절한 IAM 권한 필요

2. 지원되는 리전 확인
   - Claude 3.5 Sonnet v2 (us-west-2 리전)에서 사용

3. 파일 크기 제한
   - 대용량 파일의 경우 처리 시간이 길어질 수 있음
   - 매우 큰 파일은 분할 처리 권장

## 스크린샷

챗봇 실행 화면:

![Chatbot Screenshot](img/screenshot2.png)

## 라이선스

MIT License
