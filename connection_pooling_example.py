"""
Connection Pooling Example
Demonstrates the difference between regular connections and pooled connections
"""

import sqlite3
import time
from threading import Thread

# ============================================
# WITHOUT Connection Pooling (Current System)
# ============================================

def without_pooling():
    """Each operation creates a new connection"""
    print("\n🔴 WITHOUT Connection Pooling:")
    start = time.time()
    
    for i in range(10):
        # Create new connection each time (SLOW)
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM expenses")
        result = cursor.fetchone()
        
        conn.close()
        print(f"  Query {i+1}: {result[0]} expenses")
    
    elapsed = time.time() - start
    print(f"  Time: {elapsed:.4f} seconds\n")


# ============================================
# WITH Connection Pooling
# ============================================

class SimpleConnectionPool:
    """A simple connection pool implementation"""
    
    def __init__(self, database, pool_size=5):
        """Create a pool of database connections"""
        self.database = database
        self.pool = []
        self.available = []
        
        # Pre-create connections
        for _ in range(pool_size):
            conn = sqlite3.connect(database, check_same_thread=False)
            self.pool.append(conn)
            self.available.append(conn)
        
        print(f"✅ Created connection pool with {pool_size} connections")
    
    def get_connection(self):
        """Get a connection from the pool"""
        if self.available:
            conn = self.available.pop()
            return conn
        else:
            # Pool exhausted, create new connection
            conn = sqlite3.connect(self.database, check_same_thread=False)
            self.pool.append(conn)
            return conn
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        if conn not in self.available:
            self.available.append(conn)
    
    def close_all(self):
        """Close all connections in pool"""
        for conn in self.pool:
            conn.close()


def with_pooling():
    """Use connection pool for multiple operations"""
    print("\n🟢 WITH Connection Pooling:")
    
    # Create pool once
    pool = SimpleConnectionPool('expenses.db', pool_size=3)
    
    start = time.time()
    
    for i in range(10):
        # Get connection from pool (FAST - reuses existing)
        conn = pool.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM expenses")
        result = cursor.fetchone()
        
        # Return to pool instead of closing
        pool.return_connection(conn)
        print(f"  Query {i+1}: {result[0]} expenses")
    
    elapsed = time.time() - start
    print(f"  Time: {elapsed:.4f} seconds")
    
    pool.close_all()
    print()


# ============================================
# Real-World Scenario: Multiple Users
# ============================================

def simulate_multiple_users_without_pool():
    """Simulate 5 users making requests"""
    print("\n🔴 Multiple Users WITHOUT Pooling:")
    start = time.time()
    
    def user_request(user_id):
        # Each user creates their own connection
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM expenses")
        result = cursor.fetchone()
        conn.close()
        print(f"  User {user_id}: Got {result[0]} expenses")
    
    threads = []
    for i in range(5):
        thread = Thread(target=user_request, args=(i+1,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    elapsed = time.time() - start
    print(f"  Time: {elapsed:.4f} seconds\n")


def simulate_multiple_users_with_pool():
    """Simulate 5 users with connection pool"""
    print("\n🟢 Multiple Users WITH Pooling:")
    pool = SimpleConnectionPool('expenses.db', pool_size=3)
    start = time.time()
    
    def user_request(user_id):
        # Users share connections from pool
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM expenses")
        result = cursor.fetchone()
        pool.return_connection(conn)
        print(f"  User {user_id}: Got {result[0]} expenses")
    
    threads = []
    for i in range(5):
        thread = Thread(target=user_request, args=(i+1,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    elapsed = time.time() - start
    print(f"  Time: {elapsed:.4f} seconds")
    pool.close_all()
    print()


# ============================================
# When to Use Connection Pooling
# ============================================

def when_to_use():
    print("""
📚 When to Use Connection Pooling:
─────────────────────────────────────────

✅ GOOD for:
  • Web applications (multiple users)
  • API servers
  • Multi-threaded applications
  • High-frequency database operations
  
❌ NOT needed for:
  • Single-user desktop apps (like our expense tracker!)
  • Scripts that run once and exit
  • Low-traffic applications
  • Simple command-line tools

💡 Our Smart Expense Tracker:
  → Single user, one connection at a time
  → Connection pooling would be OVERKILL
  → Current approach is perfectly fine!
    """)


if __name__ == "__main__":
    print("="*60)
    print("CONNECTION POOLING DEMONSTRATION")
    print("="*60)
    
    # Basic comparison
    without_pooling()
    with_pooling()
    
    # Multi-user scenario
    simulate_multiple_users_without_pool()
    simulate_multiple_users_with_pool()
    
    # When to use
    when_to_use()

