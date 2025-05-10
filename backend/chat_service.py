import os
import openai
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ChatService:
    """Service for interacting with OpenAI Chat API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI service"""
        # Try to load environment variables again from a relative path
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = "gpt-4-1106-preview"  # Using GPT-4 Turbo (as of creation, closest to 4.1)
    
    async def generate_response(self, 
                              query: str, 
                              history: List[Dict[str, str]] = None,
                              system_prompt: str = None) -> str:
        """
        Generate a response from the OpenAI GPT model
        
        Args:
            query: The user's query
            history: A list of previous message exchanges
            system_prompt: Optional system prompt to guide the assistant
            
        Returns:
            The assistant's response
        """
        if history is None:
            history = []
            
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            # Default system prompt
            messages.append({
                "role": "system", 
                "content": "You are a helpful AI assistant specialized in answering questions about RAG systems and document processing."
            })
        
        # Add conversation history
        for message in history:
            messages.append({
                "role": message.get("role", "user"),
                "content": message.get("content", "")
            })
        
        # Add the current query
        messages.append({"role": "user", "content": query})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating chat response: {str(e)}")
            raise
    
    async def generate_ticket_assisted_response(self,
                                             query: str,
                                             ticket_description: str,
                                             history: List[Dict[str, str]] = None) -> str:
        """
        Generate a response with the context of a ticket
        
        Args:
            query: The user's query
            ticket_description: The description of the ticket to provide context
            history: A list of previous message exchanges
            
        Returns:
            The assistant's response
        """
        # Create a system prompt based on the ticket description
        system_prompt = f"""You are a helpful ticket management assistant. 
You are helping with a ticket that has the following description:

{ticket_description}

As a personal ticketing application helper, your goal is to provide assistance with this ticket.
Respond helpfully to questions about this ticket and suggest next steps or solutions when appropriate.
Be concise but thorough in your responses."""

        return await self.generate_response(
            query=query,
            history=history,
            system_prompt=system_prompt
        ) 