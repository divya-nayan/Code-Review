"""
Streamlit-based Chatbot Web Application
"""
import streamlit as st
from src.chatbot import ChatBot
from config.settings import GROQ_API_KEY, APP_TITLE, MODEL_NAME


def init_session_state():
    """Initialize session state variables"""
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = ChatBot(api_key=GROQ_API_KEY, model=MODEL_NAME)
    if "messages" not in st.session_state:
        st.session_state.messages = []


def main():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🤖",
        layout="centered"
    )

    st.title("🤖 " + APP_TITLE)
    st.caption("Powered by Groq LLaMA 3.2")

    # Initialize
    init_session_state()

    # Sidebar
    with st.sidebar:
        st.header("Settings")

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="Higher values make output more random"
        )

        max_tokens = st.slider(
            "Max Tokens",
            min_value=256,
            max_value=2048,
            value=1024,
            step=128
        )

        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.session_state.chatbot.reset()
            st.rerun()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.chat(
                    prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                st.markdown(response)

        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
