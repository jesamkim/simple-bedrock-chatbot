import base64
import random
from io import BytesIO
from typing import List, Tuple, Union

import streamlit as st
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_aws import ChatBedrock
from langchain_core.messages import AIMessage, HumanMessage
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.runnables import RunnableWithMessageHistory
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from PIL import Image

REGIONS_CONFIG = [
    {"region": "us-east-1", "model_id": "us.anthropic.claude-3-5-sonnet-20240620-v1:0"},
    {"region": "ap-northeast-1", "model_id": "anthropic.claude-3-5-sonnet-20240620-v1:0"},
    {"region": "us-east-2", "model_id": "us.anthropic.claude-3-5-sonnet-20240620-v1:0"},
    {"region": "ap-northeast-2", "model_id": "anthropic.claude-3-5-sonnet-20240620-v1:0"},
    {"region": "us-west-2", "model_id": "us.anthropic.claude-3-5-sonnet-20240620-v1:0"}
]

CLAUDE_PROMPT = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="history"),
        MessagesPlaceholder(variable_name="input"),
    ]
)

INIT_MESSAGE = {
    "role": "assistant",
    "content": "안녕하세요! 저는 Claude 3.5 Sonnet 입니다. 무엇을 도와드릴까요 ?",
}

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container: st.container) -> None:
        self.container = container
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

def set_page_config() -> None:
    st.set_page_config(page_title="Bedrock Chatbot", layout="wide")
    st.title("Claude 3.5 Sonnet v1")

def get_sidebar_params() -> Tuple[float, float, int, int, int, str]:
    with st.sidebar:
        st.markdown("## Inference Parameters")
        system_prompt = st.text_area(
            "System Prompt", 
            "You're a cool assistant, love to respond in Korean.",
            key=f"{st.session_state['widget_key']}_System_Prompt",
        )
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1,
            key=f"{st.session_state['widget_key']}_Temperature",
        )
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                top_p = st.slider(
                    "Top-P",
                    min_value=0.0,
                    max_value=1.0,
                    value=1.00,
                    step=0.01,
                    key=f"{st.session_state['widget_key']}_Top-P",
                )
            with col2:
                top_k = st.slider(
                    "Top-K",
                    min_value=1,
                    max_value=500,
                    value=500,
                    step=5,
                    key=f"{st.session_state['widget_key']}_Top-K",
                )
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                max_tokens = st.slider(
                    "Max Token",
                    min_value=0,
                    max_value=4096,
                    value=4096,
                    step=8,
                    key=f"{st.session_state['widget_key']}_Max_Token",
                )
            with col2:
                memory_window = st.slider(
                    "Memory Window",
                    min_value=0,
                    max_value=10,
                    value=10,
                    step=1,
                    key=f"{st.session_state['widget_key']}_Memory_Window",
                )

    return temperature, top_p, top_k, max_tokens, memory_window, system_prompt

def init_conversationchain(
    temperature: float,
    top_p: float,
    top_k: int,
    max_tokens: int,
    memory_window: int,
    system_prompt: str,
) -> RunnableWithMessageHistory:
    if 'region_index' not in st.session_state:
        st.session_state.region_index = 0
    
    current_config = REGIONS_CONFIG[st.session_state.region_index]
    
    model_kwargs = {
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_tokens": max_tokens,
    }
    
    if system_prompt != "":
        model_kwargs["system"] = system_prompt

    llm = ChatBedrock(
        model_id=current_config["model_id"],
        model_kwargs=model_kwargs,
        streaming=True,
        region_name=current_config["region"]
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    chain = prompt | llm

    def get_session_history():
        return StreamlitChatMessageHistory()

    conversation = RunnableWithMessageHistory(
        runnable=chain,
        get_session_history=get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )

    if "messages" not in st.session_state:
        st.session_state.messages = [INIT_MESSAGE]

    # 다음 리전으로 순환
    st.session_state.region_index = (st.session_state.region_index + 1) % len(REGIONS_CONFIG)

    return conversation

def generate_response(
    conversation: RunnableWithMessageHistory, 
    input: Union[str, List[dict]]
) -> str:
    with st.chat_message("assistant"):
        stream_handler = StreamHandler(st.empty())
        response = conversation.invoke(
            {"input": input}, 
            {"callbacks": [stream_handler]}
        )
        return stream_handler.text

def new_chat() -> None:
    st.session_state["messages"] = [INIT_MESSAGE]
    st.session_state["langchain_messages"] = []
    st.session_state["file_uploader_key"] = random.randint(1, 100)

def display_chat_messages(uploaded_files: List[st.runtime.uploaded_file_manager.UploadedFile]) -> None:
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

def langchain_messages_format(messages: List[Union[AIMessage, HumanMessage, dict]]) -> List[Union[AIMessage, HumanMessage]]:
    """
    Format the messages for the LangChain conversation chain.
    """
    formatted_messages = []
    for message in messages:
        if isinstance(message, (AIMessage, HumanMessage)):
            if isinstance(message.content, list):
                if "role" in message.content[0]:
                    if message.type == "ai":
                        message = AIMessage(content=message.content[0]["content"])
                    if message.type == "human":
                        message = HumanMessage(content=message.content[0]["content"])
            formatted_messages.append(message)
        elif isinstance(message, dict):
            if message["role"] == "ai" or message["role"] == "assistant":
                formatted_messages.append(AIMessage(content=message["content"]))
            elif message["role"] == "human" or message["role"] == "user":
                formatted_messages.append(HumanMessage(content=message["content"]))
    return formatted_messages


def main() -> None:
    """
    Main function to run the Streamlit app.
    """
    set_page_config()

    # Initialize session state variables
    if "widget_key" not in st.session_state:
        st.session_state["widget_key"] = str(random.randint(1, 1000000))
    
    if "messages" not in st.session_state:
        st.session_state.messages = [INIT_MESSAGE]
    
    if "langchain_messages" not in st.session_state:
        st.session_state.langchain_messages = []
        
    if "file_uploader_key" not in st.session_state:
        st.session_state.file_uploader_key = 0

    # Add a button to start a new chat
    st.sidebar.button("New Chat", on_click=new_chat, type="primary")
    
    temperature, top_p, top_k, max_tokens, memory_window, system_prompt = get_sidebar_params()
    conv_chain = init_conversationchain(temperature, top_p, top_k, max_tokens, memory_window, system_prompt)

    # Image uploader
    uploaded_files = st.file_uploader(
        "Choose an image",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key=st.session_state["file_uploader_key"],
    )

    # Display chat messages
    display_chat_messages(uploaded_files)

    # User-provided prompt
    prompt = st.chat_input()

    # Get images from previous messages
    message_images_list = [
        image_id
        for message in st.session_state.messages
        if message["role"] == "user"
        and "images" in message
        and message["images"]
        for image_id in message["images"]
    ]

    # Show image in corresponding chat box
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

    # Modify langchain_messages format if not empty
    if st.session_state.langchain_messages:
        st.session_state.langchain_messages = langchain_messages_format(
            st.session_state.langchain_messages
        )

    # main 함수의 응답 생성 부분
    if st.session_state.messages[-1]["role"] != "assistant":
        response = generate_response(
            conv_chain, [{"role": "user", "content": prompt_new}]
        )
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)


if __name__ == "__main__":
    main()
