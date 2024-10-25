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

### Prerequisites:

* python 3.9
* docker
* use a Chrome browser for development
* [중요] AWS 계정에서 `anthropic.claude-3-5-sonnet-20240620-v1:0` (Claude 3.5 Sonnet v1) 모델이 <b>us-east-1, us-east-2, us-west-2, ap-northeast-1, ap-northeast-2 리전</b>에 모두 Access Granted 되어 있어야 합니다.

## 배포 방법 :


### 1. git clone

```
git clone https://github.com/jesamkim/simple-bedrock-chatbot.git

cd simple-bedrock-chatbot/CDK-deploy

```
(optional) Edit `docker_app/config_file.py`, choose a `STACK_NAME` and a `CUSTOM_HEADER_VALUE`.


### 2. 디펜던시 설치
 
```
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

```

### 3. CDK 템플릿 배포 
- 배포는 서울 리전에 해도 됩니다.
- Bedrock Claude 3 모델 access 권한 설정만 us-west-2에 미리 해두시면 됩니다.

```
cdk bootstrap
cdk deploy
```

배포에는 약 10분이 소요됩니다.

CloudFront 배포 URL을 확인할 수 있습니다.

### 4. 브라우저에서 CloudFront distribution URL에 연결합니다.
```
# Output 예시
Outputs:
cdk-chatbot-claude3.CloudFrontDistributionURL = xxx2cj9ksuhwvn.cloudfront.net
```


## 실행 화면
![screenshot1-1](/CDK-deploy/img/screenshot1-1.png)


<br>

## (Optional) 배포 전 개발 환경에서 테스트

cdk 템플릿을 배포한 후에는 VSCode와 같은 개발 환경에서 Streamlit 앱을 먼저 테스트할 수 있습니다.
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

4. 이제 Streamlit 앱을 수정하여 자신만의 데모를 만들어 보세요!

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
