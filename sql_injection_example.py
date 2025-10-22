"""
SQL Injection and Parameterized Queries Demonstration
WARNING: This shows dangerous code for EDUCATIONAL purposes only!
"""

import sqlite3

# Setup test database
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT,
        role TEXT
    )
""")

cursor.execute("""
    CREATE TABLE expenses (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        category TEXT,
        amount REAL,
        description TEXT
    )
""")

# Add sample data
cursor.execute("INSERT INTO users VALUES (1, 'alice', 'secret123', 'admin')")
cursor.execute("INSERT INTO users VALUES (2, 'bob', 'password456', 'user')")
cursor.execute("INSERT INTO expenses VALUES (1, 1, 'Food', 45.50, 'Lunch')")
cursor.execute("INSERT INTO expenses VALUES (2, 2, 'Transport', 20.00, 'Uber')")
conn.commit()

print("="*70)
print("SQL INJECTION ATTACK DEMONSTRATION")
print("="*70)
print("\n⚠️  WARNING: Educational purposes only!")
print("Never use the 'BAD' examples in real code!\n")

# ============================================
# SCENARIO 1: Login Authentication
# ============================================

print("\n" + "="*70)
print("SCENARIO 1: User Login")
print("="*70)

def login_vulnerable(username, password):
    """❌ VULNERABLE: String concatenation"""
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    print(f"\n❌ BAD Query: {query}")
    
    cursor.execute(query)
    result = cursor.fetchone()
    return result

def login_safe(username, password):
    """✅ SAFE: Parameterized query"""
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    print(f"\n✅ GOOD Query: {query}")
    print(f"   Parameters: ('{username}', '{password}')")
    
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    return result


print("\n--- Normal Login Attempt ---")
username = "alice"
password = "secret123"

result = login_safe(username, password)
if result:
    print(f"✅ Login successful! Welcome, {result[1]}")
else:
    print("❌ Login failed!")


print("\n\n--- SQL INJECTION ATTACK! ---")
print("Attacker enters:")
username_malicious = "alice' OR '1'='1"
password_malicious = "anything"
print(f"Username: {username_malicious}")
print(f"Password: {password_malicious}")

result = login_vulnerable(username_malicious, password_malicious)
if result:
    print(f"\n🚨 DANGER! Attacker logged in as: {result[1]}")
    print("The attacker bypassed authentication!")
else:
    print("Login failed")

# Now try with safe version
print("\n--- Same Attack on SAFE Version ---")
result = login_safe(username_malicious, password_malicious)
if result:
    print(f"Login successful as: {result[1]}")
else:
    print("✅ Attack blocked! Login failed (as it should)")


# ============================================
# SCENARIO 2: Data Deletion Attack
# ============================================

print("\n\n" + "="*70)
print("SCENARIO 2: Searching Expenses")
print("="*70)

def search_expenses_vulnerable(category):
    """❌ VULNERABLE: String formatting"""
    query = f"SELECT * FROM expenses WHERE category = '{category}'"
    print(f"\n❌ BAD Query: {query}")
    
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        return []

def search_expenses_safe(category):
    """✅ SAFE: Parameterized query"""
    query = "SELECT * FROM expenses WHERE category = ?"
    print(f"\n✅ GOOD Query: {query}")
    print(f"   Parameter: ('{category}')")
    
    cursor.execute(query, (category,))
    return cursor.fetchall()


print("\n--- Normal Search ---")
results = search_expenses_safe("Food")
print(f"Found {len(results)} expenses")

print("\n\n--- DELETION ATTACK! ---")
print("Attacker enters:")
malicious_input = "Food'; DELETE FROM expenses; --"
print(f"Category: {malicious_input}")

results = search_expenses_vulnerable(malicious_input)
print("\nChecking if expenses table was deleted...")
cursor.execute("SELECT COUNT(*) FROM expenses")
count = cursor.fetchone()[0]
print(f"Expenses remaining: {count}")
if count == 0:
    print("🚨 DISASTER! All expenses were deleted!")

# Restore data
cursor.execute("INSERT INTO expenses VALUES (1, 1, 'Food', 45.50, 'Lunch')")
cursor.execute("INSERT INTO expenses VALUES (2, 2, 'Transport', 20.00, 'Uber')")
conn.commit()

print("\n--- Same Attack on SAFE Version ---")
results = search_expenses_safe(malicious_input)
print(f"Found {len(results)} expenses")
cursor.execute("SELECT COUNT(*) FROM expenses")
count = cursor.fetchone()[0]
print(f"✅ Expenses remaining: {count} (attack blocked!)")


# ============================================
# SCENARIO 3: Data Exfiltration
# ============================================

print("\n\n" + "="*70)
print("SCENARIO 3: Data Exfiltration Attack")
print("="*70)

def get_expense_vulnerable(expense_id):
    """❌ VULNERABLE"""
    query = f"SELECT * FROM expenses WHERE id = {expense_id}"
    print(f"\n❌ BAD Query: {query}")
    
    cursor.execute(query)
    return cursor.fetchall()

print("\n--- Normal Request ---")
print("User requests: expense_id = 1")
results = get_expense_vulnerable(1)
print(f"Returned: {results}")

print("\n\n--- UNION ATTACK (Steal All Passwords!) ---")
print("Attacker enters:")
malicious_id = "1 UNION SELECT id, username, password, role FROM users"
print(f"expense_id = {malicious_id}")

results = get_expense_vulnerable(malicious_id)
print(f"\n🚨 LEAKED DATA:")
for row in results:
    print(f"   {row}")
print("Attacker now has all usernames and passwords!")


# ============================================
# HOW PARAMETERIZED QUERIES WORK
# ============================================

print("\n\n" + "="*70)
print("HOW PARAMETERIZED QUERIES PROTECT YOU")
print("="*70)

print("""
What Happens with String Concatenation (BAD):
─────────────────────────────────────────────
query = f"SELECT * FROM users WHERE username = '{username}'"

