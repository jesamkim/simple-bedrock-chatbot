import streamlit as st #모든 streamlit 명령은 "st" 별칭을 통해 사용할 수 있습니다
import chatbot_lib as glib #로컬 라이브러리 스크립트에 대한 참조

st.set_page_config(page_title="Chatbot") #HTML 제목
st.title("Claude v2.1 - Chatbot DEMO") #페이지 제목
st.caption("이 chatbot은 Anthropic Claude v2.1 버전을 사용합니다. Claude v2.1에서 지원하는 다양한 프롬프트 기법을 실험해보세요.")
st.markdown("[Claude 2.1 Guide](https://docs.anthropic.com/claude/docs/claude-2p1-guide) 의 프롬프트 예시를 참조하세요.")

if 'memory' not in st.session_state: #메모리가 아직 생성되지 않았는지 확인합니다.
    st.session_state.memory = glib.get_memory() #메모리 초기화


if 'chat_history' not in st.session_state: #채팅 내역이 아직 생성되지 않았는지 확인합니다.
    st.session_state.chat_history = [] #채팅 내역 초기화

# 'New Conversation' 버튼을 사이드바에 추가합니다.
if st.sidebar.button('New Conversation'):
    st.session_state.chat_history = [] # 새 대화 시작시 채팅 기록 초기화


#채팅 기록 다시 렌더링(Streamlit은 이 스크립트를 다시 실행하므로 이전 채팅 메시지를 보존하려면 이 기능이 필요합니다.)
for message in st.session_state.chat_history: #채팅 기록 루프
    with st.chat_message(message["role"]): #지정된 역할에 대한 챗 라인을 렌더링하며, with 블록의 모든 내용을 포함합니다.
        st.markdown(message["text"]) #챗 컨텐츠 출력


input_text = st.chat_input("Chat with your bot here") #채팅 입력 상자 표시

if input_text: #사용자가 채팅 메시지를 제출한 후 이 if 블록의 코드를 실행합니다.
    
    with st.chat_message("user"): #사용자 채팅 메시지 표시
        st.markdown(input_text) #사용자의 최신 메시지를 렌더링합니다.
 

    st.session_state.chat_history.append({"role":"user", "text":input_text}) #사용자의 최신 메시지를 채팅 기록에 추가합니다.
    
    chat_response = glib.get_chat_response(input_text=input_text, memory=st.session_state.memory) #지원 라이브러리를 ���해 모델을 호출합니다.
    
    with st.chat_message("assistant"): #봇 채팅 메시지 표시
        st.markdown(chat_response) #봇의 최신 응답 표시
    
    st.session_state.chat_history.append({"role":"assistant", "text":chat_response}) #봇의 최신 메시지를 채팅 기록에 추가합니다.