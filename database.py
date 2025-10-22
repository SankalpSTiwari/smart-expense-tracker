"""
Database module for Smart Expense Tracker
Handles all database operations using SQLite
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import os


class Database:
    """Manages database operations for expense tracking"""
    
    def __init__(self, db_name: str = "expenses.db"):
        """Initialize database connection"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        # Expenses table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                payment_method TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Budget table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL UNIQUE,
                monthly_limit REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Categories table for predefined categories
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                icon TEXT
            )
        """)
        
        self.conn.commit()
        self._initialize_default_categories()
    
    def _initialize_default_categories(self):
        """Initialize default expense categories"""
        default_categories = [
            ('Food & Dining', '🍔'),
            ('Transportation', '🚗'),
            ('Shopping', '🛍️'),
            ('Entertainment', '🎬'),
            ('Healthcare', '🏥'),
            ('Bills & Utilities', '💡'),
            ('Education', '📚'),
            ('Travel', '✈️'),
            ('Groceries', '🛒'),
            ('Personal Care', '💅'),
            ('Rent', '🏠'),
            ('Investments', '📈'),
            ('Others', '📌')
        ]
        
        for category, icon in default_categories:
            try:
                self.cursor.execute(
                    "INSERT INTO categories (name, icon) VALUES (?, ?)",
                    (category, icon)
                )
            except sqlite3.IntegrityError:
                # Category already exists
                pass
        
        self.conn.commit()
    
    def add_expense(self, date: str, category: str, amount: float, 
                   description: str = "", payment_method: str = "Cash") -> int:
        """Add a new expense"""
        self.cursor.execute("""
            INSERT INTO expenses (date, category, amount, description, payment_method)
            VALUES (?, ?, ?, ?, ?)
        """, (date, category, amount, description, payment_method))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_expenses(self, limit: Optional[int] = None, 
                    category: Optional[str] = None,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> List[sqlite3.Row]:
        """Retrieve expenses with optional filters"""
        query = "SELECT * FROM expenses WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date DESC, id DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense by ID"""
        self.cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def update_expense(self, expense_id: int, **kwargs) -> bool:
        """Update an expense"""
        valid_fields = ['date', 'category', 'amount', 'description', 'payment_method']
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return False
        
        values.append(expense_id)
        query = f"UPDATE expenses SET {', '.join(updates)} WHERE id = ?"
        self.cursor.execute(query, values)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def get_categories(self) -> List[sqlite3.Row]:
        """Get all categories"""
        self.cursor.execute("SELECT * FROM categories ORDER BY name")
        return self.cursor.fetchall()
    
    def add_category(self, name: str, icon: str = "📌") -> int:
        """Add a new category"""
        self.cursor.execute(
            "INSERT INTO categories (name, icon) VALUES (?, ?)",
            (name, icon)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def set_budget(self, category: str, monthly_limit: float) -> int:
        """Set or update budget for a category"""
        self.cursor.execute("""
            INSERT INTO budgets (category, monthly_limit)
            VALUES (?, ?)
            ON CONFLICT(category) DO UPDATE SET monthly_limit = ?
        """, (category, monthly_limit, monthly_limit))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_budgets(self) -> List[sqlite3.Row]:
        """Get all budgets"""
        self.cursor.execute("SELECT * FROM budgets ORDER BY category")
        return self.cursor.fetchall()
    
    def get_budget(self, category: str) -> Optional[sqlite3.Row]:
        """Get budget for a specific category"""
        self.cursor.execute(
            "SELECT * FROM budgets WHERE category = ?",
            (category,)
        )
        return self.cursor.fetchone()
    
    def get_total_expenses(self, start_date: Optional[str] = None,
                          end_date: Optional[str] = None,
                          category: Optional[str] = None) -> float:
        """Calculate total expenses with optional filters"""
        query = "SELECT SUM(amount) FROM expenses WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        self.cursor.execute(query, params)
        result = self.cursor.fetchone()[0]
        return result if result else 0.0
    
    def get_category_summary(self, start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> List[Tuple]:
        """Get spending summary by category"""
        query = """
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM expenses
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " GROUP BY category ORDER BY total DESC"
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def get_monthly_summary(self) -> List[Tuple]:
        """Get monthly spending summary"""
        query = """
            SELECT strftime('%Y-%m', date) as month, 
                   SUM(amount) as total,
                   COUNT(*) as count
            FROM expenses
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

