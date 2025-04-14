import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog

# === Database Setup ===
conn = sqlite3.connect("library.db")
cursor = conn.cursor()

# Create books table
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    book_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    is_issued INTEGER DEFAULT 0
)
""")

# Create request queue table
cursor.execute("""
CREATE TABLE IF NOT EXISTS request_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT
)
""")
conn.commit()


# === Functions ===
def add_book():
    book_id = simpledialog.askstring("Input", "Enter Book ID:")
    title = simpledialog.askstring("Input", "Enter Title:")
    author = simpledialog.askstring("Input", "Enter Author:")
    if book_id and title and author:
        try:
            cursor.execute("INSERT INTO books (book_id, title, author) VALUES (?, ?, ?)", (book_id, title, author))
            conn.commit()
            messagebox.showinfo("Success", f"Book '{title}' added.")
        except sqlite3.IntegrityError:
            messagebox.showwarning("Error", "Book ID already exists.")

def delete_book():
    book_id = simpledialog.askstring("Input", "Enter Book ID to delete:")
    cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
    if cursor.rowcount > 0:
        conn.commit()
        messagebox.showinfo("Deleted", f"Book {book_id} deleted.")
    else:
        messagebox.showwarning("Error", "Book not found.")

def search_book():
    keyword = simpledialog.askstring("Input", "Enter keyword to search:")
    if keyword:
        cursor.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ?", 
                       (f'%{keyword}%', f'%{keyword}%'))
        results = cursor.fetchall()
        if results:
            result_text = ""
            for book in results:
                status = "Issued" if book[3] else "Available"
                result_text += f"{book[0]}: {book[1]} by {book[2]} - {status}\n"
            messagebox.showinfo("Search Results", result_text)
        else:
            messagebox.showinfo("Search", "No matching books found.")

def issue_book():
    book_id = simpledialog.askstring("Input", "Enter Book ID to issue:")
    cursor.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()
    if book:
        if not book[3]:  # is_issued == 0
            cursor.execute("UPDATE books SET is_issued = 1 WHERE book_id = ?", (book_id,))
            conn.commit()
            messagebox.showinfo("Issued", f"Book '{book[1]}' issued.")
        else:
            cursor.execute("INSERT INTO request_queue (book_id) VALUES (?)", (book_id,))
            conn.commit()
            messagebox.showinfo("Info", "Book already issued. Added to request queue.")
    else:
        messagebox.showwarning("Error", "Book not found.")

def return_book():
    book_id = simpledialog.askstring("Input", "Enter Book ID to return:")
    cursor.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()
    if book:
        cursor.execute("UPDATE books SET is_issued = 0 WHERE book_id = ?", (book_id,))
        conn.commit()
        message = f"Book '{book[1]}' returned."
        # Remove from queue if exists
        cursor.execute("DELETE FROM request_queue WHERE book_id = ? LIMIT 1", (book_id,))
        conn.commit()
        messagebox.showinfo("Returned", message)
    else:
        messagebox.showwarning("Error", "Book not found.")

def view_all_books():
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    if books:
        result = ""
        for book in books:
            status = "Issued" if book[3] else "Available"
            result += f"{book[0]}: {book[1]} by {book[2]} - {status}\n"
        messagebox.showinfo("All Books", result)
    else:
        messagebox.showinfo("All Books", "No books found.")

def view_request_queue():
    cursor.execute("SELECT book_id FROM request_queue")
    queue = cursor.fetchall()
    if queue:
        result = "Book Request Queue:\n"
        for i, (book_id,) in enumerate(queue):
            cursor.execute("SELECT title FROM books WHERE book_id = ?", (book_id,))
            title = cursor.fetchone()
            if title:
                result += f"{i+1}. {title[0]} (ID: {book_id})\n"
        messagebox.showinfo("Queue", result)
    else:
        messagebox.showinfo("Queue", "Request queue is empty.")


# === GUI ===
root = tk.Tk()
root.title("Library Management System with Database")
root.geometry("400x400")

tk.Button(root, text="Add Book", command=add_book, width=30).pack(pady=5)
tk.Button(root, text="Delete Book", command=delete_book, width=30).pack(pady=5)
tk.Button(root, text="Search Book", command=search_book, width=30).pack(pady=5)
tk.Button(root, text="Issue Book", command=issue_book, width=30).pack(pady=5)
tk.Button(root, text="Return Book", command=return_book, width=30).pack(pady=5)
tk.Button(root, text="View All Books", command=view_all_books, width=30).pack(pady=5)
tk.Button(root, text="View Request Queue", command=view_request_queue, width=30).pack(pady=5)

root.mainloop()

# Close DB connection when GUI closes
conn.close()
