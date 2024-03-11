import base64
from io import BytesIO
from typing import List, Union

from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.chat_models import BedrockChat
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts.chat import ChatPromptTemplate, MessagesPlaceholder
from PIL import Image

# 사용할 Claude 모델 ID 지정 (Anthropic Claude v3 sonnet)
MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

# 프롬프트 템플릿 정의
CLAUDE_PROMPT = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="history"),
        MessagesPlaceholder(variable_name="input"),
    ]
)

# 초기 메시지 설정
INIT_MESSAGE = {
    "role": "assistant",
    "content": "안녕하세요! 저는 Bedrock의 Claude v3 입니다. 무엇을 도와드릴까요?",
}

# 시스템 프롬프트 설정
SYSTEM_PROMPT = "You're a cool assistant, love to response with emoji."


def init_conversationchain(
    temperature: float,
    top_p: float,
    top_k: int,
    max_tokens: int,
    memory_window: int,
) -> ConversationChain:
    """
    주어진 파라미터로 ConversationChain을 초기화합니다.
    """
    model_kwargs = {
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_tokens": max_tokens,
        "system": SYSTEM_PROMPT,
    }

    llm = BedrockChat(model_id=MODEL_ID, model_kwargs=model_kwargs, streaming=True)

    conversation = ConversationChain(
        llm=llm,
        verbose=True,
        memory=ConversationBufferWindowMemory(
            k=memory_window,
            ai_prefix="Assistant",
            chat_memory=StreamlitChatMessageHistory(),
            return_messages=True,
        ),
        prompt=CLAUDE_PROMPT,
    )

    return conversation


def generate_response(
    conversation: ConversationChain, input: Union[str, List[dict]]
) -> str:
    """
    conversation chain에서 주어진 입력으로 응답을 생성합니다.
    """
    return conversation.predict(input=input)


def langchain_messages_format(messages: List[Union[AIMessage, HumanMessage]]) -> List[Union[AIMessage, HumanMessage]]:
    """
    LangChain conversation chain 에 맞게 메시지 형식을 변환합니다.
    """
    for i, message in enumerate(messages):
        if isinstance(message.content, list):
            if "role" in message.content[0]:
                if message.type == "ai":
                    message = AIMessage(message.content[0]["content"])
                if message.type == "human":
                    message = HumanMessage(message.content[0]["content"])
                messages[i] = message
    return messages