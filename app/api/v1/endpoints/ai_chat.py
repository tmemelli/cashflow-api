"""
AI Chat endpoints.

Provides AI-powered financial assistance through natural language:
- Chat with AI about finances
- View conversation history
- Delete specific conversations

All endpoints require authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.chat import Chat
from app.schemas.ai_chat import ChatRequest, ChatResponse, ChatHistory
from app.services.ai_service import AIService

def get_ai_service() -> AIService:
    """
    Dependency that provides AIService instance.
    
    Returns:
        AIService: Configured AI service instance.
    """
    return AIService()


router = APIRouter()


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    service: AIService = Depends(get_ai_service)
):
    """
    Chat with AI assistant about your finances.
    
    Send a question in natural language and receive an AI-generated
    response based on your financial data.
    
    **Examples of questions:**
    - "How much did I spend this month?"
    - "What's my current balance?"
    - "Show me my top expense categories"
    - "How much did I spend on food?"
    
    The AI analyzes your transactions and provides personalized answers.
    
    Args:
        request (ChatRequest): User's question.
        db (Session): Database session (injected).
        current_user (User): Authenticated user (injected).
    
    Returns:
        ChatResponse: AI's response with optional structured data.
    
    Raises:
        HTTPException 500: If OpenAI API fails or processing error occurs.
    
    Note:
        - Conversation is automatically saved to history
        - Response includes structured data when relevant
        - SQL query included for transparency
    """
    
    try:
        response = service.process_question(
            db=db,
            user=current_user,
            question=request.message
        )
        
        return ChatResponse(
            reply=response["reply"],
            data=response.get("data"),
            sql_query=response.get("sql_query")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}"
        )


@router.get("/history", response_model=List[ChatHistory], status_code=status.HTTP_200_OK)
def get_chat_history(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    service: AIService = Depends(get_ai_service)
):
    """
    Retrieve your AI chat history.
    
    Returns your most recent conversations with the AI assistant,
    newest first.
    
    Args:
        limit (int): Maximum number of records to return (default: 10, max: 50).
        db (Session): Database session (injected).
        current_user (User): Authenticated user (injected).
    
    Returns:
        List[ChatHistory]: List of chat records.
    
    Note:
        - Only returns YOUR conversations (user isolation)
        - Includes metadata (timestamps, SQL queries, errors)
        - Useful for reviewing past interactions
    """
    
    # Validate limit
    if limit > 50:
        limit = 50
    
    history = service.get_user_history(db, current_user, limit)
    
    return history


@router.delete("/history/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a specific chat from history.
    
    Permanently removes a conversation record from your history.
    
    Args:
        chat_id (int): ID of the chat to delete.
        db (Session): Database session (injected).
        current_user (User): Authenticated user (injected).
    
    Raises:
        HTTPException 404: If chat not found or doesn't belong to user.
    
    Note:
        - Only YOUR chats can be deleted (user isolation)
        - Deletion is permanent (no soft delete for chats)
    """
    
    # Find chat
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    # Delete
    db.delete(chat)
    db.commit()
    
    return None
