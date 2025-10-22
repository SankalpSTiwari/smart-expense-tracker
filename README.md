# 💰 Smart Expense Tracker

A powerful and intelligent expense tracking application built with Python that helps you manage your finances with ease. Track expenses, set budgets, analyze spending patterns, and get smart insights about your financial habits.

## ✨ Features

### 📝 Core Features

- **Expense Management**: Add, view, edit, and delete expenses with ease
- **Category Organization**: Organize expenses into customizable categories
- **Multiple Payment Methods**: Track different payment methods (Cash, Credit Card, Debit Card, UPI, etc.)
- **Search Functionality**: Quickly find expenses by keywords
- **Date Filtering**: Filter expenses by date ranges

### 💰 Budget Management

- **Budget Setting**: Set monthly budgets for different categories
- **Real-time Alerts**: Get warnings when approaching or exceeding budget limits
- **Budget Tracking**: Monitor budget usage with percentage indicators
- **Visual Comparison**: Compare budgeted vs actual spending

### 📊 Analytics & Reports

- **Spending Summaries**: View summaries by week, month, year, or custom periods
- **Category Breakdown**: Detailed analysis of spending by category
- **Trend Analysis**: Identify spending trends over time
- **Monthly Predictions**: Project monthly spending based on current patterns
- **Period Comparison**: Compare spending between different time periods

### 💡 Smart Insights

- **Intelligent Analysis**: Get personalized insights about spending patterns
- **Spending Habits**: Identify weekend vs weekday spending patterns
- **Top Categories**: Know where your money goes
- **Transaction Frequency**: Monitor how often you spend
- **Budget Warnings**: Proactive alerts for budget management

### 📈 Visualizations

Generate beautiful charts and graphs:

- Category Pie Charts
- Category Bar Charts
- Monthly Trend Lines
- Daily Expense Charts
- Budget vs Actual Comparison Charts

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the repository**

   ```bash
   cd smart-expense-tracker
   ```

2. **Install required dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 📖 Usage Guide

### Getting Started

1. **Launch the application**

   ```bash
   python main.py
   ```

2. **Main Menu Options**
   - `1` - Add a new expense
   - `2` - View expenses with filters
   - `3` - Search for specific expenses
   - `4` - Edit an existing expense
   - `5` - Delete an expense
   - `6` - View detailed reports and analytics
   - `7` - Get smart insights about your spending
   - `8` - Generate visual charts
   - `9` - Manage budgets
   - `10` - Manage expense categories
   - `0` - Exit the application

### Adding an Expense

1. Select option `1` from the main menu
2. Enter the amount
3. Choose a category from the list
4. Add an optional description
5. Specify the date (or press Enter for today)
6. Select payment method

**Example:**

```
Amount ($): 45.50
Category: Food & Dining
Description: Lunch at restaurant
Date: 2025-10-22
Payment method: Credit Card
```

### Setting Up Budgets

1. Go to Budget Management (option `9`)
2. Select "Set/Update Budget"
3. Choose a category
4. Enter monthly budget limit

**Example:**

```
Category: Food & Dining
Monthly budget limit ($): 500
```

### Viewing Reports

Access the Reports menu (option `6`) to view:

- **Weekly/Monthly/Yearly Summaries**: Overview of spending
- **Category Breakdown**: Detailed category analysis
- **Trend Analysis**: Spending patterns over time
- **Monthly Prediction**: Forecast for current month
- **Period Comparison**: Compare two time periods

### Generating Charts

1. Select option `8` from main menu
2. Choose the type of chart you want
3. Charts are saved in the `charts/` directory
4. Open the PNG files to view your visualizations

## 📁 Project Structure

```
smart-expense-tracker/
│
├── main.py                 # Main CLI interface
├── database.py            # Database operations (SQLite)
├── expense_manager.py     # Expense management logic
├── analytics.py           # Analytics and insights engine
├── visualizations.py      # Chart generation module
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── expenses.db           # SQLite database (created on first run)
└── charts/               # Generated charts (created automatically)
```

## 💾 Data Storage

- All data is stored locally in a SQLite database (`expenses.db`)
- No internet connection required
- Your financial data stays private on your device

## 🎯 Use Cases

### Personal Finance Management

- Track daily expenses
- Monitor spending habits
- Stay within budget limits
- Plan future expenses

### Budget Planning

- Set realistic budgets based on historical data
- Get alerts before overspending
- Compare actual vs planned spending

### Financial Analysis

- Identify spending patterns
- Find areas to cut costs
- Track financial progress over time
- Make data-driven financial decisions

## 🔒 Privacy & Security

- **Local Storage**: All data is stored locally on your device
- **No Cloud Sync**: No data is sent to external servers
- **Complete Privacy**: Your financial information remains private
- **Backup Ready**: Simply backup the `expenses.db` file

## 🛠️ Advanced Features

### Custom Categories

Add your own expense categories to match your lifestyle:

```
Menu → Manage Categories → Add New Category
```

### Date Range Filtering

View expenses for any time period:

```
View Expenses → By date range → Enter start and end dates
```

### Expense Search

Find expenses by description or category:

```
Search Expenses → Enter keyword
```

## 📊 Sample Insights

The Smart Expense Tracker provides insights like:

- 💡 "Food & Dining accounts for 35% of your spending this month"
- 📈 "Your spending has been increasing recently. Average monthly: $1,250"
- ⚠️ "At the current rate, you're projected to spend $1,800 this month"
- 🎉 "40% of your spending happens on weekends"
- ✅ "You're on track to spend less this month!"

## 🤝 Tips for Best Results

1. **Consistent Tracking**: Add expenses regularly for accurate insights
2. **Use Categories**: Properly categorize expenses for better analysis
3. **Set Realistic Budgets**: Base budgets on historical spending data
4. **Review Weekly**: Check your spending summary weekly
5. **Monitor Trends**: Use trend analysis to identify patterns
6. **Act on Insights**: Use the smart insights to improve spending habits

## 🐛 Troubleshooting

### Charts Not Generating

- Ensure matplotlib is installed: `pip install matplotlib`
- Check that the `charts/` directory has write permissions

### Database Errors

- If you encounter database errors, backup and delete `expenses.db`
- The application will create a fresh database on next run

### Display Issues

- For best experience, use a terminal with UTF-8 support
- Emoji support varies by terminal and operating system

## 📝 Future Enhancements

Potential features for future versions:

- Export data to CSV/Excel
- Import expenses from bank statements
- Multiple currency support
- Recurring expenses
- Income tracking
- Savings goals
- Mobile app version
- Web interface

## 📄 License

This project is open source and available for personal and educational use.

## 👨‍💻 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📞 Support

For issues or questions:

- Check the troubleshooting section
- Review the usage guide
- Ensure all dependencies are installed

## 🌟 Acknowledgments

Built with:

- Python 3
- SQLite for data storage
- Matplotlib for visualizations
- Love for good financial habits! 💪

---

**Made with ❤️ for smarter financial management**

Start tracking your expenses today and take control of your finances! 💰📊
