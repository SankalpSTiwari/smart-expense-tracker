"""
UI Components Module
Reusable UI components for the Smart Expense Tracker Web Interface
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Optional


def apply_custom_css():
    """Apply custom CSS styling to the app"""
    st.markdown("""
        <style>
        /* Main container */
        .main {
            padding: 0rem 1rem;
        }
        
        /* Metrics styling - works in both light and dark mode */
        .stMetric {
            background-color: rgba(28, 131, 225, 0.1);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(28, 131, 225, 0.2);
        }
        
        /* Ensure metric labels are visible */
        .stMetric label {
            color: inherit !important;
            font-weight: 600 !important;
        }
        
        /* Ensure metric values are visible */
        .stMetric [data-testid="stMetricValue"] {
            color: inherit !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
        }
        
        /* Metric delta */
        .stMetric [data-testid="stMetricDelta"] {
            color: inherit !important;
        }
        
        /* Success message */
        .success-message {
            padding: 10px;
            background-color: rgba(40, 167, 69, 0.1);
            border-left: 5px solid #28a745;
            margin: 10px 0;
            border-radius: 5px;
            color: inherit;
        }
        
        /* Warning message */
        .warning-message {
            padding: 10px;
            background-color: rgba(255, 193, 7, 0.1);
            border-left: 5px solid #ffc107;
            margin: 10px 0;
            border-radius: 5px;
            color: inherit;
        }
        
        /* Dark mode specific adjustments */
        @media (prefers-color-scheme: dark) {
            .stMetric {
                background-color: rgba(28, 131, 225, 0.15);
                border: 1px solid rgba(28, 131, 225, 0.3);
            }
        }
        </style>
        """, unsafe_allow_html=True)


def display_metric_cards(metrics: List[Dict[str, any]]):
    """
    Display a row of metric cards
    
    Args:
        metrics: List of dicts with 'label', 'value', 'delta', 'help'
    """
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        with col:
            st.metric(
                label=metric.get('label', ''),
                value=metric.get('value', ''),
                delta=metric.get('delta'),
                help=metric.get('help')
            )


def create_pie_chart(data: pd.DataFrame, values_col: str, names_col: str, 
                     title: str = '', height: int = 400) -> go.Figure:
    """
    Create an interactive pie chart
    
    Args:
        data: DataFrame with the data
        values_col: Column name for values
        names_col: Column name for labels
        title: Chart title
        height: Chart height in pixels
    
    Returns:
        Plotly figure object
    """
    fig = px.pie(
        data, 
        values=values_col, 
        names=names_col,
        title=title,
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=height)
    return fig


def create_line_chart(data: pd.DataFrame, x_col: str, y_col: str, 
                      title: str = '', height: int = 400) -> go.Figure:
    """
    Create an interactive line chart with area fill
    
    Args:
        data: DataFrame with the data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Chart title
        height: Chart height in pixels
    
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data[x_col], 
        y=data[y_col],
        mode='lines+markers',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=10),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title=x_col,
        yaxis_title=y_col,
        hovermode='x unified'
    )
    return fig


def create_bar_chart(data: pd.DataFrame, x_col: str, y_col: str, 
                     title: str = '', height: int = 400, 
                     color_col: Optional[str] = None) -> go.Figure:
    """
    Create an interactive bar chart
    
    Args:
        data: DataFrame with the data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Chart title
        height: Chart height in pixels
        color_col: Optional column for color mapping
    
    Returns:
        Plotly figure object
    """
    fig = px.bar(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        text=y_col,
        title=title,
        color_continuous_scale='Blues' if color_col else None
    )
    fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
    fig.update_layout(height=height, xaxis_title=x_col, yaxis_title=y_col)
    return fig


def display_budget_progress(budget_status: List[Dict]):
    """
    Display budget progress bars with status indicators
    
    Args:
        budget_status: List of budget status dictionaries
    """
    if not budget_status:
        st.info("No budgets set. Go to Budget Manager to set your budgets!")
        return
    
    for budget in budget_status:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            percentage = budget['percentage']
            
            # Choose emoji based on status
            if percentage < 75:
                color = "🟢"
            elif percentage < 90:
                color = "🟡"
            else:
                color = "🔴"
            
            st.markdown(f"**{color} {budget['category']}**")
            st.progress(min(percentage / 100, 1.0))
            st.caption(f"${budget['spent']:.2f} of ${budget['limit']:.2f} ({percentage:.1f}%)")
        
        with col2:
            remaining = budget['remaining']
            if remaining > 0:
                st.metric("Remaining", f"${remaining:.2f}")
            else:
                st.metric("Over", f"${abs(remaining):.2f}", delta=f"-${abs(remaining):.2f}")


def display_expenses_table(expenses: List[Dict], columns: List[str] = None):
    """
    Display expenses in a formatted table
    
    Args:
        expenses: List of expense dictionaries
        columns: Optional list of columns to display
    """
    if not expenses:
        st.info("No expenses found.")
        return
    
    df = pd.DataFrame(expenses)
    
    # Format amount column
    if 'amount' in df.columns:
        df['amount'] = df['amount'].apply(lambda x: f"${x:.2f}")
    
    # Select columns if specified
    if columns:
        df = df[columns]
    
    st.dataframe(df, use_container_width=True, hide_index=True)


