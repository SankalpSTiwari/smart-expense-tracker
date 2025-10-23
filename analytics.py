"""
Analytics module for Smart Expense Tracker
Provides insights, predictions, and spending analysis
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from database import Database
from collections import defaultdict
import statistics


class Analytics:
    """Provides analytical insights for expenses"""
    
    def __init__(self, db: Database):
        """Initialize analytics with database"""
        self.db = db
    
    def get_spending_summary(self, period: str = "month") -> Dict:
        """
        Get spending summary for a period
        
        Args:
            period: 'week', 'month', 'year', or 'all'
        
        Returns:
            Dictionary with summary statistics
        """
        end_date = datetime.now()
        
        if period == "week":
            start_date = end_date - timedelta(days=7)
            period_name = "This Week"
        elif period == "month":
            start_date = end_date.replace(day=1)
            period_name = "This Month"
        elif period == "year":
            start_date = end_date.replace(month=1, day=1)
            period_name = "This Year"
        else:
            start_date = None
            period_name = "All Time"
        
        start_date_str = start_date.strftime("%Y-%m-%d") if start_date else None
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        total = self.db.get_total_expenses(start_date_str, end_date_str)
        expenses = self.db.get_expenses(start_date=start_date_str, end_date=end_date_str)
        category_summary = self.db.get_category_summary(start_date_str, end_date_str)
        
        # Calculate average per transaction
        avg_per_transaction = total / len(expenses) if expenses else 0
        
        # Calculate daily average
        if start_date:
            days = (end_date - start_date).days + 1
        else:
            if expenses:
                first_expense_date = datetime.strptime(expenses[-1]['date'], "%Y-%m-%d")
                days = (end_date - first_expense_date).days + 1
            else:
                days = 1
        
        avg_per_day = total / days if days > 0 else 0
        
        # Find top categories
        top_categories = []
        for cat in category_summary[:5]:
            percentage = (cat[1] / total * 100) if total > 0 else 0
            top_categories.append({
                "category": cat[0],
                "amount": cat[1],
                "count": cat[2],
                "percentage": percentage
            })
        
        return {
            "period": period_name,
            "total_spent": total,
            "transaction_count": len(expenses),
            "avg_per_transaction": avg_per_transaction,
            "avg_per_day": avg_per_day,
            "top_categories": top_categories,
            "start_date": start_date_str,
            "end_date": end_date_str
        }
    
    def get_category_breakdown(self, start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> List[Dict]:
        """Get detailed breakdown by category"""
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        if not start_date:
            start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        
        category_summary = self.db.get_category_summary(start_date, end_date)
        total = self.db.get_total_expenses(start_date, end_date)
        
        breakdown = []
        for cat in category_summary:
            percentage = (cat[1] / total * 100) if total > 0 else 0
            breakdown.append({
                "category": cat[0],
                "total": cat[1],
                "count": cat[2],
                "percentage": percentage,
                "avg_per_transaction": cat[1] / cat[2] if cat[2] > 0 else 0
            })
        
        return breakdown
    
    def get_trend_analysis(self, months: int = 6) -> Dict:
        """
        Analyze spending trends over recent months
        
        Args:
            months: Number of months to analyze
        
        Returns:
            Dictionary with trend information
        """
        monthly_data = self.db.get_monthly_summary()
        
        if not monthly_data or len(monthly_data) < 2:
            return {
                "trend": "INSUFFICIENT_DATA",
                "message": "Not enough data for trend analysis"
            }
        
        # Get last N months
        recent_months = monthly_data[:min(months, len(monthly_data))]
        amounts = [month[1] for month in recent_months]
        
        # Calculate trend
        avg_spending = statistics.mean(amounts)
        current_month = amounts[0]
        
        # Compare with previous month
        if len(amounts) >= 2:
            prev_month = amounts[1]
            month_change = ((current_month - prev_month) / prev_month * 100) if prev_month > 0 else 0
        else:
            month_change = 0
        
        # Determine trend direction
        if len(amounts) >= 3:
            recent_avg = statistics.mean(amounts[:3])
            older_avg = statistics.mean(amounts[3:]) if len(amounts) > 3 else recent_avg
            
            if recent_avg > older_avg * 1.1:
                trend = "INCREASING"
            elif recent_avg < older_avg * 0.9:
                trend = "DECREASING"
            else:
                trend = "STABLE"
        else:
            trend = "STABLE"
        
        # Calculate standard deviation (spending consistency)
        std_dev = statistics.stdev(amounts) if len(amounts) >= 2 else 0
        
        return {
            "trend": trend,
            "avg_monthly_spending": avg_spending,
            "current_month_spending": current_month,
            "month_over_month_change": month_change,
            "spending_consistency": "HIGH" if std_dev < avg_spending * 0.2 else "MODERATE" if std_dev < avg_spending * 0.4 else "LOW",
            "monthly_data": [
                {
                    "month": month[0],
                    "total": month[1],
                    "count": month[2]
                }
                for month in recent_months
            ]
        }
    
    def predict_monthly_spending(self) -> Dict:
        """
        Predict spending for current month based on current progress
        
        Returns:
            Dictionary with prediction
        """
        now = datetime.now()
        first_day = now.replace(day=1).strftime("%Y-%m-%d")
        today = now.strftime("%Y-%m-%d")
        
        # Get spending so far this month
        spent_so_far = self.db.get_total_expenses(first_day, today)
        
        # Calculate days passed and total days in month
        days_passed = now.day
        last_day = (now.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        total_days = last_day.day
        
        # Simple linear projection
        if days_passed > 0:
            daily_avg = spent_so_far / days_passed
            projected_total = daily_avg * total_days
        else:
            projected_total = 0
        
        # Get last month's spending for comparison
        last_month_start = (now.replace(day=1) - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d")
        last_month_end = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")
        last_month_total = self.db.get_total_expenses(last_month_start, last_month_end)
        
        return {
            "current_spending": spent_so_far,
            "projected_monthly_total": projected_total,
            "days_passed": days_passed,
            "days_remaining": total_days - days_passed,
            "daily_average": daily_avg if days_passed > 0 else 0,
            "last_month_total": last_month_total,
            "comparison_with_last_month": projected_total - last_month_total if last_month_total > 0 else 0
        }
    
    def get_spending_insights(self) -> List[str]:
        """
        Generate smart insights about spending patterns
        
        Returns:
            List of insight messages
        """
        insights = []
        
        # Get current month data
        now = datetime.now()
        first_day = now.replace(day=1).strftime("%Y-%m-%d")
        today = now.strftime("%Y-%m-%d")
        
        # Category insights
        category_breakdown = self.get_category_breakdown(first_day, today)
        if category_breakdown:
            top_category = category_breakdown[0]
            if top_category['percentage'] > 40:
                insights.append(
                    f"💡 {top_category['category']} accounts for {top_category['percentage']:.1f}% "
                    f"of your spending this month. Consider if this aligns with your priorities."
                )
        
        # Trend insights
        trend = self.get_trend_analysis()
        if trend['trend'] == "INCREASING":
            insights.append(
                f"📈 Your spending has been increasing recently. "
                f"Average monthly spending: ${trend['avg_monthly_spending']:.2f}"
            )
        elif trend['trend'] == "DECREASING":
            insights.append(
                f"📉 Great job! Your spending has been decreasing. "
                f"Keep up the good work!"
            )
        
        # Prediction insights
        prediction = self.predict_monthly_spending()
        if prediction['days_passed'] >= 5:
            if prediction['projected_monthly_total'] > prediction['last_month_total'] * 1.2:
                projected = prediction['projected_monthly_total']
                last_month = prediction['last_month_total']
                insights.append(
                    f"⚠️ At the current rate, you're projected to spend ${projected:.2f} this month, which is significantly higher than last month (${last_month:.2f})."
                )
            elif prediction['projected_monthly_total'] < prediction['last_month_total'] * 0.8:
                projected = prediction['projected_monthly_total']
                last_month = prediction['last_month_total']
                insights.append(
                    f"✅ You're on track to spend less this month! Projected: ${projected:.2f} vs Last month: ${last_month:.2f}"
                )
        
        # Weekend vs weekday spending
        expenses = self.db.get_expenses(start_date=first_day, end_date=today)
        weekend_total = 0
        weekday_total = 0
        
        for expense in expenses:
            date_obj = datetime.strptime(expense['date'], "%Y-%m-%d")
            if date_obj.weekday() >= 5:  # Saturday = 5, Sunday = 6
                weekend_total += expense['amount']
            else:
                weekday_total += expense['amount']
        
        total = weekend_total + weekday_total
        if total > 0:
            weekend_percentage = (weekend_total / total) * 100
            if weekend_percentage > 40:
                insights.append(
                    f"🎉 {weekend_percentage:.1f}% of your spending happens on weekends. "
                    f"This might be a good area to monitor."
                )
        
        # Transaction frequency insights
        if len(expenses) > 0:
            days_with_expenses = len(set(exp['date'] for exp in expenses))
            avg_transactions_per_day = len(expenses) / days_with_expenses if days_with_expenses > 0 else 0
            
            if avg_transactions_per_day > 5:
                insights.append(
                    f"📱 You're averaging {avg_transactions_per_day:.1f} transactions per day. "
                    f"Consider consolidating purchases to reduce impulse spending."
                )
        
        if not insights:
            insights.append("📊 Keep tracking your expenses to get personalized insights!")
        
        return insights
    
    def compare_periods(self, period1_start: str, period1_end: str,
                       period2_start: str, period2_end: str) -> Dict:
        """
        Compare spending between two time periods
        
        Returns:
            Dictionary with comparison data
        """
        period1_total = self.db.get_total_expenses(period1_start, period1_end)
        period2_total = self.db.get_total_expenses(period2_start, period2_end)
        
        period1_expenses = self.db.get_expenses(start_date=period1_start, end_date=period1_end)
        period2_expenses = self.db.get_expenses(start_date=period2_start, end_date=period2_end)
        
        change_amount = period2_total - period1_total
        change_percentage = ((period2_total - period1_total) / period1_total * 100) if period1_total > 0 else 0
        
        return {
            "period1": {
                "start": period1_start,
                "end": period1_end,
                "total": period1_total,
                "count": len(period1_expenses)
            },
            "period2": {
                "start": period2_start,
                "end": period2_end,
                "total": period2_total,
                "count": len(period2_expenses)
            },
            "change_amount": change_amount,
            "change_percentage": change_percentage,
            "direction": "INCREASED" if change_amount > 0 else "DECREASED" if change_amount < 0 else "UNCHANGED"
        }

