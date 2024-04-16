# CDK로 Chatbot 배포하기

이 앱은 웹 인터페이스를 통해 Amazon Bedrock Claude 3 챗봇I데모를 쉽게 생성하고 배포하는 시작점으로 사용할 수 있습니다. 
파이썬으로만 작성되었으며, AWS에 배포하기 위한 cdk 템플릿이 포함되어 있습니다.

기본 Streamlit 앱을 배포하며 다음 구성 요소가 포함되어 있습니다:

* ALB 및 CloudFront 뒤에 있는 ECS/Fargate의 Streamlit 앱


## 아키텍처

![Architecture diagram](/CDK-deploy/img/archi_streamlit_cdk.png)

## Usage

docker_app 폴더에서 Streamlit 앱을 찾을 수 있습니다. 로컬에서 실행하거나 도커를 사용하여 실행할 수 있습니다.

메인 폴더에는 ECS/ALB에 앱을 배포하기 위한 cdk 템플릿이 있습니다.

Prerequisites:

* python 3.8
* docker
* use a Chrome browser for development
* 당신의 AWS 계정에서 `anthropic.claude-v3` 모델이 us-west-2 리전에 활성화 되어 있어야 합니다.
* 이 데모를 생성하는 데 사용된 환경은 Amazon Linux 2023이 설치된 AWS Cloud9 m5.large 인스턴스이지만 다른 구성에서도 작동합니다.

To deploy:


1. git clone

```
git clone https://github.com/jesamkim/simple-bedrock-chatbot.git

cd simple-bedrock-chatbot/CDK-deploy

```
(optional) Edit `docker_app/config_file.py`, choose a `STACK_NAME` and a `CUSTOM_HEADER_VALUE`.


2. 디펜던시 설치
 
```
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

3. [필수] Google 검색 기능을 사용하기 위해 각자 미리 발급받은 `GOOGLE_ENGINE_ID`와 `GOOGLE_API_KEY`가 필요 합니다.
`GOOGLE_ENGINE_ID`와 `GOOGLE_API_KEY` 값을 simple-bedrock-chatbot/CDK-deploy/docker_app/search.py 를 수정하여 넣습니다.
```
# Google API 키와 검색 엔진 ID를 환경 변수에서 가져옵니다.
API_KEY = "YOUR_GOOGLE_API_KEY"
SEARCH_ENGINE_ID = "YOUR_GOOGLE_ENGINE_ID"
```

4. CDK 템플릿 배포 (배포는 서울 리전에 할 수 있습니다)

```
cdk bootstrap
cdk deploy
```

배포에는 5~10분이 소요됩니다.

CloudFront 배포 URL을 확인할 수 있습니다.

5. 브라우저에서 CloudFront distribution URL에 연결합니다.
```
# Output 예시
Outputs:
cdk-chatbot-claude3.CloudFrontDistributionURL = xxx2cj9ksuhwvn.cloudfront.net
```


## 실행 화면
![screenshot1](/CDK-deploy/img/screenshot1.png)


<br>

## (Optional) Cloud9에서 테스트

cdk 템플릿을 배포한 후에는 Cloud9에서 바로 Streamlit 앱을 테스트할 수 있습니다.
도커를 사용할 수 있지만 적절한 권한이 있는 역할을 설정하거나 필요한 Python 디펜던시를 설치한 후 터미널에서 직접 Streamlit 앱을 실행해야 합니다.

Streamlit 앱을 직접 실행하기:

1. cdk 템플릿 배포를 위해 virtual env를 활성화 한 경우, deactivate 하세요:

```
deactivate
```

2. streamlit-docker 디렉토리로 이동하고, 새 virtual env를 다시 생성하고 디펜던시를 설치합니다:

```
cd docker_app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Streamlit 서버 실행하기

```
streamlit run app.py --server.port 8080
```

4. Cloud9에 내장된 브라우저는 세션 쿠키를 보관하지 않아 인증 메커니즘이 제대로 작동하지 않으므로 Cloud9에서 실행 중인 애플리케이션 미리보기/미리 보기 버튼을 클릭하고 새 창에서 브라우저 팝업 버튼을 클릭합니다.
새 창에 앱이 표시되지 않으면 사이트 간 추적 쿠키를 허용하도록 브라우저를 구성해야 할 수 있습니다.

5. 이제 Streamlit 앱을 수정하여 자신만의 데모를 만들어 보세요!

## 몇 가지 제한 사항

* CloudFront와 ALB 간의 연결은 SSL 암호화가 아닌 HTTP로 이루어집니다.
즉, CloudFront와 ALB 간의 트래픽은 암호화되지 않습니다.
자체 도메인 이름과 SSL/TLS 인증서를 ALB에 가져와서 HTTPS를 구성하는 것을 **강력히 권장**합니다.
* 제공된 코드는 데모 및 개발 시작용이며 프로덕션용이 아닙니다.
Python 앱은 Streamlit 및 Streamlit-cognito-auth와 같은 타사 라이브러리를 사용합니다.
개발자는 모든 타사 디펜던시를 적절히 조사, 유지 관리 및 테스트할 책임이 있습니다.
특히 인증 및 권한 부여 메커니즘을 철저히 평가해야 합니다.
일반적으로 이 데모 코드를 프로덕션 애플리케이션이나 민감한 데이터에 통합하기 전에 보안 검토 및 테스트를 수행해야 합니다.
* AWS는 이 데모에서 구현되지 않았지만 이 애플리케이션의 보안을 향상시킬 수 있는 다양한 서비스를 제공합니다.
네트워크 ACL 및 AWS WAF와 같은 네트워크 보안 서비스는 리소스에 대한 액세스를 제어할 수 있습니다.
또한 DDoS 보호를 위해 AWS Shield를, 위협 탐지를 위해 Amazon GuardDuty를 사용할 수 있습니다.
Amazon Inspector는 보안 평가를 수행합니다.
보안을 강화할 수 있는 AWS 서비스 및 모범 사례는 더 많이 있습니다.
추가 권장 사항은 AWS 공유 책임 모델 및 보안 모범 사례 지침을 참조하세요.
개발자는 특정 보안 요구 사항을 충족하도록 이러한 서비스를 올바르게 구현하고 구성할 책임이 있습니다.

## Acknowledgments

이 코드는 다음 코드에서 영감을 얻었습니다:

* https://github.com/tzaffi/streamlit-cdk-fargate.git
* https://github.com/aws-samples/build-scale-generative-ai-applications-with-amazon-bedrock-workshop/


## License

This application is licensed under the MIT-0 License. See the LICENSE file.