from app.services.chat_service import ChatService
from app.schemas.chat import ChatRequest, ChatResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends
from app.core.deps import get_db

router = APIRouter()

@router.post("/completion", response_model=ChatResponse)
async def chat_completion(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Send a message to the AI assistant and get a response.
    Supports conversation history for multi-turn chat.
    """
    try:
        service = ChatService(db)
        reply = await service.get_completion(
            message=request.message,
            history=request.history
        )
        return ChatResponse(reply=reply)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")
