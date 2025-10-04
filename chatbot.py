"""
Simple chatbot using Groq API
"""
import os
from groq import Groq
from config import GROQ_API_KEY

class SimpleChatbot:
    def __init__(self, api_key=None):
        self.api_key = api_key or GROQ_API_KEY
        self.client = Groq(api_key=self.api_key)
        self.conversation_history = []

    def chat(self, user_message):
        """Send a message and get a response"""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        response = self.client.chat.completions.create(
            model="llama-3.2-90b-text-preview",
            messages=self.conversation_history,
            temperature=0.7,
            max_tokens=1024
        )

        assistant_message = response.choices[0].message.content
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def reset(self):
        """Clear conversation history"""
        self.conversation_history = []


def main():
    """Main chatbot loop"""
    print("Simple Chatbot - Type 'quit' to exit, 'reset' to clear history\n")

    bot = SimpleChatbot()

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == 'quit':
            print("Goodbye!")
            break

        if user_input.lower() == 'reset':
            bot.reset()
            print("Conversation history cleared.")
            continue

        if not user_input:
            continue

        try:
            response = bot.chat(user_input)
            print(f"\nBot: {response}\n")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
