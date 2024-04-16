# 필요한 라이브러리 가져오기
import base64
import random
from io import BytesIO
from typing import List, Tuple, Union

import streamlit as st
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.chat_models import BedrockChat
from langchain_core.messages import AIMessage, HumanMessage
from langchain.callbacks.base import BaseCallbackHandler
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
    "content": "안녕하세요! 저는 Claude 3 챗봇 입니다. 무엇을 도와드릴까요?",
}

# 시스템 프롬프트 설정
SYSTEM_PROMPT = "You're a cool assistant. By default, it answers in Korean. If you don't know the answer, just say that you don't know, don't try to make up an answer."

class StreamHandler(BaseCallbackHandler):
    """
    Callback 핸들러를 사용하여 생성된 텍스트를 Streamlit에 스트리밍합니다.
    """

    def __init__(self, container: st.container) -> None:
        self.container = container
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """
        새로운 토큰을 텍스트에 추가하고 Streamlit 컨테이너를 업데이트합니다.
        """
        self.text += token
        self.container.markdown(self.text)


def set_page_config() -> None:
    """
    Streamlit 페이지 설정을 초기화합니다.
    """
    st.set_page_config(page_title="🤖 Chat with Bedrock", layout="wide")
    st.title("🤖 Chatbot demo w/ Amazon Bedrock")
    st.subheader("- model : Claude v3 sonnet")


def get_sidebar_params() -> Tuple[float, float, int, int, int, bool]:
    """
    왼쪽 사이드바에 Claude v3 파라미터와 Google Search 옵션을 표시합니다.
    """
    with st.sidebar:
        st.markdown("## Inference Parameters")
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1,
            key=f"{st.session_state['widget_key']}_Temperature",
        )
        top_p = st.slider(
            "Top-P",
            min_value=0.0,
            max_value=1.0,
            value=1.00,
            step=0.01,
            key=f"{st.session_state['widget_key']}_Top-P",
        )
        top_k = st.slider(
            "Top-K",
            min_value=1,
            max_value=500,
            value=500,
            step=5,
            key=f"{st.session_state['widget_key']}_Top-K",
        )
        max_tokens = st.slider(
            "Max Token",
            min_value=0,
            max_value=4096,
            value=4096,
            step=8,
            key=f"{st.session_state['widget_key']}_Max Token",
        )
        memory_window = st.slider(
            "Memory Window",
            min_value=0,
            max_value=10,
            value=10,
            step=1,
            key=f"{st.session_state['widget_key']}_Memory Window",
        )
        google_search_enabled = st.checkbox("Google Search", value=False)

    return temperature, top_p, top_k, max_tokens, memory_window, google_search_enabled


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

    llm = BedrockChat(
        region_name="us-west-2", ## Bedrock Claude v3 리전
        model_id=MODEL_ID, 
        model_kwargs=model_kwargs, 
        streaming=True)

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

    # LLM에서 생성된 응답 저장
    if "messages" not in st.session_state:
        st.session_state.messages = [INIT_MESSAGE]

    return conversation


def generate_response(
    conversation: ConversationChain, input: Union[str, List[dict]]
) -> str:
    """
    conversation chain에서 주어진 입력으로 응답을 생성합니다.
    """
    return conversation.invoke(
        {"input": input}, {"callbacks": [StreamHandler(st.empty())]}
    )


def new_chat() -> None:
    """
    채팅 세션을 재설정하고 새로운 conversation chain을 초기화합니다.
    """
    st.session_state["messages"] = [INIT_MESSAGE]
    st.session_state["langchain_messages"] = []
    st.session_state["file_uploader_key"] = random.randint(1, 100)


def display_chat_messages(uploaded_files: List[st.runtime.uploaded_file_manager.UploadedFile]) -> None:
    """
    채팅 메시지와 업로드된 이미지를 Streamlit 앱에 표시합니다.
    """
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if uploaded_files:
                if "images" in message and message["images"]:
                    num_cols = 10
                    cols = st.columns(num_cols)
                    i = 0

                    for image_id in message["images"]:
                        for uploaded_file in uploaded_files:
                            if image_id == uploaded_file.file_id:
                                img = Image.open(uploaded_file)

                                with cols[i]:
                                    st.image(img, caption="", width=75)
                                    i += 1

                                if i >= num_cols:
                                    i = 0

            if message["role"] == "user":
                if isinstance(message["content"], str):
                    st.markdown(message["content"])
                elif isinstance(message["content"], dict):
                    st.markdown(message["content"]["input"][0]["content"][0]["text"])
                else:
                    st.markdown(message["content"][0]["text"])

            if message["role"] == "assistant":
                if isinstance(message["content"], str):
                    st.markdown(message["content"])
                elif "response" in message["content"]:
                    st.markdown(message["content"]["response"])


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



