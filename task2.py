import sqlite3

# Create / Connect to database
conn = sqlite3.connect("company.db")

cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    department TEXT,
    salary REAL
)
""")

# Insert data
cursor.execute("INSERT INTO employees (name, age, department, salary) VALUES (?, ?, ?, ?)",
               ("Ravi", 28, "HR", 30000))

cursor.execute("INSERT INTO employees (name, age, department, salary) VALUES (?, ?, ?, ?)",
               ("Sneha", 25, "IT", 45000))

cursor.execute("INSERT INTO employees (name, age, department, salary) VALUES (?, ?, ?, ?)",
               ("Arjun", 30, "Finance", 50000))

cursor.execute("INSERT INTO employees (name, age, department, salary) VALUES (?, ?, ?, ?)",
               ("Meena", 27, "Marketing", 38000))

cursor.execute("INSERT INTO employees (name, age, department, salary) VALUES (?, ?, ?, ?)",
               ("Kiran", 29, "IT", 47000))

# Commit changes
conn.commit()

# Fetch data
cursor.execute("SELECT * FROM employees")
print(cursor.fetchall())

# Close connection
conn.close()