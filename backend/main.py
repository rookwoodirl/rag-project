from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from routes import router

# Initialize FastAPI app
app = FastAPI(title="RAG API Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router, prefix="/api")

# Health check endpoint
@app.get("/")
async def root():
    return {"status": "healthy", "service": "RAG Document API"}

# Run with: uvicorn main:app --reload





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
    