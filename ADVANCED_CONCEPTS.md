# 🎓 Advanced Database Concepts Explained

## Table of Contents

1. [Connection Pooling](#connection-pooling)
2. [executemany()](#executemany)
3. [Parameterized Queries & SQL Injection](#parameterized-queries)

---

## 1️⃣ Connection Pooling

### What is it?

**Connection Pooling** is a technique where you maintain a "pool" of reusable database connections instead of creating a new connection for each operation.

### Visual Diagram

```
❌ WITHOUT Connection Pooling:
─────────────────────────────
Request 1:  Create → Use → Close  ⏱️  100ms
Request 2:  Create → Use → Close  ⏱️  100ms
Request 3:  Create → Use → Close  ⏱️  100ms
Total: 300ms

✅ WITH Connection Pooling:
──────────────────────────
Initialize: Create pool of 3 connections  ⏱️  100ms

Request 1:  Borrow conn1 → Use → Return  ⏱️  10ms
Request 2:  Borrow conn2 → Use → Return  ⏱️  10ms
Request 3:  Borrow conn3 → Use → Return  ⏱️  10ms
Total: 130ms (2.3x faster!)
```

### How It Works

```python
# Traditional approach (what we use now)
def add_expense():
    conn = sqlite3.connect('expenses.db')  # Create connection
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses ...")
    conn.commit()
    conn.close()  # Close connection

# Connection pooling approach
pool = ConnectionPool(size=5)  # Create 5 connections once

def add_expense():
    conn = pool.get_connection()  # Get from pool (fast!)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses ...")
    conn.commit()
    pool.release(conn)  # Return to pool (don't close!)
```

### Benefits

1. **⚡ Performance**: Creating connections is slow (especially for remote databases)
2. **💾 Resource Management**: Limit max concurrent connections
3. **🔄 Reusability**: Connections are expensive objects
4. **📊 Monitoring**: Track connection usage

### When to Use

✅ **USE Connection Pooling:**

- Web applications (Django, Flask, FastAPI)
- API servers handling many requests
- Multi-threaded applications
- Database servers (MySQL, PostgreSQL)
- High-traffic applications

❌ **DON'T USE Connection Pooling:**

- Single-user desktop apps (like our Expense Tracker!)
- Command-line scripts
- Single-threaded applications
- Simple automation scripts
- SQLite with one user

### Performance Impact

```
Test: 1000 database operations

Without pooling:  2.5 seconds
With pooling:     0.3 seconds
Improvement:      8.3x faster!
```

### Real-World Example

```python
# Web API with Flask + Connection Pool
from flask import Flask
from dbutils.pooled_db import PooledDB

app = Flask(__name__)

# Create connection pool at startup
pool = PooledDB(
    creator=sqlite3,
    maxconnections=10,
    mincached=2,
    database='expenses.db'
)

@app.route('/add-expense', methods=['POST'])
def add_expense():
    # Get connection from pool
    conn = pool.connection()

    # Use it
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses ...")
    conn.commit()

    # Return to pool (automatic on close)
    conn.close()

    return "Success"
```

---

## 2️⃣ executemany()

### What is it?

`executemany()` executes the same SQL statement **multiple times** with different parameters in a **single batch operation**.

### The Problem

```python
# ❌ BAD: Individual operations (slow!)
expenses = [
    ('2025-10-01', 'Food', 45.50),
    ('2025-10-02', 'Transport', 20.00),
    ('2025-10-03', 'Shopping', 100.00),
    # ... 1000 more expenses
]

for date, category, amount in expenses:
    cursor.execute(
        "INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)",
        (date, category, amount)
    )
conn.commit()

# Database trips: 1000 (one per expense)
# Time: ~5 seconds
```

### The Solution

```python
# ✅ GOOD: Batch operation (fast!)
cursor.executemany(
    "INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)",
    expenses  # Pass all data at once!
)
conn.commit()

# Database trips: 1 (batch operation)
# Time: ~0.05 seconds (100x faster!)
```

### How It Works Internally

```
execute() - One at a time:
──────────────────────────
Python → Database: INSERT expense 1
Python ← Database: OK
Python → Database: INSERT expense 2
Python ← Database: OK
Python → Database: INSERT expense 3
Python ← Database: OK
... repeat 1000 times

executemany() - Batch:
─────────────────────
Python → Database: INSERT 1000 expenses
Python ← Database: OK

Result: Much faster!
```

### Performance Comparison

```
Dataset Size    execute()    executemany()    Speedup
────────────────────────────────────────────────────
10 records      0.010s       0.001s          10x
100 records     0.100s       0.005s          20x
1,000 records   1.000s       0.020s          50x
10,000 records  10.000s      0.100s          100x
```

### Real-World Use Cases

#### 1. CSV Import

```python
import csv

def import_from_csv(filename):
    expenses = []

    with open(filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header

        for row in reader:
            expenses.append((row[0], row[1], float(row[2])))

    # Import all at once!
    cursor.executemany(
        "INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)",
        expenses
    )
    conn.commit()

    print(f"Imported {len(expenses)} expenses!")
```

#### 2. Batch Updates

```python
# Update multiple budgets
updates = [
    (500.00, 'Food'),
    (300.00, 'Transport'),
    (200.00, 'Shopping'),
]

cursor.executemany(
    "UPDATE budgets SET monthly_limit = ? WHERE category = ?",
    updates
)
```

#### 3. Batch Deletes

```python
# Delete old expenses
old_expense_ids = [(1,), (2,), (3,), (4,), (5,)]

cursor.executemany(
    "DELETE FROM expenses WHERE id = ?",
    old_expense_ids
)
```

### When to Use

✅ **USE executemany():**

- Importing data (CSV, Excel, JSON)
- Bulk inserts/updates/deletes
- Data migration scripts
- Processing API responses
- Any operation on multiple records

❌ **DON'T USE executemany():**

- Single record operations
- Different SQL for each record
- When you need to check results between operations

---

## 3️⃣ Parameterized Queries & SQL Injection

### What is SQL Injection?

**SQL Injection** is when an attacker manipulates your SQL queries by inserting malicious SQL code through user input.

### The Danger (Live Example)

```python
# ❌ VULNERABLE CODE
username = input("Username: ")
password = input("Password: ")

query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
cursor.execute(query)
```

**Normal usage:**

```
Username: alice
Password: secret123

Query: SELECT * FROM users WHERE username = 'alice' AND password = 'secret123'
Result: Returns alice's data ✅
```

**Malicious usage:**

```
Username: alice' OR '1'='1
Password: anything

Query: SELECT * FROM users WHERE username = 'alice' OR '1'='1' AND password = 'anything'
                                              └── Always TRUE!
Result: Returns ALL users! 🚨
```

### Real Attack Examples

#### Attack 1: Bypass Authentication

```python
# Attacker enters:
username = "admin' --"

# Resulting query:
SELECT * FROM users WHERE username = 'admin' --' AND password = 'xyz'
                                              └── Everything after is commented out!

# Result: Logs in as admin without password!
```

#### Attack 2: Delete All Data

```python
# Attacker enters:
category = "Food'; DROP TABLE expenses; --"

# Resulting query:
SELECT * FROM expenses WHERE category = 'Food';
DROP TABLE expenses;
--'

# Result: YOUR ENTIRE EXPENSES TABLE IS DELETED! 💀
```

#### Attack 3: Steal Data

```python
# Attacker enters:
expense_id = "1 UNION SELECT username, password, NULL, NULL FROM users"

# Resulting query:
SELECT * FROM expenses WHERE id = 1
UNION SELECT username, password, NULL, NULL FROM users

# Result: Attacker gets all usernames and passwords! 🚨
```

### The Solution: Parameterized Queries

```python
# ✅ SAFE CODE - Parameterized Query
username = input("Username: ")
password = input("Password: ")

query = "SELECT * FROM users WHERE username = ? AND password = ?"
cursor.execute(query, (username, password))
```

**What happens with malicious input:**

```
Username: alice' OR '1'='1
Password: anything

The database treats it as:
  username = "alice' OR '1'='1"  (just a weird username string)
  password = "anything"

No SQL injection! It searches for a user literally named "alice' OR '1'='1"
which doesn't exist, so login fails ✅
```

### How Parameterized Queries Work

```
String Concatenation (BAD):
──────────────────────────
Your Code:  f"SELECT * FROM users WHERE id = {user_id}"
             ↓
SQL Engine: Interprets EVERYTHING as SQL code
             ↓
Malicious:  "1; DROP TABLE users" becomes valid SQL!


Parameterized Queries (GOOD):
─────────────────────────────
Your Code:  "SELECT * FROM users WHERE id = ?"
             ↓
SQL Engine: Knows "?" is a DATA placeholder
             ↓
Your Data:  (user_id,)
             ↓
SQL Engine: Escapes special characters automatically
             ↓
Malicious:  "1; DROP TABLE users" → safely escaped as string
```

### Different Syntax by Database

```python
# SQLite (what we use)
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# MySQL
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# PostgreSQL
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# Named parameters (SQLite)
cursor.execute("SELECT * FROM users WHERE id = :id", {"id": user_id})

# Named parameters (PostgreSQL)
cursor.execute("SELECT * FROM users WHERE id = %(id)s", {"id": user_id})
```

### Benefits Beyond Security

1. **🔒 Security**: Prevents SQL injection (obviously!)
2. **⚡ Performance**: Database can cache query plans
3. **🎨 Auto-escaping**: Handles quotes, special chars automatically
4. **📖 Readability**: Cleaner, more maintainable code
5. **🐛 Debugging**: Easier to see structure vs data

### Real-World Disasters

| Year | Company           | Impact                   | Cause         |
| ---- | ----------------- | ------------------------ | ------------- |
| 2008 | Heartland Payment | 130M credit cards stolen | SQL Injection |
| 2011 | Sony PlayStation  | 77M accounts compromised | SQL Injection |
| 2012 | Yahoo             | 450K passwords leaked    | SQL Injection |
| 2013 | Target            | 40M credit cards stolen  | SQL Injection |

**All preventable with parameterized queries!**

### Testing Your Code

Try these inputs to test for SQL injection:

```python
test_inputs = [
    "'",                          # Single quote
    "' OR '1'='1",               # OR condition
    "'; DROP TABLE expenses; --", # Command injection
    "1' UNION SELECT * FROM users --", # UNION attack
    "admin' --",                 # Comment injection
]

for test in test_inputs:
    result = search_expense(test)
    # If ANY cause errors or unexpected behavior, you're vulnerable!
```

### Golden Rules

1. ✅ **ALWAYS** use parameterized queries for user input
2. ❌ **NEVER** use f-strings or string concatenation for SQL
3. ✅ **ALWAYS** validate input (but don't rely on it alone)
4. ❌ **NEVER** trust ANY input (even from "trusted" sources)
5. ✅ **ALWAYS** use `?` or `%s` placeholders
6. ❌ **NEVER** build SQL queries dynamically from strings

### Quick Reference

```python
# ❌ DANGEROUS - Don't do this!
query = f"SELECT * FROM table WHERE id = {user_input}"
query = "SELECT * FROM table WHERE id = " + user_input
query = "SELECT * FROM table WHERE id = {}".format(user_input)
cursor.execute(query)


# ✅ SAFE - Do this!
query = "SELECT * FROM table WHERE id = ?"
cursor.execute(query, (user_input,))
```

---

## 🎓 Summary

### Connection Pooling

- **What**: Reuse database connections
- **When**: Multi-user web apps, APIs
- **Why**: 10-100x faster
- **Our App**: Not needed (single user)

### executemany()

- **What**: Batch database operations
- **When**: Multiple similar operations
- **Why**: 10-100x faster than loops
- **Our App**: Could use for CSV import!

### Parameterized Queries

- **What**: Separate SQL code from data
- **When**: ALWAYS with user input
- **Why**: Prevents SQL injection
- **Our App**: ✅ Already using everywhere!

---

## 📚 Further Learning

- [OWASP SQL Injection Guide](https://owasp.org/www-community/attacks/SQL_Injection)
- [Python DB-API 2.0](https://peps.python.org/pep-0249/)
- [SQLite Performance Tips](https://www.sqlite.org/optoverview.html)

---

**Your Smart Expense Tracker already follows all these best practices! ✅**
