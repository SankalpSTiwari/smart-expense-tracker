"""
Visualization module for Smart Expense Tracker
Creates charts and graphs for expense data
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database import Database
import os


class Visualizer:
    """Creates visualizations for expense data"""
    
    def __init__(self, db: Database):
        """Initialize visualizer with database"""
        self.db = db
        self.output_dir = "charts"
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def plot_category_pie_chart(self, start_date: Optional[str] = None,
                                end_date: Optional[str] = None,
                                save: bool = True) -> str:
        """
        Create a pie chart of expenses by category
        
        Returns:
            Path to saved chart file
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        if not start_date:
            start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        
        category_summary = self.db.get_category_summary(start_date, end_date)
        
        if not category_summary:
            print("No data available for the selected period.")
            return ""
        
        # Prepare data
        categories = [cat[0] for cat in category_summary]
        amounts = [cat[1] for cat in category_summary]
        
        # Create figure
        plt.figure(figsize=(10, 8))
        colors = plt.cm.Set3(range(len(categories)))
        
        # Create pie chart
        wedges, texts, autotexts = plt.pie(
            amounts,
            labels=categories,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        
        # Beautify
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        plt.title(f'Expense Breakdown by Category\n{start_date} to {end_date}', 
                 fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        if save:
            filename = os.path.join(self.output_dir, 'category_pie_chart.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            return filename
        else:
            plt.show()
            return ""
    
    def plot_category_bar_chart(self, start_date: Optional[str] = None,
                               end_date: Optional[str] = None,
                               save: bool = True) -> str:
        """
        Create a bar chart of expenses by category
        
        Returns:
            Path to saved chart file
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        if not start_date:
            start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        
        category_summary = self.db.get_category_summary(start_date, end_date)
        
        if not category_summary:
            print("No data available for the selected period.")
            return ""
        
        # Prepare data
        categories = [cat[0] for cat in category_summary]
        amounts = [cat[1] for cat in category_summary]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create bar chart
        bars = ax.bar(categories, amounts, color='skyblue', edgecolor='navy', alpha=0.7)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:.2f}',
                   ha='center', va='bottom', fontsize=9)
        
        # Beautify
        ax.set_xlabel('Category', fontsize=12, fontweight='bold')
        ax.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
        ax.set_title(f'Expenses by Category\n{start_date} to {end_date}', 
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        if save:
            filename = os.path.join(self.output_dir, 'category_bar_chart.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            return filename
        else:
            plt.show()
            return ""
    
    def plot_monthly_trend(self, months: int = 6, save: bool = True) -> str:
        """
        Create a line chart showing monthly spending trend
        
        Returns:
            Path to saved chart file
        """
        monthly_data = self.db.get_monthly_summary()
        
        if not monthly_data:
            print("No data available.")
            return ""
        
        # Get last N months
        recent_months = list(reversed(monthly_data[:min(months, len(monthly_data))]))
        
        # Prepare data
        months_labels = [month[0] for month in recent_months]
        amounts = [month[1] for month in recent_months]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create line chart
        ax.plot(months_labels, amounts, marker='o', linewidth=2, 
               markersize=8, color='darkblue', markerfacecolor='lightblue')
        
        # Add value labels
        for i, (month, amount) in enumerate(zip(months_labels, amounts)):
            ax.text(i, amount, f'${amount:.2f}', 
                   ha='center', va='bottom', fontsize=9)
        
        # Beautify
        ax.set_xlabel('Month', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Spending ($)', fontsize=12, fontweight='bold')
        ax.set_title('Monthly Spending Trend', fontsize=14, fontweight='bold', pad=20)
        
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        if save:
            filename = os.path.join(self.output_dir, 'monthly_trend.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            return filename
        else:
            plt.show()
            return ""
    
    def plot_daily_expenses(self, days: int = 30, save: bool = True) -> str:
        """
        Create a chart showing daily expenses
        
        Returns:
            Path to saved chart file
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        expenses = self.db.get_expenses(start_date=start_date_str, end_date=end_date_str)
        
        if not expenses:
            print("No data available for the selected period.")
            return ""
        
        # Aggregate by date
        daily_totals = {}
        for expense in expenses:
            date = expense['date']
            daily_totals[date] = daily_totals.get(date, 0) + expense['amount']
        
        # Sort by date
        sorted_dates = sorted(daily_totals.keys())
        amounts = [daily_totals[date] for date in sorted_dates]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Convert dates to datetime objects for better formatting
        date_objects = [datetime.strptime(d, "%Y-%m-%d") for d in sorted_dates]
        
        # Create bar chart
        ax.bar(date_objects, amounts, color='coral', edgecolor='darkred', alpha=0.7)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days // 15)))
        
        # Beautify
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
        ax.set_title(f'Daily Expenses (Last {days} Days)', 
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        if save:
            filename = os.path.join(self.output_dir, 'daily_expenses.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            return filename
        else:
            plt.show()
            return ""
    
    def plot_budget_vs_actual(self, save: bool = True) -> str:
        """
        Create a comparison chart of budget vs actual spending
        
        Returns:
            Path to saved chart file
        """
        budgets = self.db.get_budgets()
        
        if not budgets:
            print("No budgets set.")
            return ""
        
        # Get current month spending
        now = datetime.now()
        first_day = now.replace(day=1).strftime("%Y-%m-%d")
        today = now.strftime("%Y-%m-%d")
        
        categories = []
        budget_amounts = []
        actual_amounts = []
        
        for budget in budgets:
            category = budget['category']
            budget_limit = budget['monthly_limit']
            actual = self.db.get_total_expenses(
                category=category,
                start_date=first_day,
                end_date=today
            )
            
            categories.append(category)
            budget_amounts.append(budget_limit)
            actual_amounts.append(actual)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = range(len(categories))
        width = 0.35
        
        # Create grouped bar chart
        bars1 = ax.bar([i - width/2 for i in x], budget_amounts, width, 
                       label='Budget', color='lightgreen', edgecolor='darkgreen', alpha=0.7)
        bars2 = ax.bar([i + width/2 for i in x], actual_amounts, width,
                       label='Actual', color='lightcoral', edgecolor='darkred', alpha=0.7)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${height:.0f}',
                       ha='center', va='bottom', fontsize=8)
        
        # Beautify
        ax.set_xlabel('Category', fontsize=12, fontweight='bold')
        ax.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
        ax.set_title('Budget vs Actual Spending (Current Month)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()
        
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        if save:
            filename = os.path.join(self.output_dir, 'budget_vs_actual.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            return filename
        else:
            plt.show()
            return ""
    
    def generate_all_charts(self) -> List[str]:
        """
        Generate all available charts
        
        Returns:
            List of paths to saved chart files
        """
        print("Generating charts...")
        charts = []
        
        print("  Creating category pie chart...")
        chart = self.plot_category_pie_chart()
        if chart:
            charts.append(chart)
        
        print("  Creating category bar chart...")
        chart = self.plot_category_bar_chart()
        if chart:
            charts.append(chart)
        
        print("  Creating monthly trend chart...")
        chart = self.plot_monthly_trend()
        if chart:
            charts.append(chart)
        
        print("  Creating daily expenses chart...")
        chart = self.plot_daily_expenses()
        if chart:
            charts.append(chart)
        
        print("  Creating budget vs actual chart...")
        chart = self.plot_budget_vs_actual()
        if chart:
            charts.append(chart)
        
        print(f"\n✓ Generated {len(charts)} chart(s) in '{self.output_dir}' directory")
        
        return charts

