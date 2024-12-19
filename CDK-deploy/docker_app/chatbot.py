import random
from typing import List, Tuple, Union
import os
import tempfile
import csv
import pandas as pd

import streamlit as st
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_aws import ChatBedrock, ChatBedrockConverse
from langchain_core.messages import AIMessage, HumanMessage
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import boto3

REGION = "us-west-2"
MODELS = {
    "Claude 3.5 Sonnet v2": {
        "id": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "class": ChatBedrock,
        "use_model_kwargs": True,
        "max_tokens": 4096
    },
    "Nova Pro 1.0": {
        "id": "us.amazon.nova-pro-v1:0",
        "class": None,  # 직접 boto3 client 사용
        "use_model_kwargs": False,
        "max_tokens": 5000
    }
}

SUPPORTED_FORMATS = ['pdf', 'doc', 'docx', 'md', 'ppt', 'pptx', 'txt', 'html', 'csv', 'xls', 'xlsx']

CLAUDE_PROMPT = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="history"),
    MessagesPlaceholder(variable_name="input"),
])

def get_init_message(model_name: str) -> dict:
    return {
        "role": "assistant",
        "content": f"안녕하세요! 저는 AI 도우미 입니다. 문서를 업로드하시면 문서 내용을 기반으로 답변해드리겠습니다. 무엇을 도와드릴까요?",
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
    st.title("Bedrock Chatbot with Document Q&A")

def get_sidebar_params() -> Tuple[float, float, int, int, int, str]:
    with st.sidebar:
        st.markdown("## Model Selection")
        model_name = st.radio(
            "Choose a model",
            options=list(MODELS.keys()),
            index=0,
            key=f"{st.session_state['widget_key']}_Model"
        )
        
        st.markdown("## Document Upload")
        uploaded_file = st.file_uploader(
            "Upload a document",
            type=SUPPORTED_FORMATS,
            help="지원되는 파일 형식: pdf, doc, docx, md, ppt, pptx, txt, html, csv, xls, xlsx"
        )

        st.markdown("## Inference Parameters")
        system_prompt = st.text_area(
            "System Prompt",
            "You're a helpful assistant who loves to respond in Korean. You'll answer questions based on the uploaded documents. When you're not certain about something, don't guess or make up information. Instead, honestly admit that you don't know.",
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
                # 선택된 모델에 따라 max_tokens 슬라이더 범위 조정
                model_max_tokens = MODELS[model_name]["max_tokens"]
                max_tokens = st.slider(
                    "Max Token",
                    min_value=0,
                    max_value=model_max_tokens,
                    value=model_max_tokens,
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

    return temperature, top_p, top_k, max_tokens, memory_window, system_prompt, uploaded_file, model_name

def process_text_based_file(file_path: str) -> str:
    """텍스트 기반 파일(txt, md, html) 처리"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def process_excel_file(file_path: str) -> str:
    """엑셀 파일(xls, xlsx) 처리"""
    df = pd.read_excel(file_path)
    return df.to_string()

def process_csv_file(file_path: str) -> str:
    """CSV 파일 처리"""
    df = pd.read_csv(file_path)
    return df.to_string()

def process_powerpoint_file(file_path: str) -> str:
    """파워포인트 파일(ppt, pptx) 처리"""
    from pptx import Presentation
    
    text = []
    try:
        prs = Presentation(file_path)
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text.append(shape.text)
    except Exception as e:
        st.warning(f"일부 슬라이드를 처리하는 중 오류가 발생했습니다: {str(e)}")
    
    return "\n\n".join(text)

def process_uploaded_file(file_path: str) -> str:
    """문서 파일을 처리하여 텍스트로 변환"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_ext == '.pdf':
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        
        elif file_ext in ['.doc', '.docx']:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        
        elif file_ext in ['.txt', '.md', '.html']:
            return process_text_based_file(file_path)
        
        elif file_ext in ['.csv']:
            return process_csv_file(file_path)
        
        elif file_ext in ['.xls', '.xlsx']:
            return process_excel_file(file_path)
        
        elif file_ext in ['.ppt', '.pptx']:
            return process_powerpoint_file(file_path)
        
        else:
            raise ValueError(f"지원하지 않는 파일 형식입니다: {file_ext}")
            
    except Exception as e:
        raise Exception(f"파일 처리 중 오류가 발생했습니다 ({file_ext}): {str(e)}")

def init_conversationchain(
    temperature: float,
    top_p: float,
    top_k: int,
    max_tokens: int,
    memory_window: int,
    system_prompt: str,
    model_name: str,
    context: str = None
) -> Union[RunnableWithMessageHistory, boto3.client]:

    model_info = MODELS[model_name]
    model_id = model_info["id"]
    use_model_kwargs = model_info["use_model_kwargs"]

    # 문서 컨텍스트가 있는 경우 시스템 프롬프트에 추가
    if context:
        full_system_prompt = f"{system_prompt}\n\n참고할 문서 내용:\n\n{context}"
    else:
        full_system_prompt = system_prompt

    if use_model_kwargs:  # ChatBedrock (Claude 3.5 Sonnet)
        model_kwargs = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_tokens": max_tokens,
            "system": full_system_prompt
        }
        llm = ChatBedrock(
            model_id=model_id,
            model_kwargs=model_kwargs,
            streaming=True,
            region_name=REGION
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", full_system_prompt),
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

        return conversation
    else:  # Nova Pro - 직접 boto3 client 사용
        return boto3.client("bedrock-runtime", region_name=REGION)

def generate_response(
    conversation: Union[RunnableWithMessageHistory, boto3.client],
    input: Union[str, List[dict]]
) -> str:
    with st.chat_message("assistant"):
        stream_handler = StreamHandler(st.empty())
        try:
            if isinstance(conversation, RunnableWithMessageHistory):  # Claude 3.5 Sonnet
                response = conversation.invoke(
                    {"input": input},
                    {"callbacks": [stream_handler]}
                )
                if isinstance(response, str):
                    stream_handler.container.markdown(response)
                    return response
                return stream_handler.text
            else:  # Nova Pro
                # 문서 컨텍스트가 있는 경우 첫 번째 user 메시지에 포함
                system_message = st.session_state[f"{st.session_state['widget_key']}_System_Prompt"]
                if "document_context" in st.session_state:
                    system_message = f"{system_message}\n\n참고할 문서 내용:\n\n{st.session_state['document_context']}"
                
                messages = [
                    {"role": "user", "content": [{"text": system_message}]},
                    {"role": "assistant", "content": [{"text": "알겠습니다. 문서 내용을 참고하여 답변하겠습니다."}]},
                    {"role": "user", "content": [{"text": input[0]["content"][0]["text"]}]}
                ]
                
                response = conversation.converse_stream(
                    modelId=MODELS["Nova Pro 1.0"]["id"],
                    messages=messages,
                    inferenceConfig={
                        "temperature": float(st.session_state[f"{st.session_state['widget_key']}_Temperature"]),
                        "maxTokens": int(st.session_state[f"{st.session_state['widget_key']}_Max_Token"]),
                    }
                )

                full_response = ""
                for event in response['stream']:
                    if 'contentBlockDelta' in event:
                        delta_text = event['contentBlockDelta']['delta']['text']
                        full_response += delta_text
                        stream_handler.container.markdown(full_response)
                
                return full_response

        except Exception as e:
            if "ThrottlingException" in str(e):
                error_message = "요청을 처리하지 못했습니다. 잠시 후 다시 말씀해 주세요. 🙏"
            else:
                error_message = f"죄송합니다. 오류가 발생했습니다: {str(e)}"
            stream_handler.container.markdown(error_message)
            return error_message

def new_chat() -> None:
    st.session_state["messages"] = [get_init_message(st.session_state[f"{st.session_state['widget_key']}_Model"])]
    st.session_state["langchain_messages"] = []
    if "document_context" in st.session_state:
        del st.session_state["document_context"]

def display_chat_messages() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
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

def handle_file_upload(uploaded_file) -> str:
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        try:
            # 문서 처리하여 텍스트 추출
            document_text = process_uploaded_file(tmp_file_path)
            st.session_state["document_context"] = document_text
            os.unlink(tmp_file_path)
            return document_text
        except Exception as e:
            os.unlink(tmp_file_path)
            st.error(f"문서 처리 중 오류가 발생했습니다: {str(e)}")
            return None
    return None

def main() -> None:
    set_page_config()

    if "widget_key" not in st.session_state:
        st.session_state["widget_key"] = str(random.randint(1, 1000000))
    if "messages" not in st.session_state:
        st.session_state.messages = [get_init_message("Claude 3.5 Sonnet v2")]
    if "langchain_messages" not in st.session_state:
        st.session_state.langchain_messages = []

    st.sidebar.button("New Chat", on_click=new_chat, type="primary")

    temperature, top_p, top_k, max_tokens, memory_window, system_prompt, uploaded_file, model_name = get_sidebar_params()

    document_context = None
    if uploaded_file:
        document_context = handle_file_upload(uploaded_file)
        if document_context:
            st.sidebar.success(f"문서가 성공적으로 업로드되었습니다: {uploaded_file.name}")
    elif "document_context" in st.session_state:
        document_context = st.session_state["document_context"]

    conv_chain = init_conversationchain(
        temperature, top_p, top_k, max_tokens, memory_window, system_prompt, model_name, document_context
    )

    display_chat_messages()

    prompt = st.chat_input()

    if prompt:
        prompt_text = {"type": "text", "text": prompt}
        prompt_new = [prompt_text]
        st.session_state.messages.append({"role": "user", "content": prompt_new})
        with st.chat_message("user"):
            st.markdown(prompt)

    if st.session_state.langchain_messages:
        st.session_state.langchain_messages = langchain_messages_format(
            st.session_state.langchain_messages
        )

    if st.session_state.messages[-1]["role"] != "assistant":
        response = generate_response(
            conv_chain, [{"role": "user", "content": prompt_new}]
        )

        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)

if __name__ == "__main__":
    main()