If username = "alice' OR '1'='1"
Final query becomes:
  SELECT * FROM users WHERE username = 'alice' OR '1'='1'
                                               └── Always TRUE!
  
Result: Returns ALL users! 🚨


What Happens with Parameterized Queries (GOOD):
───────────────────────────────────────────────
query = "SELECT * FROM users WHERE username = ?"
cursor.execute(query, (username,))

If username = "alice' OR '1'='1"
Database treats entire string as DATA, not CODE:
  SELECT * FROM users WHERE username = 'alice'' OR ''1''=''1'
                                       └── Just a weird username, not SQL!

Result: No user found (safe!) ✅


The '?' placeholder tells the database:
  "Whatever comes here is DATA, not SQL code"
  
The database properly escapes special characters automatically!
""")


# ============================================
# BEST PRACTICES
# ============================================

print("\n" + "="*70)
print("BEST PRACTICES")
print("="*70)

print("""
✅ DO THIS:
──────────
# Python (SQLite)
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# Python (MySQL/PostgreSQL)
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# Python (named parameters)
cursor.execute("SELECT * FROM users WHERE id = :id", {"id": user_id})


❌ NEVER DO THIS:
─────────────────
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

query = "SELECT * FROM users WHERE id = " + str(user_id)
cursor.execute(query)

query = "SELECT * FROM users WHERE id = {}".format(user_id)
cursor.execute(query)


🎯 GOLDEN RULE:
───────────────
NEVER build SQL queries using string concatenation or f-strings
when the data comes from user input!

ALWAYS use parameterized queries (?, %s, or :name)


📋 BENEFITS:
────────────
1. 🔒 Prevents SQL injection (security)
2. ⚡ Better performance (query plan caching)
3. 🎨 Handles special characters automatically
4. 📝 Cleaner, more readable code
5. 🐛 Easier to debug
""")


# ============================================
# REAL-WORLD IMPACT
# ============================================

print("\n" + "="*70)
print("REAL-WORLD SQL INJECTION DISASTERS")
print("="*70)

print("""
Famous SQL Injection Attacks:

1. 🏦 2008 - Heartland Payment Systems
   → 130 million credit cards stolen
   → Loss: $140 million
   
2. 🎮 2011 - Sony PlayStation Network
   → 77 million user accounts compromised
   → Network down for 23 days
   
3. 🗳️  2012 - Yahoo Voices
   → 450,000 passwords leaked
   → Used simple SQL injection
   
4. 💳 2013 - Target Corporation
   → 40 million credit cards stolen
   → Started with SQL injection

5. 🚗 2015 - VTech Learning
   → 5 million customer records
   → Including children's data

All could have been prevented with parameterized queries! 🛡️
""")


# ============================================
# TESTING YOUR CODE
# ============================================

print("\n" + "="*70)
print("HOW TO TEST FOR SQL INJECTION")
print("="*70)

print("""
Test these inputs in your application:

1. Single quote:           '
2. Double dash:            --
3. OR statement:           ' OR '1'='1
4. UNION attack:           ' UNION SELECT * FROM users --
5. Comment injection:      '; DROP TABLE users; --
6. Multiple statements:    '; DELETE FROM expenses; --
7. Boolean injection:      1' AND '1'='1
8. Time-based:            1' AND SLEEP(5) --

If ANY of these cause:
  • Unexpected results
  • Database errors
  • Different behavior
  
Then you have a SQL injection vulnerability! 🚨

✅ With parameterized queries, ALL of these are safe!
""")

conn.close()

print("\n" + "="*70)
print("🎓 SUMMARY")
print("="*70)
print("""
Key Takeaways:

1. ALWAYS use parameterized queries (?, %s, :name)
2. NEVER concatenate user input into SQL
3. This applies to ALL databases (SQLite, MySQL, PostgreSQL, etc.)
4. Even if you "trust" the input, use parameterized queries
5. It's not just about security - it's also better performance!

Your Smart Expense Tracker is SAFE ✅
We use parameterized queries throughout!
""")

