"""
Chatbot implementation
"""
import logging
from groq import Groq
from typing import List, Dict, Optional

from .exceptions import APIError, InvalidAPIKeyError
from .validators import validate_api_key, validate_temperature, validate_max_tokens, validate_message
from .constants import DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS

logger = logging.getLogger(__name__)


class ChatBot:
    """Simple chatbot with conversation history"""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        system_message: Optional[str] = None
    ):
        """
        Initialize chatbot

        Args:
            api_key: API key
            model: Model name to use
            system_message: Optional system message to set chatbot behavior

        Raises:
            InvalidAPIKeyError: If API key is invalid
            APIError: If client initialization fails
        """
        self.api_key = validate_api_key(api_key)
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []

        # Add system message if provided
        if system_message:
            self.conversation_history.append({
                "role": "system",
                "content": system_message
            })

        try:
            self.client = Groq(api_key=self.api_key)
            logger.info(f"ChatBot initialized with model: {self.model}")
        except Exception as e:
            raise APIError(f"Failed to initialize API client: {e}")

    def chat(
        self,
        message: str,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS
    ) -> str:
        """
        Send a message and get response

        Args:
            message: User message
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response

        Returns:
            Assistant's response

        Raises:
            ValueError: If parameters are invalid
            APIError: If API call fails
        """
        # Validate inputs
        message = validate_message(message)
        temperature = validate_temperature(temperature)
        max_tokens = validate_max_tokens(max_tokens)

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        logger.debug(f"Sending message (temp={temperature}, tokens={max_tokens})")

        try:
            # Get response from API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Extract response content
            assistant_message = response.choices[0].message.content

            if not assistant_message:
                raise APIError("Received empty response from API")

            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            logger.debug(f"Received response ({len(assistant_message)} chars)")
            return assistant_message

        except Exception as e:
            # Remove the user message from history since we failed
            self.conversation_history.pop()
            raise APIError(f"Failed to get response from API: {e}")

    def reset(self) -> None:
        """Clear conversation history (keeps system message if any)"""
        system_messages = [
            msg for msg in self.conversation_history
            if msg.get("role") == "system"
        ]
        self.conversation_history = system_messages
        logger.info("Conversation history reset")

    def get_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history

        Returns:
            List of message dictionaries
        """
        return self.conversation_history.copy()

    def get_message_count(self) -> int:
        """
        Get number of messages in conversation (excluding system messages)

        Returns:
            Number of messages
        """
        return len([
            msg for msg in self.conversation_history
            if msg.get("role") != "system"
        ])
