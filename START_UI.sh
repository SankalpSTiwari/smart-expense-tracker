#!/bin/bash
# Start the Smart Expense Tracker Web UI

echo "🚀 Starting Smart Expense Tracker Web UI..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$(dirname "$0")"

streamlit run app.py

echo ""
echo "👋 Thanks for using Smart Expense Tracker!"

