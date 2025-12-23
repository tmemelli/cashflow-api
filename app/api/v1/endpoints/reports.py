"""
Reports endpoints module.

This module provides REST API endpoints for financial reports and analytics.
Generates insights, trends, and summaries of user's financial data.

Endpoints:
- GET /reports/summary - Overall financial summary
- GET /reports/by-category - Spending/income by category
- GET /reports/monthly - Monthly breakdown
- GET /reports/trends - Financial trends over time
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.api.deps import get_db, get_current_active_user
from app.crud.crud_transaction import transaction as crud_transaction
from app.crud.crud_category import category as crud_category
from app.models.user import User
from app.models.transaction import Transaction, TransactionType
from app.models.category import Category

router = APIRouter()


# GET /reports/summary - Overall summary
@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """
    Get overall financial summary.
    
    Query Parameters:
    - start_date: Filter from date (YYYY-MM-DD) - optional, defaults to 30 days ago
    - end_date: Filter to date (YYYY-MM-DD) - optional, defaults to today
    
    Returns:
    {
        "period": {
            "start_date": "2025-01-01",
            "end_date": "2025-01-31"
        },
        "statistics": {
            "total_income": "5000.00",
            "total_expense": "3500.50",
            "balance": "1499.50",
            "transaction_count": 25
        },
        "averages": {
            "avg_daily_income": "161.29",
            "avg_daily_expense": "112.92",
            "avg_transaction_amount": "300.02"
        }
    }
    """
    # Set default dates
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    # Get statistics
    stats = crud_transaction.get_statistics(
        db, user_id=current_user.id, start_date=start_date, end_date=end_date
    )
    
    # Calculate days in period
    days_in_period = (end_date - start_date).days + 1
    
    # Calculate averages
    total_income = Decimal(stats["total_income"])
    total_expense = Decimal(stats["total_expense"])
    
    avg_daily_income = total_income / days_in_period
    avg_daily_expense = total_expense / days_in_period
    
    if stats["transaction_count"] > 0:
        avg_transaction = (total_income + total_expense) / stats["transaction_count"]
    else:
        avg_transaction = Decimal("0.00")
    
    return {
        "period": {"start_date": start_date, "end_date": end_date},
        "statistics": stats,
        "averages": {
            "avg_daily_income": str(avg_daily_income.quantize(Decimal("0.01"))),
            "avg_daily_expense": str(avg_daily_expense.quantize(Decimal("0.01"))),
            "avg_transaction_amount": str(avg_transaction.quantize(Decimal("0.01")))
        }
    }


# GET /reports/by-category - Breakdown by category
@router.get("/by-category")
def get_by_category(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    transaction_type: Optional[TransactionType] = None
):
    """
    Get spending/income breakdown by category.
    
    Query Parameters:
    - start_date: Filter from date - optional, defaults to 30 days ago
    - end_date: Filter to date - optional, defaults to today
    - transaction_type: Filter by type (income/expense) - optional
    
    Returns:
    {
        "period": {
            "start_date": "2025-01-01",
            "end_date": "2025-01-31"
        },
        "by_category": [
            {
                "category_id": 1,
                "category_name": "Food",
                "category_type": "expense",
                "total_amount": "850.50",
                "transaction_count": 12,
                "percentage": 24.3
            },
            {
                "category_id": 2,
                "category_name": "Transport",
                "category_type": "expense",
                "total_amount": "320.00",
                "transaction_count": 8,
                "percentage": 9.1
            }
        ],
        "uncategorized": {
            "total_amount": "150.00",
            "transaction_count": 3,
            "percentage": 4.3
        },
        "total": "3500.50"
    }
    """
    # Set default dates
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    # Query categorized transactions
    query = (
        db.query(
            Category.id.label('category_id'),
            Category.name.label('category_name'),
            Category.type.label('category_type'),
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('transaction_count')
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.date_transaction >= start_date,
            Transaction.date_transaction <= end_date,
            Transaction.is_deleted == False
        )
    )
    
    if transaction_type:
        query = query.filter(Transaction.type == transaction_type)
    
    results = query.group_by(Category.id, Category.name, Category.type).all()
    
    # Query uncategorized transactions
    uncategorized_query = db.query(
        func.sum(Transaction.amount),
        func.count(Transaction.id)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.category_id == None,
        Transaction.date_transaction >= start_date,
        Transaction.date_transaction <= end_date,
        Transaction.is_deleted == False
    )
    
    if transaction_type:
        uncategorized_query = uncategorized_query.filter(Transaction.type == transaction_type)
    
    uncategorized_total, uncategorized_count = uncategorized_query.first()
    uncategorized_total = uncategorized_total or Decimal("0.00")
    uncategorized_count = uncategorized_count or 0
    
    # Calculate grand total
    grand_total = sum(r.total_amount for r in results) + uncategorized_total
    
    # Build response
    by_category = []
    for r in results:
        percentage = (float(r.total_amount) / float(grand_total) * 100) if grand_total > 0 else 0
        by_category.append({
            "category_id": r.category_id,
            "category_name": r.category_name,
            "category_type": r.category_type.value,
            "total_amount": str(r.total_amount),
            "transaction_count": r.transaction_count,
            "percentage": round(percentage, 2)
        })
    
    uncategorized_percentage = (float(uncategorized_total) / float(grand_total) * 100) if grand_total > 0 else 0
    
    return {
        "period": {"start_date": start_date, "end_date": end_date},
        "by_category": by_category,
        "uncategorized": {
            "total_amount": str(uncategorized_total),
            "transaction_count": uncategorized_count,
            "percentage": round(uncategorized_percentage, 2)
        },
        "total": str(grand_total)
    }


# GET /reports/monthly - Monthly breakdown
@router.get("/monthly")
def get_monthly(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    months: int = Query(default=6, ge=1, le=12, description="Number of months to retrieve")
):
    """
    Get monthly financial breakdown.
    
    Query Parameters:
    - months: Number of months to retrieve (1-12) - default 6
    
    Returns:
    {
        "months": [
            {
                "year": 2025,
                "month": 1,
                "month_name": "January",
                "total_income": "5000.00",
                "total_expense": "3500.50",
                "balance": "1499.50",
                "transaction_count": 25
            },
            {
                "year": 2024,
                "month": 12,
                "month_name": "December",
                "total_income": "4800.00",
                "total_expense": "3200.00",
                "balance": "1600.00",
                "transaction_count": 22
            }
        ]
    }
    """
    import calendar
    
    # Calculate start date
    start_date = date.today() - timedelta(days=months*30)
    
    # Query grouped by year and month
    results = (
        db.query(
            extract('year', Transaction.date_transaction).label('year'),
            extract('month', Transaction.date_transaction).label('month'),
            Transaction.type,
            func.sum(Transaction.amount).label('total')
        )
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.date_transaction >= start_date,
            Transaction.is_deleted == False
        )
        .group_by('year', 'month', Transaction.type)
        .all()
    )
    
    # Organize by month
    months_data = {}
    for r in results:
        key = (int(r.year), int(r.month))
        if key not in months_data:
            months_data[key] = {"income": Decimal("0.00"), "expense": Decimal("0.00")}
        
        if r.type == TransactionType.INCOME:
            months_data[key]["income"] = r.total
        else:
            months_data[key]["expense"] = r.total
    
    # Build response
    month_list = []
    for (year, month), data in sorted(months_data.items(), reverse=True):
        month_list.append({
            "year": year,
            "month": month,
            "month_name": calendar.month_name[month],
            "total_income": str(data["income"]),
            "total_expense": str(data["expense"]),
            "balance": str(data["income"] - data["expense"])
        })
    
    return {"months": month_list}


# GET /reports/trends - Financial trends
@router.get("/trends")
def get_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    period: str = Query(default="weekly", pattern="^(daily|weekly|monthly)$")
):
    """
    Get financial trends over time.
    
    Query Parameters:
    - period: Aggregation period (daily/weekly/monthly) - default weekly
    
    Returns for period="weekly":
    {
        "period": "weekly",
        "data": [
            {
                "period_start": "2025-01-06",
                "period_end": "2025-01-12",
                "total_income": "1250.00",
                "total_expense": "875.25",
                "balance": "374.75",
                "transaction_count": 8
            },
            {
                "period_start": "2024-12-30",
                "period_end": "2025-01-05",
                "total_income": "1100.00",
                "total_expense": "950.00",
                "balance": "150.00",
                "transaction_count": 7
            }
        ]
    }
    """
    # Calculate date range based on period
    if period == "daily":
        start_date = date.today() - timedelta(days=30)
        days_back = 30
    elif period == "weekly":
        start_date = date.today() - timedelta(weeks=12)
        days_back = 12 * 7
    else:  # monthly
        start_date = date.today() - timedelta(days=365)
        days_back = 365
    
    # Query transactions
    results = (
        db.query(
            Transaction.date_transaction,
            Transaction.type,
            func.sum(Transaction.amount).label('total')
        )
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.date_transaction >= start_date,
            Transaction.is_deleted == False
        )
        .group_by(Transaction.date_transaction, Transaction.type)
        .all()
    )
    
    # Organize data by date
    daily_data = {}
    for r in results:
        if r.date_transaction not in daily_data:
            daily_data[r.date_transaction] = {"income": Decimal("0.00"), "expense": Decimal("0.00")}
        
        if r.type == TransactionType.INCOME:
            daily_data[r.date_transaction]["income"] = r.total
        else:
            daily_data[r.date_transaction]["expense"] = r.total
    
    # Aggregate by period
    trend_data = []
    
    if period == "daily":
        # Return daily data
        for i in range(days_back):
            current_date = date.today() - timedelta(days=i)
            data = daily_data.get(current_date, {"income": Decimal("0.00"), "expense": Decimal("0.00")})
            trend_data.append({
                "period_start": current_date,
                "period_end": current_date,
                "total_income": str(data["income"]),
                "total_expense": str(data["expense"]),
                "balance": str(data["income"] - data["expense"])
            })
        trend_data.reverse()
    
    elif period == "weekly":
        # Group by weeks
        for i in range(12):
            week_start = date.today() - timedelta(weeks=i+1)
            week_end = date.today() - timedelta(weeks=i)
            
            week_income = Decimal("0.00")
            week_expense = Decimal("0.00")
            
            for current_date, data in daily_data.items():
                if week_start <= current_date < week_end:
                    week_income += data["income"]
                    week_expense += data["expense"]
            
            trend_data.append({
                "period_start": week_start,
                "period_end": week_end - timedelta(days=1),
                "total_income": str(week_income),
                "total_expense": str(week_expense),
                "balance": str(week_income - week_expense)
            })
        trend_data.reverse()
    
    else:  # monthly
        # Group by months using extract
        monthly_results = (
            db.query(
                extract('year', Transaction.date_transaction).label('year'),
                extract('month', Transaction.date_transaction).label('month'),
                Transaction.type,
                func.sum(Transaction.amount).label('total')
            )
            .filter(
                Transaction.user_id == current_user.id,
                Transaction.date_transaction >= start_date,
                Transaction.is_deleted == False
            )
            .group_by('year', 'month', Transaction.type)
            .all()
        )
        
        months_data = {}
        for r in monthly_results:
            key = (int(r.year), int(r.month))
            if key not in months_data:
                months_data[key] = {"income": Decimal("0.00"), "expense": Decimal("0.00")}
            
            if r.type == TransactionType.INCOME:
                months_data[key]["income"] = r.total
            else:
                months_data[key]["expense"] = r.total
        
        # Build 12 months of data
        for i in range(12):
            month_date = date.today().replace(day=1) - timedelta(days=i*30)
            key = (month_date.year, month_date.month)
            data = months_data.get(key, {"income": Decimal("0.00"), "expense": Decimal("0.00")})
            
            # Calculate month start/end
            import calendar
            last_day = calendar.monthrange(month_date.year, month_date.month)[1]
            period_start = month_date.replace(day=1)
            period_end = month_date.replace(day=last_day)
            
            trend_data.append({
                "period_start": period_start,
                "period_end": period_end,
                "total_income": str(data["income"]),
                "total_expense": str(data["expense"]),
                "balance": str(data["income"] - data["expense"])
            })
        trend_data.reverse()
    
    return {
        "period": period,
        "data": trend_data
    }
