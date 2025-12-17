"""
AI Service for chat functionality.

This service handles all AI-powered chat operations:
- Question analysis
- Data retrieval from database
- OpenAI API integration
- Response generation
- Conversation history management

The service acts as an intermediary between the user, database,
and OpenAI API, ensuring secure and efficient operations.
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from openai import OpenAI
from datetime import datetime

from app.core.config import settings
from app.models.user import User
from app.models.chat import Chat
from app.models.transaction import Transaction
from app.models.category import Category
from sqlalchemy import func


class AIService:
    """
    Service class for AI chat operations.
    
    Handles the complete flow of AI-powered financial assistance:
    1. Receives user's question
    2. Analyzes intent and required data
    3. Fetches relevant financial data
    4. Generates AI response via OpenAI
    5. Saves conversation to history
    
    Attributes:
        client (OpenAI): OpenAI API client instance.
        model (str): OpenAI model to use (default: gpt-4o-mini).
    
    Example:
        >>> from app.services.ai_service import AIService
        >>> service = AIService()
        >>> response = service.process_question(
        ...     db=db,
        ...     user=current_user,
        ...     question="How much did I spend?"
        ... )
    """
    
    def __init__(self):
        """
        Initialize AI Service with OpenAI client.
        
        Raises:
            ValueError: If OPENAI_API_KEY is not configured.
        """
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured in environment")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    def process_question(
        self,
        db: Session,
        user: User,
        question: str
    ) -> Dict[str, Any]:
        """
        Process user's question and generate AI response.
        
        This is the main entry point for chat functionality. Orchestrates
        the complete flow from question to response.
        
        Args:
            db (Session): Database session for queries.
            user (User): Current authenticated user.
            question (str): User's question or prompt.
        
        Returns:
            dict: Response containing:
                - reply (str): AI's natural language response
                - data (dict, optional): Structured data supporting response
                - sql_query (str, optional): SQL query executed
        
        Raises:
            Exception: If OpenAI API fails or database error occurs.
        
        Example:
            >>> response = service.process_question(
            ...     db=db,
            ...     user=current_user,
            ...     question="How much did I spend this month?"
            ... )
            >>> print(response["reply"])
            "You spent $1,500.00 this month on 25 transactions."
        """
        
        try:
            # Step 1: Analyze question and fetch data
            context_data = self._fetch_financial_context(db, user, question)
            
            # Step 2: Generate AI response
            ai_response = self._generate_ai_response(question, context_data, user)
            
            # Step 3: Save to history
            self._save_to_history(
                db=db,
                user=user,
                question=question,
                response=ai_response["reply"],
                sql_query=ai_response.get("sql_query"),
                was_successful=True
            )
            
            return ai_response
            
        except Exception as e:
            # Save error to history
            error_msg = str(e)
            self._save_to_history(
                db=db,
                user=user,
                question=question,
                response=f"Sorry, I encountered an error: {error_msg}",
                sql_query=None,
                was_successful=False,
                error_message=error_msg
            )
            
            raise

    def _fetch_financial_context(
        self,
        db: Session,
        user: User,
        question: str
    ) -> Dict[str, Any]:
        """
        Fetch relevant financial data based on user's question.
        
        Analyzes the question to determine what data is needed and
        retrieves it from the database.
        
        Args:
            db (Session): Database session.
            user (User): Current user.
            question (str): User's question (used for intent detection).
        
        Returns:
            dict: Financial context containing:
                - total_income (float): Total income amount
                - total_expense (float): Total expense amount
                - balance (float): Current balance
                - transaction_count (int): Number of transactions
                - categories (list): Categories with spending
                - recent_transactions (list): Last 10 transactions
        
        Note:
            Currently fetches comprehensive data. Future optimization:
            analyze question to fetch only relevant data.
        """
        
        # Fetch summary statistics
        income_total = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.type == "income",
            Transaction.is_deleted == False
        ).scalar() or 0.0
        
        expense_total = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.type == "expense",
            Transaction.is_deleted == False
        ).scalar() or 0.0
        
        balance = income_total - expense_total
        
        transaction_count = db.query(func.count(Transaction.id)).filter(
            Transaction.user_id == user.id,
            Transaction.is_deleted == False
        ).scalar() or 0
        
        # Fetch category breakdown
        category_stats = db.query(
            Category.name,
            Category.type,
            func.sum(Transaction.amount).label('total')
        ).join(
            Transaction, Transaction.category_id == Category.id
        ).filter(
            Transaction.user_id == user.id,
            Transaction.is_deleted == False
        ).group_by(
            Category.id, Category.name, Category.type
        ).all()
        
        categories = [
            {
                "name": name,
                "type": type_,
                "total": float(total)
            }
            for name, type_, total in category_stats
        ]
        
        # Fetch recent transactions
        recent = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.is_deleted == False
        ).order_by(
            Transaction.date.desc()
        ).limit(10).all()
        
        recent_transactions = [
            {
                "id": t.id,
                "type": t.type,
                "amount": float(t.amount),
                "description": t.description,
                "date": t.date.isoformat(),
                "category": t.category.name if t.category else None
            }
            for t in recent
        ]
        
        return {
            "total_income": float(income_total),
            "total_expense": float(expense_total),
            "balance": float(balance),
            "transaction_count": transaction_count,
            "categories": categories,
            "recent_transactions": recent_transactions
        }

    def _generate_ai_response(
        self,
        question: str,
        context_data: Dict[str, Any],
        user: User
    ) -> Dict[str, Any]:
        """
        Generate AI response using OpenAI API.
        
        Sends user's question and financial context to OpenAI,
        which generates a natural language response based on the data.
        
        Args:
            question (str): User's question.
            context_data (dict): Financial data context from database.
            user (User): Current user (for personalization).
        
        Returns:
            dict: Response containing:
                - reply (str): AI's natural language response
                - data (dict): Structured data (same as context_data)
                - sql_query (str): Description of queries executed
        
        Raises:
            Exception: If OpenAI API call fails.
        
        Note:
            Uses GPT-4o-mini by default for cost efficiency.
            Can be upgraded to GPT-4 for better responses.
        """
        
        # Build system prompt (AI's personality and instructions)
        system_prompt = f"""You are a helpful personal finance assistant.

