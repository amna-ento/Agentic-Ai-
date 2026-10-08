from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel

from app.agent import agent
from app.database.database import initialize_database


app = FastAPI(
    title="Personal AI Assistant API",
    description="API for interacting with the Personal AI Assistant.",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.on_event("startup")
def startup():
    initialize_database()


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    thread_id = str(uuid4())

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": request.message,
                }
            ]
        },
        config={
            "configurable": {
                "thread_id": thread_id,
            }
        },
    )

    return ChatResponse(
        response=result["messages"][-1].content
    )