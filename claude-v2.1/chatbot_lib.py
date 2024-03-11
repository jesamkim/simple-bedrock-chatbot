import os
from langchain.memory import ConversationBufferMemory
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationChain

def get_llm():
        
    model_kwargs = { #Anthropic Cloude v2
        "prompt": "\n\nHuman:<prompt>\n\nAssistant:",
        "max_tokens_to_sample": 1024, 
        "temperature": 0, 
        "top_p": 0.5, 
        "stop_sequences": ["\n\nHuman:"]
    }
    
    llm = Bedrock(
        credentials_profile_name=os.environ.get("BWB_PROFILE_NAME"), #AWS 자격 증명에 사용할 프로필 이름을 설정합니다(기본값이 아닌 경우)
        region_name=os.environ.get("BWB_REGION_NAME"), #리전 이름을 설정합니다(기본값이 아닌 경우)
        endpoint_url=os.environ.get("BWB_ENDPOINT_URL"), #endpoint URL을 설정합니다 (필요한 경우)
        model_id="anthropic.claude-v2:1", #파운데이션 모델 설정
        model_kwargs=model_kwargs) #모델 속성 설정
    
    return llm


def get_memory(): #�� 채팅 세션에 대한 메모리 생성
    
    #ConversationBufferMemory에서 human_prefix와 ai_prefix를 지정 합니다. Claude-v2의 프롬프트 형식을 맞추기 위함 입니다.
    #이어서 ConversationChain을 통해 진행되는 대화의 "큰 그림"을 유지할 수 있습니다.
    llm = get_llm()
    
    chat_memory = ConversationBufferMemory(human_prefix='Human', ai_prefix='Assistant')
    conversation = ConversationChain(llm=llm, verbose=False, memory=chat_memory) #이전 메시지를 유지합니다.
    
    return chat_memory


def get_chat_response(input_text, memory): #챗 클라이언트 함수
    
    llm = get_llm()
    
    conversation_with_summary = ConversationChain( #챗 클라이언트 생성
        llm = llm, #Bedrock LLM 사용
        memory = memory, #get_memory()의 return 값을 메모리로 활용
        verbose = True #실행 중 체인의 일부 상태를 출력합니다.
    )
    
    chat_response = conversation_with_summary.predict(input=input_text) #사용자 메시지와 요약을 모델에 전달합니다.
    
    return chat_response
