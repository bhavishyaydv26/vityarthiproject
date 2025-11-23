import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

# --- CONFIGURATION ---
DB_NAME = "expense_tracker.db"
CURRENCY_SYMBOL = "₹"

# --- 1. Database Management Functions (Updated) ---

def init_db():
    """Connects to the database and creates the 'expenses' table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,          -- Expense date (YYYY-MM-DD)
                category TEXT,      -- Category (e.g., Food, Bills)
                amount REAL,        -- Expense amount
                description TEXT    -- Optional description
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"ERROR: Failed to initialize database: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def add_expense_to_db(date, category, amount, description):
    """Inserts a new expense record into the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
                       (date, category, amount, description))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database insertion error: {e}")
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def get_total_expense():
    """Calculates and returns the sum of all 'amount' entries."""
    # ... (function remains the same)...
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]
    conn.close()
    return total if total is not None else 0.0

def get_all_expenses():
    """Fetches all records from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, category, amount, description FROM expenses ORDER BY date DESC")
    records = cursor.fetchall()
    conn.close()
    return records

def delete_expense_by_id(expense_id):
    """Deletes a record based on its unique ID."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        return cursor.rowcount > 0 # Check if any row was deleted
    except sqlite3.Error as e:
        print(f"Database deletion error: {e}")
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def get_category_breakdown():
    """Calculates the sum of expenses grouped by category."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # GROUP BY category and calculate SUM
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY SUM(amount) DESC")
    breakdown = cursor.fetchall()
    conn.close()
    return breakdown


# --- 2. GUI Logic / Event Handlers (Updated) ---

def submit_expense():
    """Handles 'Add Expense' button click."""
    date = date_entry.get()
    category = category_var.get()
    
    try:
        amount = float(amount_entry.get())
        if amount == 0:
             messagebox.showerror("Input Error", "Amount cannot be zero.")
             return
    except ValueError:
        messagebox.showerror("Input Error", "Amount must be a valid number.")
        return

    description = description_entry.get()
    
    if add_expense_to_db(date, category, amount, description):
        messagebox.showinfo("Success", f"Expense of {CURRENCY_SYMBOL}{amount:,.2f} is added successfully!")
        amount_entry.delete(0, tk.END)
        description_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Could not add expense to the database.")

def view_summary():
    """Calculates and displays the total expense in a message box."""
    total = get_total_expense()
    summary_message = f"Your Total Expense Recorded:\n\n{CURRENCY_SYMBOL} {total:,.2f}"
    messagebox.showinfo("Total Expense Summary", summary_message)

def show_all_expenses():
    """Creates a new window to display all recorded expenses in a table."""
    records = get_all_expenses()

    if not records:
        messagebox.showinfo("View Expenses", "No expenses recorded yet.")
        return

    view_window = tk.Toplevel(root)
    view_window.title("All Recorded Expenses")

    # Use Treeview for a proper table/list view
    tree = ttk.Treeview(view_window, columns=("ID", "Date", "Category", "Amount", "Description"), show="headings")
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    # Define headings
    tree.heading("ID", text="ID")
    tree.heading("Date", text="Date")
    tree.heading("Category", text="Category")
    tree.heading("Amount", text=f"Amount ({CURRENCY_SYMBOL})")
    tree.heading("Description", text="Description")
    
    # Set column widths (adjust as needed)
    tree.column("ID", width=40, anchor='center')
    tree.column("Date", width=100)
    tree.column("Category", width=120)
    tree.column("Amount", width=80, anchor='e')
    tree.column("Description", width=250)

    # Insert data into the table
    for record in records:
        # Format amount to two decimal places
        formatted_record = (record[0], record[1], record[2], f"{record[3]:,.2f}", record[4])
        tree.insert("", tk.END, values=formatted_record)
        
def delete_expense_handler():
    """Asks for an ID and deletes the corresponding expense."""
    
    # Simple Toplevel dialog for input
    dialog = tk.Toplevel(root)
    dialog.title("Delete Expense")
    
    tk.Label(dialog, text="Enter Expense ID to Delete:").pack(padx=10, pady=5)
    id_entry = tk.Entry(dialog, width=15)
    id_entry.pack(padx=10, pady=5)
    
    def confirm_delete():
        try:
            expense_id = int(id_entry.get())
            if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Expense ID {expense_id}?"):
                if delete_expense_by_id(expense_id):
                    messagebox.showinfo("Success", f"Expense ID {expense_id} deleted successfully.")
                else:
                    messagebox.showerror("Error", f"Expense ID {expense_id} not found or could not be deleted.")
            dialog.destroy()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid numeric ID.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    tk.Button(dialog, text="Delete", command=confirm_delete, bg='#F44336', fg='white').pack(pady=10)
    
def show_breakdown():
    """Creates a new window to display category-wise totals."""
    breakdown_data = get_category_breakdown()

    if not breakdown_data:
        messagebox.showinfo("Category Breakdown", "No expenses recorded yet for breakdown.")
        return

    breakdown_window = tk.Toplevel(root)
    breakdown_window.title("Category-wise Breakdown")

    # Use Treeview for a proper table
    tree = ttk.Treeview(breakdown_window, columns=("Category", "Total"), show="headings")
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    # Define headings
    tree.heading("Category", text="Category")
    tree.heading("Total", text=f"Total Amount ({CURRENCY_SYMBOL})")
    
    # Set column widths
    tree.column("Category", width=150)
    tree.column("Total", width=100, anchor='e')

    # Insert data
    for category, total in breakdown_data:
        tree.insert("", tk.END, values=(category, f"{total:,.2f}"))


# --- 3. GUI Setup (Updated) ---

# Initialize DB and Main Window
init_db()
root = tk.Tk()
root.title(" Personal Expense Tracker")

# 1. Input Frame
input_frame = tk.Frame(root, padx=15, pady=15)
input_frame.pack(padx=10, pady=10, fill='x')

categories = ["Food", "Transport", "Bills", "Entertainment", "Income (Negative Expense)", "Other"]

tk.Label(input_frame, text="Date (YYYY-MM-DD):", anchor='w').grid(row=0, column=0, padx=5, pady=5, sticky='w')
date_entry = tk.Entry(input_frame, width=30) 
date_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
date_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) 

tk.Label(input_frame, text="Category:", anchor='w').grid(row=1, column=0, padx=5, pady=5, sticky='w')
category_var = tk.StringVar(input_frame)
category_var.set(categories[0])
category_menu = tk.OptionMenu(input_frame, category_var, *categories)
category_menu.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

tk.Label(input_frame, text=f"Amount ({CURRENCY_SYMBOL}):", anchor='w').grid(row=2, column=0, padx=5, pady=5, sticky='w')
amount_entry = tk.Entry(input_frame, width=30)
amount_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

tk.Label(input_frame, text="Description:", anchor='w').grid(row=3, column=0, padx=5, pady=5, sticky='w')
description_entry = tk.Entry(input_frame, width=30)
description_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

# 2. Buttons Frame
button_frame = tk.Frame(root, pady=10)
button_frame.pack()

add_button = tk.Button(button_frame, text=" Add Expense", command=submit_expense, 
                       width=15, bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
add_button.pack(side=tk.LEFT, padx=5)

total_button = tk.Button(button_frame, text=" Total Summary", command=view_summary, 
                         width=15, bg='#2196F3', fg='white', font=('Arial', 10, 'bold'))
total_button.pack(side=tk.LEFT, padx=5)

# 3. New Features Frame
feature_frame = tk.Frame(root, pady=5)
feature_frame.pack()

view_all_button = tk.Button(feature_frame, text=" View All Records", command=show_all_expenses,
                            width=15, bg='#FF9800', fg='white', font=('Arial', 10))
view_all_button.pack(side=tk.LEFT, padx=5)

breakdown_button = tk.Button(feature_frame, text=" Category Breakdown", command=show_breakdown,
                            width=17, bg='#00BCD4', fg='white', font=('Arial', 10))
breakdown_button.pack(side=tk.LEFT, padx=5)

delete_button = tk.Button(feature_frame, text=" Delete By ID", command=delete_expense_handler,
                            width=15, bg='#F44336', fg='white', font=('Arial', 10))
delete_button.pack(side=tk.LEFT, padx=5)


root.mainloop()