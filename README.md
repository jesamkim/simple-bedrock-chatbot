# Amazon Bedrock의 Claude 3.5 Sonnet을 활용한 간단한 Chatbot
Amazon Bedrock (Claude 3.5 Sonnet) &amp; LangChain &amp; Streamlit 으로 구성하는 간단 챗봇 어플리케이션

## 환경
- Amazon Bedrock의 Claude 에 대한 model access는 설정 되어 있어야 합니다. (Bedrock 모델 권한은 us-west-2 로 설정되어 있습니다)
- 코드 상에서 따로 자격증명을 다루지 않습니다. (aws configure 사전 설정 필요)


## 챗봇 실행을 위한 패키지 설치
```
pip install -r ./claude-3-5/requirements.txt -U
```


## streamlit 앱 실행
- AWS Cloud9 환경에서는 터미널에서 아래 실행 후,  상단 메뉴의 Preview > Preview Running Application 에서 streamlit UI를 빠르게 띄울 수 있습니다.
```
streamlit run ./claude-3-5/app.py --server.port 8080
```

![screenshot1-1](./img/screenshot1-1.png)


#### Reference Contents
> [Bedrock-ChatBot-with-LangChain-and-Streamlit](https://github.com/davidshtian/Bedrock-ChatBot-with-LangChain-and-Streamlit) <br>
> [aws-samples/deploy-streamlit-app](https://github.com/aws-samples/deploy-streamlit-app)
