"""
Streamlit-based Chatbot Web Application
"""
import streamlit as st
import logging

from src.chatbot import ChatBot
from src.exceptions import ChatBotError, InvalidAPIKeyError
from src.constants import (
    MIN_TEMPERATURE, MAX_TEMPERATURE, DEFAULT_TEMPERATURE,
    MIN_TOKENS, MAX_TOKENS, DEFAULT_MAX_TOKENS,
    APP_TITLE, APP_ICON, DEFAULT_PLACEHOLDER
)
from config.settings import GROQ_API_KEY, MODEL_NAME

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_session_state():
    """
    Initialize session state variables

    Raises:
        InvalidAPIKeyError: If API key is not configured
    """
    if "chatbot" not in st.session_state:
        try:
            st.session_state.chatbot = ChatBot(api_key=GROQ_API_KEY, model=MODEL_NAME)
            logger.info("Chatbot initialized successfully")
        except InvalidAPIKeyError as e:
            st.error(f"❌ Configuration Error: {e}")
            st.info("Please set your GROQ_API_KEY in the .env file")
            st.stop()
        except Exception as e:
            st.error(f"❌ Failed to initialize chatbot: {e}")
            st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "error" not in st.session_state:
        st.session_state.error = None


def main():
    """Main application entry point"""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="centered"
    )

    st.title(f"{APP_ICON} {APP_TITLE}")

    # Initialize
    init_session_state()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        temperature = st.slider(
            "Temperature",
            min_value=float(MIN_TEMPERATURE),
            max_value=float(MAX_TEMPERATURE),
            value=float(DEFAULT_TEMPERATURE),
            step=0.1,
            help="Higher values make output more random and creative"
        )

        max_tokens = st.slider(
            "Max Tokens",
            min_value=MIN_TOKENS,
            max_value=MAX_TOKENS,
            value=DEFAULT_MAX_TOKENS,
            step=128,
            help="Maximum length of the response"
        )

        st.divider()

        # Stats
        if st.session_state.chatbot:
            msg_count = st.session_state.chatbot.get_message_count()
            st.metric("Messages", msg_count)

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chatbot.reset()
            st.session_state.error = None
            logger.info("Chat cleared by user")
            st.rerun()

        st.divider()
        st.caption(f"Model: {MODEL_NAME}")

    # Display error if any
    if st.session_state.error:
        st.error(st.session_state.error)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input(DEFAULT_PLACEHOLDER):
        # Clear previous errors
        st.session_state.error = None

        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            try:
                with st.spinner("Thinking..."):
                    response = st.session_state.chatbot.chat(
                        prompt,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    st.markdown(response)

                # Add assistant message
                st.session_state.messages.append({"role": "assistant", "content": response})
                logger.info(f"Successfully processed message (temp={temperature}, tokens={max_tokens})")

            except ChatBotError as e:
                error_msg = f"❌ Chat Error: {e}"
                st.error(error_msg)
                st.session_state.error = error_msg
                # Remove the user message since we failed
                st.session_state.messages.pop()
                logger.error(f"Chat error: {e}")

            except Exception as e:
                error_msg = f"❌ Unexpected Error: {e}"
                st.error(error_msg)
                st.session_state.error = error_msg
                # Remove the user message since we failed
                st.session_state.messages.pop()
                logger.exception("Unexpected error in chat")


if __name__ == "__main__":
    main()
