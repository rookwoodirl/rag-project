#!/usr/bin/env python3

import os
import sys
import asyncio
from pathlib import Path

# Add the parent directory to the path so we can import modules
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables
from dotenv import load_dotenv
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from chat_service import ChatService

async def test_chat():
    """Test the chat service with a simple query"""
    try:
        # Initialize the chat service
        chat_service = ChatService()
        
        # Test a simple query
        query = "What is RAG in the context of AI?"
        print(f"Query: {query}")
        
        response = await chat_service.generate_response(query)
        print(f"\nResponse from GPT-4.1:\n{response}")
        
        # Test with conversation history
        history = [
            {"role": "user", "content": query},
            {"role": "assistant", "content": response}
        ]
        
        follow_up = "Can you give me an example of how it's used?"
        print(f"\nFollow-up query: {follow_up}")
        
        response = await chat_service.generate_response(follow_up, history)
        print(f"\nResponse with history:\n{response}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_chat()) 