User Information:
- Email: {user.email}
- User ID: {user.id}

Financial Context (all amounts in dollars):
- Total Income: ${context_data['total_income']:.2f}
- Total Expenses: ${context_data['total_expense']:.2f}
- Current Balance: ${context_data['balance']:.2f}
- Total Transactions: {context_data['transaction_count']}

Categories Breakdown:
{self._format_categories(context_data['categories'])}

Recent Transactions:
{self._format_recent_transactions(context_data['recent_transactions'])}

Instructions:
1. Answer the user's question based on the data above
2. Be concise and friendly
3. Use specific numbers from the data
4. If the question cannot be answered with available data, explain what's missing
5. Format currency as $X,XXX.XX
6. Provide actionable insights when appropriate
"""
        
        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_reply = response.choices[0].message.content
            
            return {
                "reply": ai_reply,
                "data": context_data,
                "sql_query": "Multiple aggregation queries executed (income, expense, categories, recent transactions)"
            }
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    
    def _format_categories(self, categories: list) -> str:
        """
        Format categories for AI prompt.
        
        Args:
            categories (list): List of category dicts.
        
        Returns:
            str: Formatted string for prompt.
        """
        if not categories:
            return "No categories yet."
        
        lines = []
        for cat in categories:
            lines.append(f"- {cat['name']} ({cat['type']}): ${cat['total']:.2f}")
        
        return "\n".join(lines)
    
    
    def _format_recent_transactions(self, transactions: list) -> str:
        """
        Format recent transactions for AI prompt.
        
        Args:
            transactions (list): List of transaction dicts.
        
        Returns:
            str: Formatted string for prompt.
        """
        if not transactions:
            return "No transactions yet."
        
        lines = []
        for t in transactions[:5]:  # Only show 5 most recent in prompt
            lines.append(
                f"- {t['date']}: {t['type'].title()} ${t['amount']:.2f} "
                f"({t['category'] or 'Uncategorized'}) - {t['description']}"
            )
        
        return "\n".join(lines)

    def _save_to_history(
        self,
        db: Session,
        user: User,
        question: str,
        response: str,
        sql_query: Optional[str] = None,
        was_successful: bool = True,
        error_message: Optional[str] = None
    ) -> Chat:
        """
        Save conversation to database history.
        
        Stores the complete conversation exchange for future reference,
        debugging, and user history retrieval.
        
        Args:
            db (Session): Database session.
            user (User): Current user.
            question (str): User's question.
            response (str): AI's response.
            sql_query (str, optional): SQL query executed.
            was_successful (bool): Whether operation succeeded.
            error_message (str, optional): Error message if failed.
        
        Returns:
            Chat: Created chat record.
        
        Note:
            Always commits to database, even on errors.
            This ensures audit trail is preserved.
        """
        
        chat = Chat(
            user_id=user.id,
            question=question,
            response=response,
            sql_query=sql_query,
            was_successful=was_successful,
            error_message=error_message
        )
        
        db.add(chat)
        db.commit()
        db.refresh(chat)
        
        return chat
    
    
    def get_user_history(
        self,
        db: Session,
        user: User,
        limit: int = 10
    ) -> list[Chat]:
        """
        Retrieve user's chat history.
        
        Fetches recent conversation history for display or analysis.
        
        Args:
            db (Session): Database session.
            user (User): Current user.
            limit (int): Maximum number of records to return (default: 10).
        
        Returns:
            list[Chat]: List of chat records, newest first.
        
        Example:
            >>> history = service.get_user_history(db, user, limit=5)
            >>> for chat in history:
            ...     print(f"Q: {chat.question}")
            ...     print(f"A: {chat.response}")
        """
        
        return db.query(Chat).filter(
            Chat.user_id == user.id
        ).order_by(
            Chat.created_at.desc()
        ).limit(limit).all()