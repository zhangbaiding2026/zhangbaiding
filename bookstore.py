import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog

# 创建数据库
conn = sqlite3.connect("bookstore.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS books (
    isbn TEXT PRIMARY KEY,
    title TEXT,
    author TEXT,
    price REAL,
    quantity INTEGER
)
''')

# 进货
def add_stock():
    isbn = simpledialog.askstring("进货", "ISBN:")
    title = simpledialog.askstring("进货", "书名:")
    author = simpledialog.askstring("进货", "作者:")
    price = simpledialog.askfloat("进货", "单价:")
    quantity = simpledialog.askinteger("进货", "数量:")

    if isbn and quantity:
        cursor.execute("SELECT * FROM books WHERE isbn=?", (isbn,))
        book = cursor.fetchone()
        if book:
            cursor.execute("UPDATE books SET quantity=quantity+? WHERE isbn=?", (quantity, isbn))
        else:
            cursor.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?)", (isbn, title, author, price, quantity))
        conn.commit()
        messagebox.showinfo("成功", "进货已记录！")

# 销售
def sell_book():
    isbn = simpledialog.askstring("销售", "ISBN:")
    quantity = simpledialog.askinteger("销售", "销售数量:")

    if isbn and quantity:
        cursor.execute("SELECT quantity FROM books WHERE isbn=?", (isbn,))
        result = cursor.fetchone()
        if result:
            current_stock = result[0]
            if quantity <= current_stock:
                cursor.execute("UPDATE books SET quantity=quantity-? WHERE isbn=?", (quantity, isbn))
                conn.commit()
                messagebox.showinfo("成功", "销售记录完成！")
            else:
                messagebox.showerror("错误", "库存不足！")
        else:
            messagebox.showerror("错误", "找不到该书！")

# 查询库存
def view_stock():
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    display = "\n".join([f"{b[0]} | {b[1]} | {b[2]} | ¥{b[3]} | 库存: {b[4]}" for b in books])
    messagebox.showinfo("库存列表", display or "暂无库存")

# 主界面
root = tk.Tk()
root.title("小书店进销存系统")

tk.Button(root, text="📦 进货", width=20, command=add_stock).pack(pady=10)
tk.Button(root, text="💰 销售", width=20, command=sell_book).pack(pady=10)
tk.Button(root, text="📚 查看库存", width=20, command=view_stock).pack(pady=10)
tk.Button(root, text="❌ 退出", width=20, command=root.quit).pack(pady=10)

root.mainloop()
