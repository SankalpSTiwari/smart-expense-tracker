"""
Expense Manager module for Smart Expense Tracker
Provides high-level operations for expense management
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database import Database
import sqlite3


class ExpenseManager:
    """Manages expense operations and business logic"""
    
    def __init__(self, db: Database):
        """Initialize expense manager with database"""
        self.db = db
    
    def add_expense(self, amount: float, category: str, description: str = "",
                   date: Optional[str] = None, payment_method: str = "Cash") -> Dict:
        """
        Add a new expense
        
        Args:
            amount: Expense amount
            category: Expense category
            description: Optional description
            date: Date in YYYY-MM-DD format (defaults to today)
            payment_method: Payment method used
        
        Returns:
            Dict with expense details and status
        """
        if amount <= 0:
            return {"success": False, "message": "Amount must be greater than 0"}
        
        if not category:
            return {"success": False, "message": "Category is required"}
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            # Validate date format
            datetime.strptime(date, "%Y-%m-%d")
            
            expense_id = self.db.add_expense(
                date=date,
                category=category,
                amount=amount,
                description=description,
                payment_method=payment_method
            )
            
            # Check if expense exceeds budget
            warning = self._check_budget_warning(category, date)
            
            return {
                "success": True,
                "expense_id": expense_id,
                "message": "Expense added successfully",
                "warning": warning
            }
        except ValueError as e:
            return {"success": False, "message": f"Invalid date format: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"Error adding expense: {str(e)}"}
    
    def _check_budget_warning(self, category: str, date: str) -> Optional[str]:
        """Check if expense pushes category over budget"""
        budget = self.db.get_budget(category)
        if not budget:
            return None
        
        # Get first and last day of the month
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        first_day = date_obj.replace(day=1).strftime("%Y-%m-%d")
        last_day = (date_obj.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        last_day_str = last_day.strftime("%Y-%m-%d")
        
        total_spent = self.db.get_total_expenses(
            category=category,
            start_date=first_day,
            end_date=last_day_str
        )
        
        budget_limit = budget['monthly_limit']
        percentage = (total_spent / budget_limit) * 100
        
        if total_spent > budget_limit:
            return f"⚠️ Budget exceeded! Spent ${total_spent:.2f} of ${budget_limit:.2f} ({percentage:.1f}%)"
        elif percentage >= 90:
            return f"⚠️ Warning: {percentage:.1f}% of budget used (${total_spent:.2f} of ${budget_limit:.2f})"
        elif percentage >= 75:
            return f"📊 Note: {percentage:.1f}% of budget used"
        
        return None
    
    def get_expenses(self, limit: Optional[int] = None,
                    category: Optional[str] = None,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> List[Dict]:
        """
        Get expenses with optional filters
        
        Returns:
            List of expense dictionaries
        """
        expenses = self.db.get_expenses(
            limit=limit,
            category=category,
            start_date=start_date,
            end_date=end_date
        )
        
        return [dict(zip(expense.keys(), expense)) for expense in expenses]
    
    def delete_expense(self, expense_id: int) -> Dict:
        """Delete an expense by ID"""
        success = self.db.delete_expense(expense_id)
        
        if success:
            return {"success": True, "message": "Expense deleted successfully"}
        else:
            return {"success": False, "message": "Expense not found"}
    
    def update_expense(self, expense_id: int, **kwargs) -> Dict:
        """Update an expense"""
        success = self.db.update_expense(expense_id, **kwargs)
        
        if success:
            return {"success": True, "message": "Expense updated successfully"}
        else:
            return {"success": False, "message": "Expense not found or no changes made"}
    
    def get_categories(self) -> List[str]:
        """Get list of all categories"""
        categories = self.db.get_categories()
        return [cat['name'] for cat in categories]
    
    def add_category(self, name: str, icon: str = "📌") -> Dict:
        """Add a new category"""
        try:
            category_id = self.db.add_category(name, icon)
            return {
                "success": True,
                "category_id": category_id,
                "message": f"Category '{name}' added successfully"
            }
        except sqlite3.IntegrityError:
            return {"success": False, "message": "Category already exists"}
        except Exception as e:
            return {"success": False, "message": f"Error adding category: {str(e)}"}
    
    def set_budget(self, category: str, monthly_limit: float) -> Dict:
        """Set or update budget for a category"""
        if monthly_limit <= 0:
            return {"success": False, "message": "Budget limit must be greater than 0"}
        
        if category not in self.get_categories():
            return {"success": False, "message": f"Category '{category}' does not exist"}
        
        try:
            self.db.set_budget(category, monthly_limit)
            return {
                "success": True,
                "message": f"Budget set for '{category}': ${monthly_limit:.2f}/month"
            }
        except Exception as e:
            return {"success": False, "message": f"Error setting budget: {str(e)}"}
    
    def get_budget_status(self, category: Optional[str] = None) -> List[Dict]:
        """
        Get budget status for categories
        
        Returns:
            List of budget status dictionaries
        """
        budgets = self.db.get_budgets()
        current_date = datetime.now()
        first_day = current_date.replace(day=1).strftime("%Y-%m-%d")
        last_day = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        last_day_str = last_day.strftime("%Y-%m-%d")
        
        budget_status = []
        
        for budget in budgets:
            cat = budget['category']
            
            if category and cat != category:
                continue
            
            spent = self.db.get_total_expenses(
                category=cat,
                start_date=first_day,
                end_date=last_day_str
            )
            
            limit = budget['monthly_limit']
            remaining = limit - spent
            percentage = (spent / limit * 100) if limit > 0 else 0
            
            status = "OK"
            if spent > limit:
                status = "EXCEEDED"
            elif percentage >= 90:
                status = "WARNING"
            elif percentage >= 75:
                status = "CAUTION"
            
            budget_status.append({
                "category": cat,
                "limit": limit,
                "spent": spent,
                "remaining": remaining,
                "percentage": percentage,
                "status": status
            })
        
        return budget_status
    
    def get_recent_expenses(self, days: int = 7) -> List[Dict]:
        """Get expenses from the last N days"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        return self.get_expenses(start_date=start_date, end_date=end_date)
    
    def get_total_spent(self, start_date: Optional[str] = None,
                       end_date: Optional[str] = None,
                       category: Optional[str] = None) -> float:
        """Get total amount spent with optional filters"""
        return self.db.get_total_expenses(start_date, end_date, category)
    
    def search_expenses(self, keyword: str) -> List[Dict]:
        """Search expenses by description or category"""
        all_expenses = self.get_expenses()
        keyword_lower = keyword.lower()
        
        return [
            expense for expense in all_expenses
            if keyword_lower in expense.get('description', '').lower()
            or keyword_lower in expense.get('category', '').lower()
        ]

