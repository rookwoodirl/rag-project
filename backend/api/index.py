from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our existing FastAPI app
from main import app

# Configure CORS for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vercel serverless function handler
async def handler(request: Request):
    """
    Handle requests in a serverless context using ASGI 3.0 protocol.
    """
    return await app(request.scope, request._receive, request._send)

# Entry point for Vercel serverless function
def entrypoint(request):
    return handler(request) 