def create_expense_form(categories: List[str], 
                       form_key: str = "expense_form",
                       default_values: Dict = None) -> Optional[Dict]:
    """
    Create a form for adding/editing expenses
    
    Args:
        categories: List of available categories
        form_key: Unique key for the form
        default_values: Optional dict with default values for editing
    
    Returns:
        Dict with form data if submitted, None otherwise
    """
    defaults = default_values or {}
    
    with st.form(form_key, clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input(
                "Amount ($)", 
                min_value=0.01, 
                value=defaults.get('amount', 10.00), 
                step=0.01
            )
            category = st.selectbox(
                "Category", 
                categories,
                index=categories.index(defaults.get('category', categories[0])) if defaults.get('category') in categories else 0
            )
            date = st.date_input(
                "Date", 
                value=defaults.get('date')
            )
        
        with col2:
            description = st.text_input(
                "Description",
                value=defaults.get('description', '')
            )
            payment_method = st.selectbox(
                "Payment Method",
                ["Cash", "Credit Card", "Debit Card", "UPI", "Bank Transfer", "Other"],
                index=0
            )
        
        submitted = st.form_submit_button("💾 Save Expense", use_container_width=True)
        
        if submitted:
            return {
                'amount': amount,
                'category': category,
                'description': description,
                'date': date,
                'payment_method': payment_method
            }
    
    return None


def display_insights(insights: List[str]):
    """
    Display smart insights with appropriate formatting
    
    Args:
        insights: List of insight messages
    """
    if not insights:
        st.info("No insights available yet. Add more expenses to get personalized insights!")
        return
    
    for insight in insights:
        # Choose message type based on content
        if "⚠️" in insight or "🚨" in insight:
            st.warning(insight)
        elif "✅" in insight or "📉" in insight:
            st.success(insight)
        else:
            st.info(insight)
        st.markdown("")


def create_budget_expander(budget: Dict):
    """
    Create an expandable section for budget details
    
    Args:
        budget: Budget status dictionary
    """
    percentage = budget['percentage']
    
    with st.expander(f"{budget['category']} - ${budget['spent']:.2f} / ${budget['limit']:.2f}"):
        # Progress bar
        st.progress(min(percentage / 100, 1.0))
        
        # Status message
        if budget['status'] == "EXCEEDED":
            st.error(f"⚠️ Budget exceeded by ${abs(budget['remaining']):.2f}!")
        elif budget['status'] == "WARNING":
            st.warning(f"⚠️ {percentage:.1f}% of budget used")
        elif budget['status'] == "CAUTION":
            st.info(f"📊 {percentage:.1f}% of budget used")
        else:
            st.success(f"✅ {percentage:.1f}% of budget used")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Budget", f"${budget['limit']:.2f}")
        with col2:
            st.metric("Spent", f"${budget['spent']:.2f}")
        with col3:
            st.metric("Remaining", f"${budget['remaining']:.2f}")


def display_summary_metrics(summary: Dict):
    """
    Display summary metrics in a formatted way
    
    Args:
        summary: Summary dictionary with metrics
    """
    metrics = [
        {
            'label': 'Total Spent',
            'value': f"${summary['total_spent']:.2f}",
            'help': f"For period: {summary['period']}"
        },
        {
            'label': 'Transactions',
            'value': summary['transaction_count']
        },
        {
            'label': 'Avg/Transaction',
            'value': f"${summary['avg_per_transaction']:.2f}"
        },
        {
            'label': 'Avg/Day',
            'value': f"${summary['avg_per_day']:.2f}"
        }
    ]
    
    display_metric_cards(metrics)


def create_filter_sidebar(categories: List[str]) -> Dict:
    """
    Create a sidebar with filters
    
    Args:
        categories: List of available categories
    
    Returns:
        Dict with filter selections
    """
    with st.sidebar:
        st.subheader("🔍 Filters")
        
        selected_category = st.selectbox("Category", ["All"] + categories)
        
        date_range = st.date_input(
            "Date Range",
            value=[],
            max_value=None
        )
        
        return {
            'category': selected_category if selected_category != "All" else None,
            'date_range': date_range
        }


def show_success_animation(message: str = "Success!"):
    """
    Show success message with animation
    
    Args:
        message: Success message to display
    """
    st.success(message)
    st.balloons()


def show_error_message(message: str):
    """
    Show error message
    
    Args:
        message: Error message to display
    """
    st.error(f"❌ {message}")


def show_warning_message(message: str):
    """
    Show warning message
    
    Args:
        message: Warning message to display
    """
    st.warning(f"⚠️ {message}")


def create_data_table_with_search(data: List[Dict], 
                                   search_columns: List[str] = None) -> pd.DataFrame:
    """
    Create a searchable data table
    
    Args:
        data: List of data dictionaries
        search_columns: Columns to search in
    
    Returns:
        Filtered DataFrame
    """
    df = pd.DataFrame(data)
    
    if df.empty:
        return df
    
    # Search box
    search = st.text_input("🔍 Search", key="table_search")
    
    if search and search_columns:
        # Create search mask
        mask = pd.Series([False] * len(df))
        for col in search_columns:
            if col in df.columns:
                mask |= df[col].astype(str).str.contains(search, case=False, na=False)
        df = df[mask]
    
    return df

