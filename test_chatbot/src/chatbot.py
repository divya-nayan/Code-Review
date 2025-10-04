"""
Chatbot implementation using Groq API
"""
from groq import Groq
from typing import List, Dict


class ChatBot:
    """Simple chatbot with conversation history"""

    def __init__(self, api_key: str, model: str = "llama-3.2-90b-text-preview"):
        """
        Initialize chatbot

        Args:
            api_key: Groq API key
            model: Model name to use
        """
        self.client = Groq(api_key=api_key)
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []

    def chat(self, message: str, temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Send a message and get response

        Args:
            message: User message
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Assistant's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        # Get response from API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation_history,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Extract response content
        assistant_message = response.choices[0].message.content

        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def reset(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history
