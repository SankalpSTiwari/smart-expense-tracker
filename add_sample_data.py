#!/usr/bin/env python3
"""
Add sample expenses across multiple months for trend analysis
"""

from datetime import datetime, timedelta
from database import Database
from expense_manager import ExpenseManager
import random

def add_varied_expenses():
    """Add expenses across multiple months"""
    
    db = Database()
    manager = ExpenseManager(db)
    
    # Define categories and typical amounts
    expense_templates = [
        ("Food & Dining", 15, 50),
        ("Transportation", 10, 30),
        ("Shopping", 30, 150),
        ("Groceries", 40, 100),
        ("Entertainment", 15, 60),
        ("Bills & Utilities", 50, 200),
    ]
    
    descriptions = {
        "Food & Dining": ["Breakfast", "Lunch", "Dinner", "Coffee", "Restaurant"],
        "Transportation": ["Gas", "Uber", "Bus fare", "Parking", "Taxi"],
        "Shopping": ["Clothes", "Electronics", "Shoes", "Accessories", "Books"],
        "Groceries": ["Weekly groceries", "Fruits & vegetables", "Snacks", "Beverages"],
        "Entertainment": ["Movie", "Concert", "Streaming", "Games", "Sports event"],
        "Bills & Utilities": ["Electricity", "Water", "Internet", "Phone", "Insurance"],
    }
    
    # Generate expenses for last 6 months
    today = datetime.now()
    expenses_added = 0
    
    print("Adding sample expenses across multiple months...")
    print("=" * 60)
    
    for month_offset in range(6):
        # Calculate the month date
        target_month = today - timedelta(days=30 * month_offset)
        month_name = target_month.strftime("%B %Y")
        
        print(f"\n📅 {month_name}")
        
        # Add 15-25 random expenses per month
        num_expenses = random.randint(15, 25)
        
        for _ in range(num_expenses):
            # Pick random category
            category, min_amt, max_amt = random.choice(expense_templates)
            
            # Random amount
            amount = round(random.uniform(min_amt, max_amt), 2)
            
            # Random day in that month
            day = random.randint(1, 28)  # Use 28 to avoid month-end issues
            expense_date = target_month.replace(day=day)
            
            # Random description
            description = random.choice(descriptions[category])
            
            # Random payment method
            payment_method = random.choice(["Cash", "Credit Card", "Debit Card", "UPI"])
            
            # Add expense
            result = manager.add_expense(
                amount=amount,
                category=category,
                description=description,
                date=expense_date.strftime("%Y-%m-%d"),
                payment_method=payment_method
            )
            
            if result['success']:
                expenses_added += 1
        
        print(f"  Added {num_expenses} expenses")
    
    print("\n" + "=" * 60)
    print(f"✅ Successfully added {expenses_added} sample expenses!")
    print(f"\n💡 Now you have data for:")
    print(f"   • Trend analysis (6 months of data)")
    print(f"   • Monthly comparisons")
    print(f"   • Spending patterns")
    print(f"   • Better insights")
    print("\n🚀 Refresh your Streamlit app to see the updated analytics!")
    
    db.close()


if __name__ == "__main__":
    add_varied_expenses()

