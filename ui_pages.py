"""
UI Pages Module
Individual page functions for the Smart Expense Tracker Web Interface
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict
import ui_components as ui


def show_dashboard_page(manager, analytics):
    """Display the dashboard page"""
    st.title("📊 Dashboard")
    st.markdown("### Your Financial Overview")
    
    # Get current month data
    now = datetime.now()
    first_day = now.replace(day=1).strftime("%Y-%m-%d")
    today = now.strftime("%Y-%m-%d")
    
    # Summary metrics
    total_month = manager.get_total_spent(start_date=first_day, end_date=today)
    expenses_month = manager.get_expenses(start_date=first_day, end_date=today)
    avg_transaction = total_month / len(expenses_month) if expenses_month else 0
    days_passed = now.day
    
    metrics = [
        {'label': '💵 This Month', 'value': f"${total_month:.2f}"},
        {'label': '📝 Transactions', 'value': len(expenses_month)},
        {'label': '💳 Avg Transaction', 'value': f"${avg_transaction:.2f}"},
        {'label': '📅 Day of Month', 'value': f"{days_passed}"}
    ]
    ui.display_metric_cards(metrics)
    
    st.markdown("---")
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Spending by Category")
        category_data = analytics.get_category_breakdown(first_day, today)
        
        if category_data:
            df = pd.DataFrame(category_data)
            fig = ui.create_pie_chart(df, 'total', 'category')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expenses recorded yet. Start by adding an expense!")
    
    with col2:
        st.subheader("📈 Monthly Trend")
        monthly_data = analytics.db.get_monthly_summary()
        
        if monthly_data:
            df = pd.DataFrame(monthly_data, columns=['Month', 'Total', 'Count'])
            df = df.head(6).iloc[::-1]
            fig = ui.create_line_chart(df, 'Month', 'Total', 'Monthly Spending Pattern')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for trend analysis yet.")
    
    # Recent expenses
    st.markdown("---")
    st.subheader("🕐 Recent Expenses")
    recent_expenses = manager.get_expenses(limit=10)
    ui.display_expenses_table(
        recent_expenses,
        columns=['date', 'category', 'amount', 'description', 'payment_method']
    )
    
    # Budget status
    st.markdown("---")
    st.subheader("💰 Budget Status")
    budget_status = manager.get_budget_status()
    ui.display_budget_progress(budget_status)


def show_add_expense_page(manager):
    """Display the add expense page"""
    st.title("➕ Add New Expense")
    
    categories = manager.get_categories()
    form_data = ui.create_expense_form(
        categories,
        form_key="add_expense_form",
        default_values={'date': datetime.now()}
    )
    
    if form_data:
        result = manager.add_expense(
            amount=form_data['amount'],
            category=form_data['category'],
            description=form_data['description'],
            date=form_data['date'].strftime("%Y-%m-%d"),
            payment_method=form_data['payment_method']
        )
        
        if result['success']:
            ui.show_success_animation(result['message'])
            if result.get('warning'):
                ui.show_warning_message(result['warning'])
        else:
            ui.show_error_message(result['message'])


def show_view_expenses_page(manager):
    """Display the view expenses page"""
    st.title("📋 View Expenses")
    
    # Filters section
    st.subheader("🔍 Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ["All"] + manager.get_categories()
        selected_category = st.selectbox("Category", categories)
    
    with col2:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
    
    with col3:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Get filtered expenses
    category_filter = selected_category if selected_category != "All" else None
    expenses = manager.get_expenses(
        category=category_filter,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )
    
    # Display summary
    st.markdown("---")
    if expenses:
        total = sum(exp['amount'] for exp in expenses)
        avg = total / len(expenses)
        
        metrics = [
            {'label': 'Total Expenses', 'value': len(expenses)},
            {'label': 'Total Amount', 'value': f"${total:.2f}"},
            {'label': 'Average', 'value': f"${avg:.2f}"}
        ]
        ui.display_metric_cards(metrics)
        
        st.markdown("---")
        
        # Searchable table
        df = ui.create_data_table_with_search(
            expenses,
            search_columns=['description', 'category']
        )
        
        if not df.empty:
            # Format amount for display
            df_display = df.copy()
            df_display['amount'] = df_display['amount'].apply(lambda x: f"${x:.2f}")
            st.dataframe(
                df_display[['id', 'date', 'category', 'amount', 'description', 'payment_method']],
                use_container_width=True,
                hide_index=True
            )
        
        # Delete expense section
        st.markdown("---")
        with st.expander("🗑️ Delete Expense"):
            # Show valid ID range
            if df_display is not None and not df_display.empty:
                min_id = df_display['id'].min()
                max_id = df_display['id'].max()
                st.caption(f"💡 Valid IDs in current view: {min_id} to {max_id}")
            
            expense_id = st.number_input("Expense ID", min_value=1, step=1, key="delete_id")
            if st.button("Delete", type="primary"):
                result = manager.delete_expense(expense_id)
                if result['success']:
                    ui.show_success_animation(result['message'])
                    st.rerun()
                else:
                    ui.show_error_message(result['message'])
    else:
        st.info("No expenses found for the selected filters.")


def show_budget_manager_page(manager):
    """Display the budget manager page"""
    st.title("💰 Budget Manager")
    
    tab1, tab2 = st.tabs(["📊 View Budgets", "➕ Set Budget"])
    
    with tab1:
        st.subheader("Current Budgets")
        budget_status = manager.get_budget_status()
        
        if budget_status:
            for budget in budget_status:
                ui.create_budget_expander(budget)
        else:
            st.info("No budgets set yet. Use the 'Set Budget' tab to create one!")
    
    with tab2:
        st.subheader("Set or Update Budget")
        
        with st.form("budget_form"):
            categories = manager.get_categories()
            category = st.selectbox("Category", categories)
            monthly_limit = st.number_input(
                "Monthly Budget Limit ($)",
                min_value=0.01,
                value=500.00,
                step=10.00
            )
            
            submitted = st.form_submit_button("💾 Set Budget", use_container_width=True)
            
            if submitted:
                result = manager.set_budget(category, monthly_limit)
                if result['success']:
                    ui.show_success_animation(result['message'])
                else:
                    ui.show_error_message(result['message'])


def show_analytics_page(analytics):
    """Display the analytics page"""
    st.title("📈 Analytics & Reports")
    
    # Period selector
    period = st.selectbox("Select Period", ["Week", "Month", "Year", "All Time"])
    period_map = {"Week": "week", "Month": "month", "Year": "year", "All Time": "all"}
    
    summary = analytics.get_spending_summary(period_map[period])
    
    # Summary metrics
    st.subheader(f"📊 {summary['period']} Summary")
    ui.display_summary_metrics(summary)
    
    st.markdown("---")
    
    # Top categories
    st.subheader("🏆 Top Spending Categories")
    if summary['top_categories']:
        df = pd.DataFrame(summary['top_categories'])
        
        # Bar chart
        fig = ui.create_bar_chart(df, 'category', 'amount', color_col='percentage')
        st.plotly_chart(fig, use_container_width=True)
        
        # Table
        df_display = df.copy()
        df_display['amount'] = df_display['amount'].apply(lambda x: f"${x:.2f}")
        df_display['percentage'] = df_display['percentage'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No data available for the selected period.")
    
    st.markdown("---")
    
    # Trend Analysis
    st.subheader("📉 Trend Analysis")
    trend = analytics.get_trend_analysis()
    
    if trend['trend'] != "INSUFFICIENT_DATA":
        col1, col2, col3 = st.columns(3)
        
        trend_emoji = "📈" if trend['trend'] == "INCREASING" else "📉" if trend['trend'] == "DECREASING" else "📊"
        
        with col1:
            st.metric("Trend", f"{trend_emoji} {trend['trend']}")
        with col2:
            st.metric("Avg Monthly", f"${trend['avg_monthly_spending']:.2f}")
        with col3:
            change = trend['month_over_month_change']
            st.metric("Month-over-Month", f"{change:+.1f}%", delta=f"{change:.1f}%")
        
        # Monthly data chart
        df = pd.DataFrame(trend['monthly_data'])
        fig = ui.create_line_chart(df, 'month', 'total', 'Monthly Spending Pattern')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"📊 {trend['message']}")
        st.markdown("""
        **💡 Tip:** To enable trend analysis, add expenses from previous months:
        - Run `python3 add_sample_data.py` to add 6 months of sample data
        - Or manually add expenses with dates from previous months
        
        Trend analysis requires at least 2 months of expense data.
        """)
    
    st.markdown("---")
    
    # Monthly Prediction
    st.subheader("🔮 Monthly Prediction")
    prediction = analytics.predict_monthly_spending()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Spending", f"${prediction['current_spending']:.2f}")
    with col2:
        st.metric("Projected Total", f"${prediction['projected_monthly_total']:.2f}")
    with col3:
        diff = prediction['comparison_with_last_month']
        st.metric("vs Last Month", f"${abs(diff):.2f}", delta=f"${diff:.2f}")


def show_insights_page(analytics):
    """Display the insights page"""
    st.title("💡 Smart Insights")
    st.markdown("### Personalized financial insights based on your spending patterns")
    
    insights = analytics.get_spending_insights()
    ui.display_insights(insights)


def show_settings_page(manager, db):
    """Display the settings page"""
    st.title("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["📁 Data Management", "🏷️ Categories", "ℹ️ About"])
    
    with tab1:
        show_data_management_tab(manager)
    
    with tab2:
        show_categories_tab(manager, db)
    
    with tab3:
        show_about_tab()


def show_data_management_tab(manager):
    """Display data management settings"""
    st.subheader("Data Management")
    
    # Export data
    st.markdown("### 📤 Export Data")
    if st.button("Export to CSV"):
        expenses = manager.get_expenses()
        if expenses:
            df = pd.DataFrame(expenses)
            csv = df.to_csv(index=False)
            st.download_button(
                "⬇️ Download CSV",
                csv,
                "expenses.csv",
                "text/csv",
                key='download-csv'
            )
        else:
            st.warning("No data to export")
    
    st.markdown("---")
    
    # Database info
    st.markdown("### 📊 Database Statistics")
    expenses = manager.get_expenses()
    categories = manager.get_categories()
    budgets = manager.db.get_budgets()
    
    metrics = [
        {'label': 'Total Expenses', 'value': len(expenses)},
        {'label': 'Categories', 'value': len(categories)},
        {'label': 'Budgets Set', 'value': len(budgets)}
    ]
    ui.display_metric_cards(metrics)


def show_categories_tab(manager, db):
    """Display category management settings"""
    st.subheader("Manage Categories")
    
    # Show existing categories
    st.markdown("### Current Categories")
    categories = db.get_categories()
    
    for cat in categories:
        st.markdown(f"- {cat['icon']} {cat['name']}")
    
    st.markdown("---")
    
    # Add new category
    st.markdown("### Add New Category")
    with st.form("add_category_form"):
        new_cat_name = st.text_input("Category Name")
        new_cat_icon = st.text_input("Emoji Icon", value="📌")
        
        if st.form_submit_button("➕ Add Category"):
            result = manager.add_category(new_cat_name, new_cat_icon)
            if result['success']:
                ui.show_success_animation(result['message'])
            else:
                ui.show_error_message(result['message'])


def show_about_tab():
    """Display about information"""
    st.subheader("About Smart Expense Tracker")
    st.markdown("""
    ### 💰 Smart Expense Tracker
    
    A powerful and intelligent expense tracking application built with Python.
    
    **Features:**
    - 📊 Real-time dashboard with insights
    - 💰 Budget management with alerts
    - 📈 Advanced analytics and predictions
    - 💡 Smart spending insights
    - 📱 Beautiful web interface
    
    **Technology Stack:**
    - Backend: Python, SQLite
    - Frontend: Streamlit
    - Visualization: Plotly
    - Analytics: Custom algorithms
    
    **Version:** 2.0.0
    
    **GitHub:** [SankalpSTiwari/smart-expense-tracker](https://github.com/SankalpSTiwari/smart-expense-tracker)
    
    ---
    
    Made with ❤️ using Python & Streamlit
    """)

