import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext

# 创建数据库并使用 Row 方便按名称访问列
conn = sqlite3.connect("bookstore.db")
conn.row_factory = sqlite3.Row
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
conn.commit()

def safe_strip(s):
    return s.strip() if isinstance(s, str) else s

# 进货
def add_stock():
    try:
        isbn = simpledialog.askstring("进货", "ISBN:")
        if isbn is None:
            return  # user cancelled
        isbn = safe_strip(isbn)
        if not isbn:
            messagebox.showerror("错误", "ISBN 不能为空。")
            return

        title = simpledialog.askstring("进货", "书名:")
        author = simpledialog.askstring("进货", "作者:")
        price = simpledialog.askfloat("进货", "单价:")
        quantity = simpledialog.askinteger("进货", "数量:")

        # Validate numeric inputs
        if quantity is None or quantity <= 0:
            messagebox.showerror("错误", "请输入大于 0 的数量。")
            return
        if price is None or price < 0:
            messagebox.showerror("错误", "请输入非负的单价。")
            return

        title = safe_strip(title) or ""
        author = safe_strip(author) or ""

        cursor.execute("SELECT * FROM books WHERE isbn = ?", (isbn,))
        book = cursor.fetchone()
        if book:
            # preserve existing values if the user left title/author empty
            new_title = title if title else book["title"]
            new_author = author if author else book["author"]
            new_price = price if price is not None else book["price"]
            cursor.execute(
                "UPDATE books SET quantity = quantity + ?, title = ?, author = ?, price = ? WHERE isbn = ?",
                (quantity, new_title, new_author, new_price, isbn)
            )
        else:
            cursor.execute(
                "INSERT INTO books (isbn, title, author, price, quantity) VALUES (?, ?, ?, ?, ?)",
                (isbn, title, author, float(price), quantity)
            )
        conn.commit()
        messagebox.showinfo("成功", "进货已记录！")
    except sqlite3.Error as e:
        messagebox.showerror("数据库错误", str(e))

# 销售
def sell_book():
    try:
        isbn = simpledialog.askstring("销售", "ISBN:")
        if isbn is None:
            return
        isbn = safe_strip(isbn)
        if not isbn:
            messagebox.showerror("错误", "ISBN 不能为空。")
            return

        quantity = simpledialog.askinteger("销售", "销售数量:")
        if quantity is None or quantity <= 0:
            messagebox.showerror("错误", "请输入大于 0 的销售数量。")
            return

        cursor.execute("SELECT quantity, price, title FROM books WHERE isbn = ?", (isbn,))
        row = cursor.fetchone()
        if not row:
            messagebox.showerror("错误", "找不到该书！")
            return

        current_stock = row["quantity"]
        price = row["price"] if row["price"] is not None else 0.0
        title = row["title"] or isbn

        if quantity <= current_stock:
            cursor.execute("UPDATE books SET quantity = quantity - ? WHERE isbn = ?", (quantity, isbn))
            conn.commit()
            total = quantity * float(price)
            messagebox.showinfo("成功", f"销售记录完成！\n书名: {title}\n数量: {quantity}\n总计: ¥{total:.2f}")
        else:
            messagebox.showerror("错误", "库存不足！")
    except sqlite3.Error as e:
        messagebox.showerror("数据库错误", str(e))

# 查询库存（使用可滚动文本窗口以便长列表）
def view_stock():
    try:
        cursor.execute("SELECT * FROM books ORDER BY title")
        books = cursor.fetchall()
        if not books:
            messagebox.showinfo("库存列表", "暂无库存")
            return

        win = tk.Toplevel(root)
        win.title("库存列表")
        st = scrolledtext.ScrolledText(win, width=80, height=20, wrap=tk.NONE)
        st.pack(fill=tk.BOTH, expand=True)
        for b in books:
            isbn = b["isbn"]
            title = b["title"] or ""
            author = b["author"] or ""
            price = b["price"] if b["price"] is not None else 0.0
            qty = b["quantity"] if b["quantity"] is not None else 0
            st.insert(tk.END, f"{isbn} | {title} | {author} | ¥{float(price):.2f} | 库存: {qty}\n")
        st.configure(state=tk.DISABLED)
    except sqlite3.Error as e:
        messagebox.showerror("数据库错误", str(e))

def on_closing():
    try:
        conn.close()
    except Exception:
        pass
    root.destroy()

# 主界面
root = tk.Tk()
root.title("小书店进销存系统")

tk.Button(root, text="📦 进货", width=20, command=add_stock).pack(pady=10)
tk.Button(root, text="💰 销售", width=20, command=sell_book).pack(pady=10)
tk.Button(root, text="📚 查看库存", width=20, command=view_stock).pack(pady=10)
tk.Button(root, text="❌ 退出", width=20, command=on_closing).pack(pady=10)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()