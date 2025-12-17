"""
AI Chat schemas for request/response validation.

This module defines Pydantic schemas for AI chat functionality:
- ChatRequest: User's question to the AI
- ChatResponse: AI's response with optional data
- ChatHistory: Historical chat record with metadata

All schemas include examples for OpenAPI documentation.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any


class ChatRequest(BaseModel):
    """
    Schema for user's chat request.
    
    Validates the incoming question from the user before processing.
    
    Attributes:
        message (str): User's question or prompt. Min 1, max 1000 characters.
    
    Example:
        {
            "message": "How much did I spend on food this month?"
        }
    """
    
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User's question or prompt to the AI assistant",
        examples=["How much did I spend this month?"]
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "What's my current balance?"
                },
                {
                    "message": "Show me my top 5 expense categories"
                },
                {
                    "message": "How much did I spend on transport last month?"
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """
    Schema for AI's response.
    
    Contains the AI's answer and optional structured data.
    
    Attributes:
        reply (str): AI's natural language response to the user.
        data (dict, optional): Structured data supporting the response.
            Can include financial statistics, transaction lists, etc.
        sql_query (str, optional): SQL query executed to gather data.
            Included for transparency and debugging.
    
    Example:
        {
            "reply": "You spent $1,500.00 this month across 25 transactions.",
            "data": {
                "total": 1500.00,
                "count": 25,
                "by_category": [...]
            },
            "sql_query": "SELECT SUM(amount) FROM transactions WHERE..."
        }
    """
    
    reply: str = Field(
        ...,
        description="AI's natural language response",
        examples=["You spent $1,500.00 this month on 25 transactions."]
    )
    
    data: Optional[dict[str, Any]] = Field(
        default=None,
        description="Structured data supporting the response (optional)",
        examples=[{"total": 1500.00, "count": 25}]
    )
    
    sql_query: Optional[str] = Field(
        default=None,
        description="SQL query executed to gather data (for transparency)",
        examples=["SELECT SUM(amount) FROM transactions WHERE type='expense'"]
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "reply": "Your current balance is $2,500.00",
                    "data": {
                        "balance": 2500.00,
                        "total_income": 5000.00,
                        "total_expense": 2500.00
                    }
                }
            ]
        }
    }


class ChatHistory(BaseModel):
    """
    Schema for chat history records.
    
    Represents a single conversation exchange retrieved from database.
    
    Attributes:
        id (int): Unique identifier for this chat record.
        question (str): User's original question.
        response (str): AI's response.
        sql_query (str, optional): SQL query that was executed.
        was_successful (bool): Whether the query executed successfully.
        error_message (str, optional): Error message if query failed.
        created_at (datetime): When this conversation occurred.
    
    Example:
        {
            "id": 1,
            "question": "How much did I spend?",
            "response": "You spent $1,500.00",
            "sql_query": "SELECT SUM(amount)...",
            "was_successful": true,
            "error_message": null,
            "created_at": "2025-12-15T14:30:00Z"
        }
    """
    
    id: int = Field(..., description="Unique chat record ID")
    question: str = Field(..., description="User's question")
    response: str = Field(..., description="AI's response")
    sql_query: Optional[str] = Field(default=None, description="SQL query executed")
    was_successful: bool = Field(default=True, description="Query execution status")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(..., description="Conversation timestamp")
    
    model_config = {
        "from_attributes": True,  # Enable ORM mode (was orm_mode in Pydantic v1)
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "question": "What's my balance?",
                    "response": "Your balance is $2,500.00",
                    "sql_query": "SELECT SUM(CASE...)",
                    "was_successful": True,
                    "error_message": None,
                    "created_at": "2025-12-15T14:30:00.123456Z"
                }
            ]
        }
    }
