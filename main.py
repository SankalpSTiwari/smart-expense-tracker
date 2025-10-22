#!/usr/bin/env python3
"""
Smart Expense Tracker - Main CLI Interface
A smart expense tracking application with analytics and budgeting features
"""

import sys
from datetime import datetime, timedelta
from database import Database
from expense_manager import ExpenseManager
from analytics import Analytics
from visualizations import Visualizer


class ExpenseTrackerCLI:
    """Command-line interface for Smart Expense Tracker"""
    
    def __init__(self):
        """Initialize the CLI application"""
        self.db = Database()
        self.manager = ExpenseManager(self.db)
        self.analytics = Analytics(self.db)
        self.visualizer = Visualizer(self.db)
        self.running = True
    
    def clear_screen(self):
        """Clear the terminal screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Print a formatted header"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70 + "\n")
    
    def print_separator(self):
        """Print a separator line"""
        print("-" * 70)
    
    def wait_for_enter(self):
        """Wait for user to press Enter"""
        input("\nPress Enter to continue...")
    
    def display_main_menu(self):
        """Display the main menu"""
        self.clear_screen()
        self.print_header("💰 SMART EXPENSE TRACKER 💰")
        
        print("1.  ➕  Add Expense")
        print("2.  📋  View Expenses")
        print("3.  🔍  Search Expenses")
        print("4.  ✏️   Edit Expense")
        print("5.  🗑️   Delete Expense")
        print("\n6.  📊  View Reports & Analytics")
        print("7.  💡  Smart Insights")
        print("8.  📈  Generate Charts")
        print("\n9.  💰  Budget Management")
        print("10. 🏷️   Manage Categories")
        print("\n0.  🚪  Exit")
        
        self.print_separator()
        return input("Select an option: ").strip()
    
    def add_expense(self):
        """Add a new expense"""
        self.clear_screen()
        self.print_header("➕ Add New Expense")
        
        try:
            # Get amount
            amount_str = input("Amount ($): ").strip()
            amount = float(amount_str)
            
            # Show categories
            categories = self.manager.get_categories()
            print("\nAvailable Categories:")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat}")
            
            # Get category
            cat_choice = input("\nSelect category (number or name): ").strip()
            if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
                category = categories[int(cat_choice) - 1]
            elif cat_choice in categories:
                category = cat_choice
            else:
                print("❌ Invalid category!")
                self.wait_for_enter()
                return
            
            # Get description
            description = input("Description (optional): ").strip()
            
            # Get date
            date_str = input("Date (YYYY-MM-DD, press Enter for today): ").strip()
            date = date_str if date_str else None
            
            # Get payment method
            print("\nPayment Methods: Cash, Credit Card, Debit Card, UPI, Other")
            payment_method = input("Payment method (default: Cash): ").strip() or "Cash"
            
            # Add expense
            result = self.manager.add_expense(
                amount=amount,
                category=category,
                description=description,
                date=date,
                payment_method=payment_method
            )
            
            print()
            self.print_separator()
            if result['success']:
                print(f"✅ {result['message']}")
                if result.get('warning'):
                    print(f"\n{result['warning']}")
            else:
                print(f"❌ {result['message']}")
            
        except ValueError:
            print("\n❌ Invalid amount! Please enter a valid number.")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
        
        self.wait_for_enter()
    
    def view_expenses(self):
        """View expenses with filters"""
        self.clear_screen()
        self.print_header("📋 View Expenses")
        
        print("Filter Options:")
        print("1. View all expenses")
        print("2. View by category")
        print("3. View by date range")
        print("4. View recent (last 7 days)")
        print("5. View this month")
        
        choice = input("\nSelect filter (1-5): ").strip()
        
        category = None
        start_date = None
        end_date = None
        limit = None
        
        if choice == "2":
            categories = self.manager.get_categories()
            print("\nCategories:")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat}")
            cat_choice = input("\nSelect category: ").strip()
            if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
                category = categories[int(cat_choice) - 1]
        
        elif choice == "3":
            start_date = input("Start date (YYYY-MM-DD): ").strip()
            end_date = input("End date (YYYY-MM-DD): ").strip()
        
        elif choice == "4":
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        elif choice == "5":
            start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        elif choice == "1":
            limit_str = input("Number of expenses to show (press Enter for all): ").strip()
            limit = int(limit_str) if limit_str.isdigit() else None
        
        # Get expenses
        expenses = self.manager.get_expenses(
            limit=limit,
            category=category,
            start_date=start_date,
            end_date=end_date
        )
        
        # Display expenses
        print()
        self.print_separator()
        
        if not expenses:
            print("No expenses found.")
        else:
            print(f"Found {len(expenses)} expense(s):\n")
            total = 0
            
            for exp in expenses:
                print(f"ID: {exp['id']}")
                print(f"Date: {exp['date']}")
                print(f"Category: {exp['category']}")
                print(f"Amount: ${exp['amount']:.2f}")
                if exp['description']:
                    print(f"Description: {exp['description']}")
                print(f"Payment: {exp['payment_method']}")
                print()
                total += exp['amount']
            
            self.print_separator()
            print(f"Total: ${total:.2f}")
        
        self.wait_for_enter()
    
    def search_expenses(self):
        """Search expenses by keyword"""
        self.clear_screen()
        self.print_header("🔍 Search Expenses")
        
        keyword = input("Enter search keyword: ").strip()
        
        if not keyword:
            print("❌ Please enter a keyword!")
            self.wait_for_enter()
            return
        
        expenses = self.manager.search_expenses(keyword)
        
        print()
        self.print_separator()
        
        if not expenses:
            print(f"No expenses found matching '{keyword}'.")
        else:
            print(f"Found {len(expenses)} expense(s) matching '{keyword}':\n")
            
            for exp in expenses:
                print(f"ID: {exp['id']} | Date: {exp['date']} | "
                      f"Category: {exp['category']} | Amount: ${exp['amount']:.2f}")
                if exp['description']:
                    print(f"  → {exp['description']}")
                print()
        
        self.wait_for_enter()
    
    def edit_expense(self):
        """Edit an existing expense"""
        self.clear_screen()
        self.print_header("✏️  Edit Expense")
        
        try:
            expense_id = int(input("Enter expense ID to edit: ").strip())
            
            # Get current expense details
            expenses = self.manager.get_expenses()
            expense = next((e for e in expenses if e['id'] == expense_id), None)
            
            if not expense:
                print(f"\n❌ Expense with ID {expense_id} not found!")
                self.wait_for_enter()
                return
            
            print(f"\nCurrent details:")
            print(f"Date: {expense['date']}")
            print(f"Category: {expense['category']}")
            print(f"Amount: ${expense['amount']:.2f}")
            print(f"Description: {expense['description']}")
            print(f"Payment: {expense['payment_method']}")
            
            print("\nEnter new values (press Enter to keep current value):")
            
            updates = {}
            
            # New amount
            new_amount = input(f"Amount (${expense['amount']:.2f}): ").strip()
            if new_amount:
                updates['amount'] = float(new_amount)
            
            # New category
            categories = self.manager.get_categories()
            print("\nCategories:", ", ".join(categories))
            new_category = input(f"Category ({expense['category']}): ").strip()
            if new_category and new_category in categories:
                updates['category'] = new_category
            
            # New description
            new_description = input(f"Description ({expense['description']}): ").strip()
            if new_description:
                updates['description'] = new_description
            
            # New date
            new_date = input(f"Date ({expense['date']}): ").strip()
            if new_date:
                updates['date'] = new_date
            
            # Update expense
            if updates:
                result = self.manager.update_expense(expense_id, **updates)
                print()
                self.print_separator()
                if result['success']:
                    print(f"✅ {result['message']}")
                else:
                    print(f"❌ {result['message']}")
            else:
                print("\n⚠️  No changes made.")
        
        except ValueError:
            print("\n❌ Invalid input!")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
        
        self.wait_for_enter()
    
    def delete_expense(self):
        """Delete an expense"""
        self.clear_screen()
        self.print_header("🗑️  Delete Expense")
        
        try:
            expense_id = int(input("Enter expense ID to delete: ").strip())
            
            # Confirm deletion
            confirm = input(f"\n⚠️  Are you sure you want to delete expense #{expense_id}? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                result = self.manager.delete_expense(expense_id)
                print()
                self.print_separator()
                if result['success']:
                    print(f"✅ {result['message']}")
                else:
                    print(f"❌ {result['message']}")
            else:
                print("\n❌ Deletion cancelled.")
        
        except ValueError:
            print("\n❌ Invalid expense ID!")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
        
        self.wait_for_enter()
    
    def view_reports(self):
        """View reports and analytics"""
        self.clear_screen()
        self.print_header("📊 Reports & Analytics")
        
        print("1. Spending Summary (Week)")
        print("2. Spending Summary (Month)")
        print("3. Spending Summary (Year)")
        print("4. Category Breakdown")
        print("5. Trend Analysis")
        print("6. Monthly Prediction")
        print("7. Compare Periods")
        
        choice = input("\nSelect report (1-7): ").strip()
        
        print()
        self.print_separator()
        
        if choice == "1":
            summary = self.analytics.get_spending_summary("week")
            self._display_spending_summary(summary)
        
        elif choice == "2":
            summary = self.analytics.get_spending_summary("month")
            self._display_spending_summary(summary)
        
        elif choice == "3":
            summary = self.analytics.get_spending_summary("year")
            self._display_spending_summary(summary)
        
        elif choice == "4":
            breakdown = self.analytics.get_category_breakdown()
            self._display_category_breakdown(breakdown)
        
        elif choice == "5":
            trend = self.analytics.get_trend_analysis()
            self._display_trend_analysis(trend)
        
        elif choice == "6":
            prediction = self.analytics.predict_monthly_spending()
            self._display_prediction(prediction)
        
        elif choice == "7":
            self._compare_periods()
        
        else:
            print("❌ Invalid choice!")
        
        self.wait_for_enter()
    
    def _display_spending_summary(self, summary):
        """Display spending summary"""
        print(f"\n📊 {summary['period']} Summary")
        print(f"Period: {summary['start_date'] or 'All time'} to {summary['end_date']}")
        print()
        print(f"Total Spent: ${summary['total_spent']:.2f}")
        print(f"Transactions: {summary['transaction_count']}")
        print(f"Average per Transaction: ${summary['avg_per_transaction']:.2f}")
        print(f"Average per Day: ${summary['avg_per_day']:.2f}")
        
        if summary['top_categories']:
            print(f"\nTop Categories:")
            for cat in summary['top_categories']:
                print(f"  • {cat['category']}: ${cat['amount']:.2f} "
                      f"({cat['percentage']:.1f}%) - {cat['count']} transaction(s)")
    
    def _display_category_breakdown(self, breakdown):
        """Display category breakdown"""
        print("\n📊 Category Breakdown (Current Month)")
        print()
        
        if not breakdown:
            print("No data available.")
            return
        
        for cat in breakdown:
            print(f"{cat['category']}:")
            print(f"  Total: ${cat['total']:.2f}")
            print(f"  Percentage: {cat['percentage']:.1f}%")
            print(f"  Transactions: {cat['count']}")
            print(f"  Avg per Transaction: ${cat['avg_per_transaction']:.2f}")
            print()
    
    def _display_trend_analysis(self, trend):
        """Display trend analysis"""
        print("\n📈 Trend Analysis")
        print()
        
        if trend['trend'] == "INSUFFICIENT_DATA":
            print(trend['message'])
            return
        
        print(f"Trend: {trend['trend']}")
        print(f"Average Monthly Spending: ${trend['avg_monthly_spending']:.2f}")
        print(f"Current Month: ${trend['current_month_spending']:.2f}")
        print(f"Month-over-Month Change: {trend['month_over_month_change']:+.1f}%")
        print(f"Spending Consistency: {trend['spending_consistency']}")
        
        print("\nRecent Months:")
        for month in trend['monthly_data']:
            print(f"  {month['month']}: ${month['total']:.2f} ({month['count']} transactions)")
    
    def _display_prediction(self, prediction):
        """Display monthly prediction"""
        print("\n🔮 Monthly Spending Prediction")
        print()
        print(f"Current Spending: ${prediction['current_spending']:.2f}")
        print(f"Days Passed: {prediction['days_passed']}")
        print(f"Days Remaining: {prediction['days_remaining']}")
        print(f"Daily Average: ${prediction['daily_average']:.2f}")
        print()
        print(f"Projected Monthly Total: ${prediction['projected_monthly_total']:.2f}")
        print(f"Last Month Total: ${prediction['last_month_total']:.2f}")
        
        diff = prediction['comparison_with_last_month']
        if diff > 0:
            print(f"Difference: +${diff:.2f} (higher than last month)")
        elif diff < 0:
            print(f"Difference: ${diff:.2f} (lower than last month)")
        else:
            print("Difference: Same as last month")
    
    def _compare_periods(self):
        """Compare two time periods"""
        print("\nCompare Two Periods")
        print()
        
        try:
            print("Period 1:")
            p1_start = input("  Start date (YYYY-MM-DD): ").strip()
            p1_end = input("  End date (YYYY-MM-DD): ").strip()
            
            print("\nPeriod 2:")
            p2_start = input("  Start date (YYYY-MM-DD): ").strip()
            p2_end = input("  End date (YYYY-MM-DD): ").strip()
            
            comparison = self.analytics.compare_periods(p1_start, p1_end, p2_start, p2_end)
            
            print()
            self.print_separator()
            print(f"\nPeriod 1 ({comparison['period1']['start']} to {comparison['period1']['end']}):")
            print(f"  Total: ${comparison['period1']['total']:.2f}")
            print(f"  Transactions: {comparison['period1']['count']}")
            
            print(f"\nPeriod 2 ({comparison['period2']['start']} to {comparison['period2']['end']}):")
            print(f"  Total: ${comparison['period2']['total']:.2f}")
            print(f"  Transactions: {comparison['period2']['count']}")
            
            print(f"\nChange: {comparison['direction']}")
            print(f"  Amount: ${abs(comparison['change_amount']):.2f}")
            print(f"  Percentage: {abs(comparison['change_percentage']):.1f}%")
        
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    
    def view_insights(self):
        """View smart insights"""
        self.clear_screen()
        self.print_header("💡 Smart Insights")
        
        insights = self.analytics.get_spending_insights()
        
        print("Here are your personalized insights:\n")
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}\n")
        
        self.wait_for_enter()
    
    def generate_charts(self):
        """Generate visualization charts"""
        self.clear_screen()
        self.print_header("📈 Generate Charts")
        
        print("1. Category Pie Chart")
        print("2. Category Bar Chart")
        print("3. Monthly Trend")
        print("4. Daily Expenses")
        print("5. Budget vs Actual")
        print("6. Generate All Charts")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        print()
        self.print_separator()
        print()
        
        try:
            if choice == "1":
                filename = self.visualizer.plot_category_pie_chart()
                if filename:
                    print(f"✅ Chart saved: {filename}")
            
            elif choice == "2":
                filename = self.visualizer.plot_category_bar_chart()
                if filename:
                    print(f"✅ Chart saved: {filename}")
            
            elif choice == "3":
                filename = self.visualizer.plot_monthly_trend()
                if filename:
                    print(f"✅ Chart saved: {filename}")
            
            elif choice == "4":
                filename = self.visualizer.plot_daily_expenses()
                if filename:
                    print(f"✅ Chart saved: {filename}")
            
            elif choice == "5":
                filename = self.visualizer.plot_budget_vs_actual()
                if filename:
                    print(f"✅ Chart saved: {filename}")
            
            elif choice == "6":
                charts = self.visualizer.generate_all_charts()
                print(f"\n✅ Generated {len(charts)} chart(s)")
            
            else:
                print("❌ Invalid choice!")
        
        except Exception as e:
            print(f"❌ Error generating chart: {str(e)}")
        
        self.wait_for_enter()
    
    def budget_management(self):
        """Budget management menu"""
        self.clear_screen()
        self.print_header("💰 Budget Management")
        
        print("1. Set/Update Budget")
        print("2. View Budget Status")
        print("3. Remove Budget")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        print()
        self.print_separator()
        
        if choice == "1":
            self._set_budget()
        elif choice == "2":
            self._view_budget_status()
        elif choice == "3":
            print("\n⚠️  Feature coming soon!")
        else:
            print("\n❌ Invalid choice!")
        
        self.wait_for_enter()
    
    def _set_budget(self):
        """Set or update budget"""
        print("\nSet Budget")
        
        categories = self.manager.get_categories()
        print("\nCategories:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
        
        cat_choice = input("\nSelect category: ").strip()
        
        if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
            category = categories[int(cat_choice) - 1]
        elif cat_choice in categories:
            category = cat_choice
        else:
            print("\n❌ Invalid category!")
            return
        
        try:
            limit = float(input("Monthly budget limit ($): ").strip())
            result = self.manager.set_budget(category, limit)
            
            print()
            if result['success']:
                print(f"✅ {result['message']}")
            else:
                print(f"❌ {result['message']}")
        
        except ValueError:
            print("\n❌ Invalid amount!")
    
    def _view_budget_status(self):
        """View budget status"""
        print("\n💰 Budget Status (Current Month)")
        print()
        
        budget_status = self.manager.get_budget_status()
        
        if not budget_status:
            print("No budgets set. Use option 1 to set budgets.")
            return
        
        for budget in budget_status:
            status_icon = {
                "OK": "✅",
                "CAUTION": "⚠️ ",
                "WARNING": "⚠️ ",
                "EXCEEDED": "❌"
            }.get(budget['status'], "")
            
            print(f"{status_icon} {budget['category']}")
            print(f"  Budget: ${budget['limit']:.2f}")
            print(f"  Spent: ${budget['spent']:.2f}")
            print(f"  Remaining: ${budget['remaining']:.2f}")
            print(f"  Usage: {budget['percentage']:.1f}%")
            print()
    
    def manage_categories(self):
        """Manage expense categories"""
        self.clear_screen()
        self.print_header("🏷️  Manage Categories")
        
        print("1. View All Categories")
        print("2. Add New Category")
        
        choice = input("\nSelect option (1-2): ").strip()
        
        print()
        self.print_separator()
        
        if choice == "1":
            categories = self.manager.get_categories()
            print(f"\nTotal Categories: {len(categories)}\n")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat}")
        
        elif choice == "2":
            name = input("\nCategory name: ").strip()
            icon = input("Icon (emoji, optional): ").strip() or "📌"
            
            result = self.manager.add_category(name, icon)
            print()
            if result['success']:
                print(f"✅ {result['message']}")
            else:
                print(f"❌ {result['message']}")
        
        else:
            print("\n❌ Invalid choice!")
        
        self.wait_for_enter()
    
    def run(self):
        """Run the main application loop"""
        while self.running:
            try:
                choice = self.display_main_menu()
                
                if choice == "1":
                    self.add_expense()
                elif choice == "2":
                    self.view_expenses()
                elif choice == "3":
                    self.search_expenses()
                elif choice == "4":
                    self.edit_expense()
                elif choice == "5":
                    self.delete_expense()
                elif choice == "6":
                    self.view_reports()
                elif choice == "7":
                    self.view_insights()
                elif choice == "8":
                    self.generate_charts()
                elif choice == "9":
                    self.budget_management()
                elif choice == "10":
                    self.manage_categories()
                elif choice == "0":
                    self.clear_screen()
                    print("\n👋 Thank you for using Smart Expense Tracker!")
                    print("Your financial data has been saved.\n")
                    self.running = False
                else:
                    print("\n❌ Invalid option! Please try again.")
                    self.wait_for_enter()
            
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user.")
                self.running = False
            except Exception as e:
                print(f"\n❌ Unexpected error: {str(e)}")
                self.wait_for_enter()
        
        # Close database connection
        self.db.close()


def main():
    """Main entry point"""
    try:
        app = ExpenseTrackerCLI()
        app.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

