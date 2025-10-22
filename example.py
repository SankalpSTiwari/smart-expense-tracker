#!/usr/bin/env python3
"""
Example script demonstrating programmatic use of Smart Expense Tracker
This shows how to use the modules without the CLI interface
"""

from datetime import datetime, timedelta
from database import Database
from expense_manager import ExpenseManager
from analytics import Analytics
from visualizations import Visualizer


def main():
    """Example usage of the Smart Expense Tracker modules"""
    
    # Initialize components
    print("=== Smart Expense Tracker - Example Usage ===\n")
    
    db = Database()
    manager = ExpenseManager(db)
    analytics = Analytics(db)
    visualizer = Visualizer(db)
    
    # Example 1: Add some expenses
    print("1. Adding sample expenses...")
    
    expenses_data = [
        {"amount": 45.50, "category": "Food & Dining", "description": "Lunch at restaurant"},
        {"amount": 120.00, "category": "Shopping", "description": "New shoes"},
        {"amount": 25.30, "category": "Transportation", "description": "Uber ride"},
        {"amount": 80.00, "category": "Groceries", "description": "Weekly groceries"},
        {"amount": 15.00, "category": "Entertainment", "description": "Movie tickets"},
    ]
    
    for expense in expenses_data:
        result = manager.add_expense(**expense)
        if result['success']:
            print(f"  ✓ Added: {expense['description']} - ${expense['amount']:.2f}")
    
    # Example 2: View recent expenses
    print("\n2. Viewing recent expenses...")
    recent = manager.get_recent_expenses(days=30)
    print(f"  Found {len(recent)} expenses in the last 30 days")
    
    # Example 3: Get spending summary
    print("\n3. Monthly spending summary...")
    summary = analytics.get_spending_summary("month")
    print(f"  Total spent: ${summary['total_spent']:.2f}")
    print(f"  Transactions: {summary['transaction_count']}")
    print(f"  Average per day: ${summary['avg_per_day']:.2f}")
    
    # Example 4: Category breakdown
    print("\n4. Category breakdown...")
    breakdown = analytics.get_category_breakdown()
    if breakdown:
        print("  Top 3 categories:")
        for cat in breakdown[:3]:
            print(f"    • {cat['category']}: ${cat['total']:.2f} ({cat['percentage']:.1f}%)")
    
    # Example 5: Set budgets
    print("\n5. Setting budgets...")
    budget_data = [
        {"category": "Food & Dining", "monthly_limit": 500.00},
        {"category": "Shopping", "monthly_limit": 300.00},
        {"category": "Transportation", "monthly_limit": 200.00},
    ]
    
    for budget in budget_data:
        result = manager.set_budget(budget['category'], budget['monthly_limit'])
        if result['success']:
            print(f"  ✓ Set budget for {budget['category']}: ${budget['monthly_limit']:.2f}/month")
    
    # Example 6: Check budget status
    print("\n6. Budget status...")
    budget_status = manager.get_budget_status()
    for status in budget_status:
        print(f"  {status['category']}: ${status['spent']:.2f} / ${status['limit']:.2f} ({status['percentage']:.1f}%)")
    
    # Example 7: Get insights
    print("\n7. Smart insights...")
    insights = analytics.get_spending_insights()
    for i, insight in enumerate(insights[:3], 1):  # Show first 3 insights
        print(f"  {i}. {insight}")
    
    # Example 8: Generate a chart
    print("\n8. Generating category pie chart...")
    try:
        chart_file = visualizer.plot_category_pie_chart()
        if chart_file:
            print(f"  ✓ Chart saved to: {chart_file}")
    except Exception as e:
        print(f"  ⚠ Could not generate chart: {str(e)}")
    
    # Example 9: Search expenses
    print("\n9. Searching expenses...")
    results = manager.search_expenses("lunch")
    print(f"  Found {len(results)} expense(s) matching 'lunch'")
    
    # Example 10: Get trend analysis
    print("\n10. Trend analysis...")
    trend = analytics.get_trend_analysis()
    if trend['trend'] != "INSUFFICIENT_DATA":
        print(f"  Trend: {trend['trend']}")
        print(f"  Average monthly spending: ${trend['avg_monthly_spending']:.2f}")
    else:
        print(f"  {trend['message']}")
    
    # Close database connection
    db.close()
    
    print("\n=== Example completed successfully! ===")
    print("\nTip: Run 'python main.py' to use the interactive CLI interface")


if __name__ == "__main__":
    main()

