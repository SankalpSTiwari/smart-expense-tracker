"""
Smart Expense Tracker - Web UI
A beautiful web interface for the expense tracker using Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import Database
from expense_manager import ExpenseManager
from analytics import Analytics
import os

# Page configuration
st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .success-message {
        padding: 10px;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        margin: 10px 0;
        border-radius: 5px;
    }
    .warning-message {
        padding: 10px;
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        margin: 10px 0;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = Database()
    st.session_state.manager = ExpenseManager(st.session_state.db)
    st.session_state.analytics = Analytics(st.session_state.db)

db = st.session_state.db
manager = st.session_state.manager
analytics = st.session_state.analytics

# Sidebar navigation
st.sidebar.title("💰 Smart Expense Tracker")
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "➕ Add Expense", "📋 View Expenses", "💰 Budget Manager", 
     "📈 Analytics", "💡 Insights", "⚙️ Settings"]
)

# Helper function to display metrics
def display_metric_card(label, value, delta=None, help_text=None):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.metric(label=label, value=value, delta=delta, help=help_text)

# ==================== DASHBOARD ====================
if page == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.markdown("### Your Financial Overview")
    
    # Get current month data
    now = datetime.now()
    first_day = now.replace(day=1).strftime("%Y-%m-%d")
    today = now.strftime("%Y-%m-%d")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Total spent this month
    total_month = manager.get_total_spent(start_date=first_day, end_date=today)
    with col1:
        st.metric("💵 This Month", f"${total_month:.2f}")
    
    # Transaction count
    expenses_month = manager.get_expenses(start_date=first_day, end_date=today)
    with col2:
        st.metric("📝 Transactions", len(expenses_month))
    
    # Average per transaction
    avg_transaction = total_month / len(expenses_month) if expenses_month else 0
    with col3:
        st.metric("💳 Avg Transaction", f"${avg_transaction:.2f}")
    
    # Days into month
    days_passed = now.day
    with col4:
        st.metric("📅 Day of Month", f"{days_passed}")
    
    st.markdown("---")
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Spending by Category")
        category_data = analytics.get_category_breakdown(first_day, today)
        
        if category_data:
            df = pd.DataFrame(category_data)
            fig = px.pie(
                df, 
                values='total', 
                names='category',
                title='',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expenses recorded yet. Start by adding an expense!")
    
    with col2:
        st.subheader("📈 Monthly Trend")
        monthly_data = db.get_monthly_summary()
        
        if monthly_data:
            df = pd.DataFrame(monthly_data, columns=['Month', 'Total', 'Count'])
            df = df.head(6).iloc[::-1]  # Last 6 months, reversed
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['Month'], 
                y=df['Total'],
                mode='lines+markers',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=10),
                fill='tozeroy',
                fillcolor='rgba(31, 119, 180, 0.2)'
            ))
            fig.update_layout(
                height=400,
                xaxis_title="Month",
                yaxis_title="Amount ($)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for trend analysis yet.")
    
    # Recent expenses
    st.markdown("---")
    st.subheader("🕐 Recent Expenses")
    recent_expenses = manager.get_expenses(limit=10)
    
    if recent_expenses:
        df = pd.DataFrame(recent_expenses)
        df = df[['date', 'category', 'amount', 'description', 'payment_method']]
        df['amount'] = df['amount'].apply(lambda x: f"${x:.2f}")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No expenses recorded yet.")
    
    # Budget status
    st.markdown("---")
    st.subheader("💰 Budget Status")
    budget_status = manager.get_budget_status()
    
    if budget_status:
        for budget in budget_status:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                percentage = budget['percentage']
                color = "🟢" if percentage < 75 else "🟡" if percentage < 90 else "🔴"
                
                st.markdown(f"**{color} {budget['category']}**")
                st.progress(min(percentage / 100, 1.0))
                st.caption(f"${budget['spent']:.2f} of ${budget['limit']:.2f} ({percentage:.1f}%)")
            
            with col2:
                remaining = budget['remaining']
                if remaining > 0:
                    st.metric("Remaining", f"${remaining:.2f}")
                else:
                    st.metric("Over", f"${abs(remaining):.2f}", delta=f"${abs(remaining):.2f}")
    else:
        st.info("No budgets set. Go to Budget Manager to set your budgets!")

# ==================== ADD EXPENSE ====================
elif page == "➕ Add Expense":
    st.title("➕ Add New Expense")
    
    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input("Amount ($)", min_value=0.01, value=10.00, step=0.01)
            categories = manager.get_categories()
            category = st.selectbox("Category", categories)
            date = st.date_input("Date", value=datetime.now())
        
        with col2:
            description = st.text_input("Description")
            payment_method = st.selectbox(
                "Payment Method",
                ["Cash", "Credit Card", "Debit Card", "UPI", "Bank Transfer", "Other"]
            )
        
        submitted = st.form_submit_button("💾 Add Expense", use_container_width=True)
        
        if submitted:
            result = manager.add_expense(
                amount=amount,
                category=category,
                description=description,
                date=date.strftime("%Y-%m-%d"),
                payment_method=payment_method
            )
            
            if result['success']:
                st.success(f"✅ {result['message']}")
                if result.get('warning'):
                    st.warning(result['warning'])
                st.balloons()
            else:
                st.error(f"❌ {result['message']}")

# ==================== VIEW EXPENSES ====================
elif page == "📋 View Expenses":
    st.title("📋 View Expenses")
    
    # Filters
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
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Expenses", len(expenses))
        with col2:
            st.metric("Total Amount", f"${total:.2f}")
        with col3:
            avg = total / len(expenses)
            st.metric("Average", f"${avg:.2f}")
        
        st.markdown("---")
        
        # Create DataFrame
        df = pd.DataFrame(expenses)
        df['amount'] = df['amount'].apply(lambda x: f"${x:.2f}")
        
        # Display with search
        search = st.text_input("🔍 Search in description or category")
        if search:
            mask = df['description'].str.contains(search, case=False, na=False) | \
                   df['category'].str.contains(search, case=False, na=False)
            df = df[mask]
        
        st.dataframe(
            df[['id', 'date', 'category', 'amount', 'description', 'payment_method']],
            use_container_width=True,
            hide_index=True
        )
        
        # Delete expense
        st.markdown("---")
        expense_id = st.number_input("Delete Expense ID", min_value=1, step=1)
        if st.button("🗑️ Delete Expense"):
            result = manager.delete_expense(expense_id)
            if result['success']:
                st.success(result['message'])
                st.rerun()
            else:
                st.error(result['message'])
    else:
        st.info("No expenses found for the selected filters.")

# ==================== BUDGET MANAGER ====================
elif page == "💰 Budget Manager":
    st.title("💰 Budget Manager")
    
    tab1, tab2 = st.tabs(["📊 View Budgets", "➕ Set Budget"])
    
    with tab1:
        st.subheader("Current Budgets")
        budget_status = manager.get_budget_status()
        
        if budget_status:
            for budget in budget_status:
                with st.expander(f"{budget['category']} - ${budget['spent']:.2f} / ${budget['limit']:.2f}"):
                    percentage = budget['percentage']
                    
                    # Progress bar
                    st.progress(min(percentage / 100, 1.0))
                    
                    # Status
                    if budget['status'] == "EXCEEDED":
                        st.error(f"⚠️ Budget exceeded by ${abs(budget['remaining']):.2f}!")
                    elif budget['status'] == "WARNING":
                        st.warning(f"⚠️ {percentage:.1f}% of budget used")
                    elif budget['status'] == "CAUTION":
                        st.info(f"📊 {percentage:.1f}% of budget used")
                    else:
                        st.success(f"✅ {percentage:.1f}% of budget used")
                    
                    # Details
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Budget", f"${budget['limit']:.2f}")
                    with col2:
                        st.metric("Spent", f"${budget['spent']:.2f}")
                    with col3:
                        st.metric("Remaining", f"${budget['remaining']:.2f}")
        else:
            st.info("No budgets set yet. Use the 'Set Budget' tab to create one!")
    
    with tab2:
        st.subheader("Set or Update Budget")
        
        with st.form("budget_form"):
            categories = manager.get_categories()
            category = st.selectbox("Category", categories)
            monthly_limit = st.number_input("Monthly Budget Limit ($)", min_value=0.01, value=500.00, step=10.00)
            
            submitted = st.form_submit_button("💾 Set Budget")
            
            if submitted:
                result = manager.set_budget(category, monthly_limit)
                if result['success']:
                    st.success(result['message'])
                else:
                    st.error(result['message'])

# ==================== ANALYTICS ====================
elif page == "📈 Analytics":
    st.title("📈 Analytics & Reports")
    
    # Period selector
    period = st.selectbox("Select Period", ["Week", "Month", "Year", "All Time"])
    period_map = {"Week": "week", "Month": "month", "Year": "year", "All Time": "all"}
    
    summary = analytics.get_spending_summary(period_map[period])
    
    # Summary metrics
    st.subheader(f"📊 {summary['period']} Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Spent", f"${summary['total_spent']:.2f}")
    with col2:
        st.metric("Transactions", summary['transaction_count'])
    with col3:
        st.metric("Avg/Transaction", f"${summary['avg_per_transaction']:.2f}")
    with col4:
        st.metric("Avg/Day", f"${summary['avg_per_day']:.2f}")
    
    st.markdown("---")
    
    # Top categories
    st.subheader("🏆 Top Spending Categories")
    if summary['top_categories']:
        df = pd.DataFrame(summary['top_categories'])
        
        fig = px.bar(
            df,
            x='category',
            y='amount',
            color='percentage',
            text='amount',
            title='',
            color_continuous_scale='Blues'
        )
        fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
        fig.update_layout(height=400, xaxis_title="Category", yaxis_title="Amount ($)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Table
        df['amount'] = df['amount'].apply(lambda x: f"${x:.2f}")
        df['percentage'] = df['percentage'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No data available for the selected period.")
    
    st.markdown("---")
    
    # Trend Analysis
    st.subheader("📉 Trend Analysis")
    trend = analytics.get_trend_analysis()
    
    if trend['trend'] != "INSUFFICIENT_DATA":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            trend_emoji = "📈" if trend['trend'] == "INCREASING" else "📉" if trend['trend'] == "DECREASING" else "📊"
            st.metric("Trend", f"{trend_emoji} {trend['trend']}")
        
        with col2:
            st.metric("Avg Monthly", f"${trend['avg_monthly_spending']:.2f}")
        
        with col3:
            change = trend['month_over_month_change']
            st.metric("Month-over-Month", f"{change:+.1f}%", delta=f"{change:.1f}%")
        
        # Monthly data chart
        df = pd.DataFrame(trend['monthly_data'])
        fig = px.line(
            df,
            x='month',
            y='total',
            markers=True,
            title='Monthly Spending Pattern'
        )
        fig.update_layout(height=400, xaxis_title="Month", yaxis_title="Amount ($)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(trend['message'])
    
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

# ==================== INSIGHTS ====================
elif page == "💡 Insights":
    st.title("💡 Smart Insights")
    st.markdown("### Personalized financial insights based on your spending patterns")
    
    insights = analytics.get_spending_insights()
    
    for i, insight in enumerate(insights, 1):
        if "⚠️" in insight or "🚨" in insight:
            st.warning(insight)
        elif "✅" in insight or "📉" in insight:
            st.success(insight)
        else:
            st.info(insight)
        st.markdown("")

# ==================== SETTINGS ====================
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["📁 Data Management", "🏷️ Categories", "ℹ️ About"])
    
    with tab1:
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
        budgets = db.get_budgets()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Expenses", len(expenses))
        with col2:
            st.metric("Categories", len(categories))
        with col3:
            st.metric("Budgets Set", len(budgets))
    
    with tab2:
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
                    st.success(result['message'])
                else:
                    st.error(result['message'])
    
    with tab3:
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
        
        **Version:** 1.0.0
        
        **GitHub:** [SankalpSTiwari/smart-expense-tracker](https://github.com/SankalpSTiwari/smart-expense-tracker)
        
        ---
        
        Made with ❤️ using Python & Streamlit
        """)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("💰 Smart Expense Tracker v1.0")

