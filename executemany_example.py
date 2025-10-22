"""
executemany() and Parameterized Queries Demonstration
Shows the power and safety of these database techniques
"""

import sqlite3
import time

# Create a test database
conn = sqlite3.connect(':memory:')  # In-memory database for testing
cursor = conn.cursor()

# Create test table
cursor.execute("""
    CREATE TABLE expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        amount REAL,
        description TEXT
    )
""")

print("="*70)
print("EXECUTEMANY DEMONSTRATION")
print("="*70)

# ============================================
# BAD: Individual INSERT statements
# ============================================

print("\n❌ BAD WAY: Individual execute() calls")
print("-" * 70)

expenses = [
    ('2025-10-01', 'Food', 45.50, 'Lunch'),
    ('2025-10-02', 'Transport', 20.00, 'Uber'),
    ('2025-10-03', 'Shopping', 100.00, 'Clothes'),
    ('2025-10-04', 'Food', 30.00, 'Dinner'),
    ('2025-10-05', 'Entertainment', 50.00, 'Movie'),
]

start = time.time()

for date, category, amount, description in expenses:
    cursor.execute(
        "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
        (date, category, amount, description)
    )
    # Each execute() is a separate database operation!

conn.commit()
elapsed = time.time() - start

print(f"Inserted {len(expenses)} expenses")
print(f"Time taken: {elapsed:.6f} seconds")
print("Database trips: 5 (one per expense)")
print()

# Clear table for next test
cursor.execute("DELETE FROM expenses")
conn.commit()


# ============================================
# GOOD: executemany() - Batch INSERT
# ============================================

print("✅ GOOD WAY: executemany()")
print("-" * 70)

start = time.time()

cursor.executemany(
    "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
    expenses  # Pass all data at once!
)

conn.commit()
elapsed = time.time() - start

print(f"Inserted {len(expenses)} expenses")
print(f"Time taken: {elapsed:.6f} seconds")
print("Database trips: 1 (batch operation)")
print()

# ============================================
# Performance Comparison with Larger Data
# ============================================

print("\n📊 PERFORMANCE COMPARISON (1000 records)")
print("="*70)

# Generate test data
large_expenses = [
    (f'2025-10-{i%30+1:02d}', 'Food', 25.50 + i, f'Expense {i}')
    for i in range(1000)
]

# Test 1: Individual inserts
cursor.execute("DELETE FROM expenses")
start = time.time()
for expense in large_expenses:
    cursor.execute(
        "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
        expense
    )
conn.commit()
time_individual = time.time() - start

# Test 2: executemany
cursor.execute("DELETE FROM expenses")
start = time.time()
cursor.executemany(
    "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
    large_expenses
)
conn.commit()
time_batch = time.time() - start

print(f"\n❌ Individual execute(): {time_individual:.4f} seconds")
print(f"✅ executemany():        {time_batch:.4f} seconds")
print(f"🚀 Speed improvement:    {time_individual/time_batch:.2f}x faster!")
print()


# ============================================
# Other executemany() Use Cases
# ============================================

print("\n💡 OTHER executemany() USE CASES")
print("="*70)

# Batch UPDATE
print("\n1. Batch Updates:")
updates = [
    (100.00, 1),  # Set amount to 100 for expense id 1
    (200.00, 2),  # Set amount to 200 for expense id 2
    (300.00, 3),  # Set amount to 300 for expense id 3
]
cursor.executemany("UPDATE expenses SET amount = ? WHERE id = ?", updates)
print("   Updated multiple expenses in one operation")

# Batch DELETE
print("\n2. Batch Deletes:")
ids_to_delete = [(1,), (2,), (3,)]
cursor.executemany("DELETE FROM expenses WHERE id = ?", ids_to_delete)
print("   Deleted multiple expenses efficiently")


# ============================================
# Real-World Example: Import from CSV
# ============================================

print("\n\n📁 REAL-WORLD EXAMPLE: Importing from CSV")
print("="*70)

# Simulate CSV import
csv_data = """2025-10-01,Food,45.50,Breakfast
2025-10-01,Transport,20.00,Bus
2025-10-02,Shopping,100.00,Groceries
2025-10-02,Food,30.00,Lunch"""

print("CSV Content:")
print(csv_data)
print()

# Parse CSV
expenses_from_csv = []
for line in csv_data.strip().split('\n'):
    date, category, amount, description = line.split(',')
    expenses_from_csv.append((date, category, float(amount), description))

# Import in ONE batch operation
cursor.execute("DELETE FROM expenses")
cursor.executemany(
    "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
    expenses_from_csv
)
conn.commit()

print(f"✅ Imported {len(expenses_from_csv)} expenses from CSV in one batch!")

# Verify
cursor.execute("SELECT * FROM expenses")
results = cursor.fetchall()
print(f"Database now has {len(results)} expenses")
print()


print("\n📚 KEY TAKEAWAYS:")
print("─"*70)
print("""
executemany() Benefits:
  1. ⚡ MUCH faster (up to 100x for large datasets)
  2. 🔒 Single transaction (all-or-nothing)
  3. 💾 Less memory overhead
  4. 📉 Reduced network latency
  5. 🎯 Cleaner, more maintainable code

When to Use:
  ✅ Importing data (CSV, Excel, APIs)
  ✅ Batch updates or deletes
  ✅ Bulk data processing
  ✅ Migration scripts
  ✅ Any operation on multiple records
  
When NOT to Use:
  ❌ Single record operations (just use execute())
  ❌ When you need different SQL for each record
""")

conn.close()

