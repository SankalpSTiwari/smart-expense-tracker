"""
Smart Expense Tracker - Web UI (Refactored)
Clean, modular architecture with separated concerns
"""

import streamlit as st
from database import Database
from expense_manager import ExpenseManager
from analytics import Analytics
import ui_components as ui
import ui_pages as pages


# ==================== PAGE CONFIGURATION ====================

def configure_page():
    """Configure page settings and styling"""
    st.set_page_config(
        page_title="Smart Expense Tracker",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    ui.apply_custom_css()


# ==================== SESSION STATE ====================

def initialize_session_state():
    """Initialize session state variables"""
    if 'db' not in st.session_state:
        st.session_state.db = Database()
        st.session_state.manager = ExpenseManager(st.session_state.db)
        st.session_state.analytics = Analytics(st.session_state.db)


def get_session_objects():
    """Get database, manager, and analytics from session state"""
    return (
        st.session_state.db,
        st.session_state.manager,
        st.session_state.analytics
    )


# ==================== NAVIGATION ====================

def render_sidebar():
    """Render sidebar navigation"""
    st.sidebar.title("💰 Smart Expense Tracker")
    
    page = st.sidebar.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "➕ Add Expense",
            "📋 View Expenses",
            "💰 Budget Manager",
            "📈 Analytics",
            "💡 Insights",
            "⚙️ Settings"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("💰 Smart Expense Tracker v2.0")
    
    return page


# ==================== PAGE ROUTING ====================

def route_to_page(page: str, db, manager, analytics):
    """Route to the selected page"""
    
    page_map = {
        "📊 Dashboard": lambda: pages.show_dashboard_page(manager, analytics),
        "➕ Add Expense": lambda: pages.show_add_expense_page(manager),
        "📋 View Expenses": lambda: pages.show_view_expenses_page(manager),
        "💰 Budget Manager": lambda: pages.show_budget_manager_page(manager),
        "📈 Analytics": lambda: pages.show_analytics_page(analytics),
        "💡 Insights": lambda: pages.show_insights_page(analytics),
        "⚙️ Settings": lambda: pages.show_settings_page(manager, db)
    }
    
    # Execute the page function
    if page in page_map:
        page_map[page]()
    else:
        st.error(f"Page '{page}' not found!")


# ==================== MAIN APPLICATION ====================

def main():
    """Main application entry point"""
    
    # Configuration
    configure_page()
    
    # Initialize session state
    initialize_session_state()
    
    # Get session objects
    db, manager, analytics = get_session_objects()
    
    # Render navigation sidebar
    selected_page = render_sidebar()
    
    # Route to selected page
    route_to_page(selected_page, db, manager, analytics)


# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    main()

