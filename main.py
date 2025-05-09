from fastapi import FastAPI
import httpx
import os
from routes import router

# Initialize FastAPI app
app = FastAPI(title="RAG API Service")

# Include router
app.include_router(router)

# Run with: uvicorn main:app --reload





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
    