def main() -> None:
    """
    Streamlit 앱의 메인 실행 함수입니다.
    """
    set_page_config()

    # 고유한 위젯 키를 한 번만 생성합니다.
    if "widget_key" not in st.session_state:
        st.session_state["widget_key"] = str(random.randint(1, 1000000))

    temperature, top_p, top_k, max_tokens, memory_window, google_search_enabled = get_sidebar_params()
    conv_chain = init_conversationchain(temperature, top_p, top_k, max_tokens, memory_window)

    # 새로운 채팅을 시작할 수 있는 버튼 추가
    st.sidebar.button("New Chat", on_click=new_chat, type="primary")

    # 이미지 업로더
    if "file_uploader_key" not in st.session_state:
        st.session_state["file_uploader_key"] = 0

    uploaded_files = st.file_uploader(
        "Choose an image",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key=st.session_state["file_uploader_key"],
    )

    # 채팅 메시지 표시
    display_chat_messages(uploaded_files)

    # 사용자 입력 프롬프트
    prompt = st.chat_input()

    # 이전 메시지에서 이미지 ID 가져오기
    message_images_list = [
        image_id
        for message in st.session_state.messages
        if message["role"] == "user"
        and "images" in message
        and message["images"]
        for image_id in message["images"]
    ]

    # 해당 채팅 박스에 이미지 표시
    uploaded_file_ids = []
    if uploaded_files and len(message_images_list) < len(uploaded_files):
        with st.chat_message("user"):
            num_cols = 10
            cols = st.columns(num_cols)
            i = 0
            content_images = []

            for uploaded_file in uploaded_files:
                if uploaded_file.file_id not in message_images_list:
                    uploaded_file_ids.append(uploaded_file.file_id)
                    img = Image.open(uploaded_file)
                    with BytesIO() as output_buffer:
                        img.save(output_buffer, format=img.format)
                        content_image = base64.b64encode(output_buffer.getvalue()).decode(
                            "utf8"
                        )
                    content_images.append(content_image)
                    with cols[i]:
                        st.image(img, caption="", width=75)
                        i += 1
                    if i >= num_cols:
                        i = 0

            if prompt:
                prompt_text = {"type": "text", "text": prompt}
                prompt_new = [prompt_text]
                for content_image in content_images:
                    prompt_image = {
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/jpeg", "data": content_image},
                    }
                    prompt_new.append(prompt_image)
                st.session_state.messages.append(
                    {"role": "user", "content": prompt_new, "images": uploaded_file_ids}
                )
                st.markdown(prompt)

    elif prompt:
        prompt_text = {"type": "text", "text": prompt}
        prompt_new = [prompt_text]
        st.session_state.messages.append({"role": "user", "content": prompt_new})
        with st.chat_message("user"):
            st.markdown(prompt)

    # langchain_messages 형식 변환
    st.session_state["langchain_messages"] = langchain_messages_format(
        st.session_state["langchain_messages"]
    )

    # 마지막 메시지가 어시스턴트가 아닌 경우 새로운 응답 생성
    if st.session_state.messages[-1]["role"] != "assistant":
        if google_search_enabled:
            # Google 검색 수행
            from search import google_search
            search_results = google_search(prompt)

            # Claude에게 전달할 context 정보 생성
            search_context = "\n".join(search_results)
            prompt_with_context = f"{prompt}\n\nContext:\n{search_context}"

            # Claude에게 context 정보와 함께 prompt 전달
            with st.chat_message("assistant"):
                response = generate_response(
                    conv_chain, [{"role": "user", "content": prompt_with_context}]
                )
        else:
            # 기존 동작 유지
            with st.chat_message("assistant"):
                response = generate_response(
                    conv_chain, [{"role": "user", "content": prompt_new}]
                )

        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)




if __name__ == "__main__":
    main()
