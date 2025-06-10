import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import pymysql
import pandas as pd

def show_info_popup(title, info):
    popup = tk.Toplevel()
    popup.title(title)
    popup_width = 540
    popup_height = 240
    popup_anchor_left = int((popup.winfo_screenwidth() - popup_width)/2) #置中視窗
    popup_anchor_top = int((popup.winfo_screenheight() - popup_height)/2)
    popup.geometry(f'{popup_width}x{popup_height}+{popup_anchor_left}+{popup_anchor_top}')
    popup.resizable(False, False)
    tk.Label(popup, text=info, font=('Microsoft YaHei', 14), justify="left").pack(expand=True, fill="both", padx=30, pady=30)
    tk.Button(popup, text="關閉", font=('Microsoft YaHei', 14), command=popup.destroy).pack(pady=10)
    popup.transient()  # 讓彈窗浮在主視窗上
    popup.grab_set()   # 模態視窗

def warn_below_safe_stock(conn, product_num):
    """Show warning if product stock falls below its safe level."""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT sv.stock_quantity, p.safe_stock, p.product_name
        FROM stock_view sv
        JOIN product p ON sv.product_num = p.product_num
        WHERE sv.product_num = %s
        """,
        (product_num,)
    )
    row = cur.fetchone()
    if row and row[0] < row[1]:
        messagebox.showwarning(
            "存量警告",
            f"商品 {row[2]} 存量({row[0]})低於安全庫存({row[1]})，請盡速補貨",
        )

class LoginFrame(tk.Frame): 
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.switch_frame = switch_frame
        tk.Label(self, text="生芳髮品", font=('Microsoft YaHei', 96)).pack(pady=120)
        account_frame = tk.Frame(self)
        account_frame.pack(pady=10)
        tk.Label(account_frame, text="帳號：", font=('Microsoft YaHei', 24)).pack(side="left",padx=10)
        self.entry_user = tk.Entry(account_frame, font=('Microsoft YaHei', 12))
        self.entry_user.pack(side="left",padx=10)
        psw_frame = tk.Frame(self)
        psw_frame.pack(pady=10)
        tk.Label(psw_frame, text="密碼：", font=('Microsoft YaHei', 24)).pack(side="left",padx=10)
        self.entry_pwd = tk.Entry(psw_frame, font=('Microsoft YaHei', 12), show='*')
        self.entry_pwd.pack(side="left",padx=10)
        tk.Button(self, text="登入", font=('Microsoft YaHei', 18), command=self.try_login).pack()

    def try_login(self):
        user = self.entry_user.get().strip()
        pwd = self.entry_pwd.get().strip()
        if not user or not pwd:
            messagebox.showerror("登入失敗", "請輸入帳號與密碼！")
            return

        try:
        # 連接主 Frame 的 conn
            cur = self.master.conn.cursor()
        # 查詢帳密
            sql = "SELECT user_type, user_num FROM user WHERE user_accont=%s AND password=%s"
            cur.execute(sql, (user, pwd))
            result = cur.fetchone()
            if result:
                user_type, user_num = result
            # 記錄目前登入者資訊，若App需後續用到user_num（如訂單時需記錄agent）
                self.master.current_user_num = user_num  
                if user_type == "admin":
                    self.switch_frame("admin_menu")
                elif user_type == "agent":
                    self.switch_frame("agent_menu")
                else:
                    messagebox.showinfo("錯誤", f"目前不支援此身份類型：{user_type}")
            else:
                messagebox.showerror("登入失敗", "帳號或密碼錯誤！")
        except Exception as e:
            messagebox.showerror("錯誤", f"資料庫查詢失敗\n{e}")

class AgentMenuFrame(tk.Frame):
    def __init__(self, master, switch_frame):
        super().__init__(master)
        tk.Label(self, text="").pack(pady=50)
        tk.Label(self, text="歡迎進入業務介面！", font=('Microsoft YaHei',36)).pack(pady=90)
        tk.Button(self, text="登出", font=('Microsoft YaHei', 12), command=lambda: switch_frame("login")).place(x=5, y=5)
        tk.Button(self, text="訂單記錄系統", font=('Microsoft YaHei', 24), command=lambda: switch_frame("order_menu")).pack(pady=30)
        tk.Button(self, text="顧客維護系統", font=('Microsoft YaHei', 24), command=lambda: switch_frame("customer_menu")).pack(pady=30)

class AdminMenuFrame(tk.Frame):
    def __init__(self, master, switch_frame):
        super().__init__(master)
        tk.Label(self, text="").pack(pady=50)
        tk.Label(self, text="歡迎進入管理員介面！", font=('Microsoft YaHei',36)).pack(pady=90)
        tk.Button(self, text="登出", font=('Microsoft YaHei', 12), command=lambda: switch_frame("login")).place(x=5, y=5)
        tk.Button(self, text="進銷存管理系統", font=('Microsoft YaHei',24), command=lambda: switch_frame("inventory_menu")).pack(pady=20)
        tk.Button(self, text="商品項目系統", font=('Microsoft YaHei',24), command=lambda: switch_frame("product_menu")).pack(pady=20)
        tk.Button(self, text="使用者管理系統", font=('Microsoft YaHei',24), command=lambda: switch_frame("user_menu")).pack(pady=20)

class UserMenuFrame(tk.Frame):
    def __init__(self, master, switch_frame):
        super().__init__(master)
        tk.Label(self, text="").pack(pady=60)
        tk.Label(self, text="使用者管理系統", font=('Microsoft YaHei',36)).pack(pady=90)
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 12), command=lambda: switch_frame("admin_menu")).place(x=5, y=5)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="使用者新增", font=('Microsoft YaHei', 24), command=lambda: switch_frame("user_add")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="使用者查詢", font=('Microsoft YaHei', 24), command=lambda: switch_frame("user_query")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="使用者修改", font=('Microsoft YaHei', 24), command=lambda: switch_frame("user_mod")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="使用者刪除", font=('Microsoft YaHei', 24), command=lambda: switch_frame("user_delete")).pack(side="left", padx=10)

class UserAddFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn

        # 大標題
        tk.Label(self, text="使用者新增", font=('Microsoft YaHei',36)).pack(pady=40)

        main_frame = tk.Frame(self)
        main_frame.pack(pady=10)

        # 使用者帳號
        tk.Label(main_frame, text="使用者帳號：", font=('Microsoft YaHei',20)).grid(row=0, column=0, sticky='e', pady=12)
        self.acc_entry = tk.Entry(main_frame, font=('Microsoft YaHei',16), width=20)
        self.acc_entry.grid(row=0, column=1, sticky='w', pady=12)

        # 使用者密碼
        tk.Label(main_frame, text="使用者密碼：", font=('Microsoft YaHei',20)).grid(row=1, column=0, sticky='e', pady=12)
        self.pw_entry = tk.Entry(main_frame, font=('Microsoft YaHei',16), width=20, show='*')
        self.pw_entry.grid(row=1, column=1, sticky='w', pady=12)

        # 使用者名稱
        tk.Label(main_frame, text="使用者名稱：", font=('Microsoft YaHei',20)).grid(row=2, column=0, sticky='e', pady=12)
        self.name_entry = tk.Entry(main_frame, font=('Microsoft YaHei',16), width=20)
        self.name_entry.grid(row=2, column=1, sticky='w', pady=12)

        # 使用者類別
        tk.Label(main_frame, text="使用者類別：", font=('Microsoft YaHei',20)).grid(row=3, column=0, sticky='e', pady=12)
        self.type_combo = ttk.Combobox(main_frame, font=('Microsoft YaHei',16), width=18, state="readonly")
        self.type_combo['values'] = ["agent", "admin"]
        self.type_combo.grid(row=3, column=1, sticky='w', pady=12)

        # 新增使用者按鈕
        tk.Button(self, text="新增使用者", font=('Microsoft YaHei',20), width=12, command=self.add_user)\
            .place(relx=0.85, rely=0.85)

        # 返回上一頁
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16), command=lambda: switch_frame("user_menu"))\
            .place(x=15, y=15)

    def add_user(self):
        acc = self.acc_entry.get().strip()
        pw = self.pw_entry.get().strip()
        name = self.name_entry.get().strip()
        user_type = self.type_combo.get()

        if not acc or acc == "輸入使用者帳號" or not pw or pw == "輸入使用者密碼" or not name or name == "輸入使用者名稱" or user_type not in ["agent", "admin"]:
            messagebox.showerror("錯誤", "請完整填寫所有欄位！")
            return

        cur = self.conn.cursor()
        try:
            cur.execute("INSERT INTO user (user_accont, password, name, user_type) VALUES (%s, %s, %s, %s)",
                        (acc, pw, name, user_type))
            self.conn.commit()
            messagebox.showinfo("成功", "已新增使用者！")
            self.acc_entry.delete(0, tk.END)
            self.pw_entry.delete(0, tk.END)
            self.name_entry.delete(0, tk.END)
            self.type_combo.set("類別下拉清單")
        except Exception as e:
            messagebox.showerror("資料庫錯誤", str(e))

class UserQueryFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn

        # 標題
        tk.Label(self, text="使用者查詢", font=('Microsoft YaHei',36,"bold")).pack(pady=40)

        main_frame = tk.Frame(self)
        main_frame.pack(pady=10)

        # 使用者名稱下拉選單
        tk.Label(main_frame, text="使用者名稱：", font=('Microsoft YaHei',20)).grid(row=0, column=0, pady=20, sticky="e")
        self.name_combo = ttk.Combobox(main_frame, font=('Microsoft YaHei',16), width=20, state="readonly")
        self.name_combo.grid(row=0, column=1, pady=20, sticky="w")

        # 查詢按鈕
        tk.Button(self, text="查詢使用者", font=('Microsoft YaHei',20), width=12, command=self.query_user)\
            .place(relx=0.85, rely=0.85)

        # 返回上一頁
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16), command=lambda: switch_frame("user_menu"))\
            .place(x=15, y=15)

        self.load_user_names()

    def load_user_names(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM user")
        names = [row[0] for row in cur.fetchall()]
        self.name_combo['values'] = names

    def query_user(self):
        user_name = self.name_combo.get()
        if not user_name:
            messagebox.showerror("錯誤", "請選擇使用者名稱")
            return
        cur = self.conn.cursor()
        cur.execute("SELECT user_accont, password, name, user_type FROM user WHERE name=%s", (user_name,))
        row = cur.fetchone()
        if row:
            info = f"""使用者帳號：{row[0]}\n使用者密碼：{row[1]}\n使用者名稱：{row[2]}\n使用者類別：{row[3]}"""
            show_info_popup("使用者資訊", info)
        else:
            messagebox.showinfo("查詢結果", "查無此使用者資料")

    def refresh(self):
        self.load_user_names()
        self.name_combo.set('')  # 清空選擇

class UserModFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn

        tk.Label(self, text="使用者修改", font=('Microsoft YaHei', 36, "bold")).pack(pady=40)
        main_frame = tk.Frame(self)
        main_frame.pack(pady=10)

        # 使用者名稱下拉選單
        tk.Label(main_frame, text="使用者名稱：", font=('Microsoft YaHei', 20)).grid(row=0, column=0, sticky="e", pady=10)
        self.name_combo = ttk.Combobox(main_frame, font=('Microsoft YaHei', 16), width=22, state="readonly")
        self.name_combo.grid(row=0, column=1, pady=10, sticky="w")
        self.name_combo.bind("<<ComboboxSelected>>", self.fill_user_info)

        # 各欄位
        tk.Label(main_frame, text="使用者名稱：", font=('Microsoft YaHei', 20)).grid(row=1, column=0, sticky="e", pady=10)
        self.name_entry = tk.Entry(main_frame, font=('Microsoft YaHei', 16), width=24)
        self.name_entry.grid(row=1, column=1, pady=10, sticky="w")

        tk.Label(main_frame, text="使用者帳號：", font=('Microsoft YaHei', 20)).grid(row=2, column=0, sticky="e", pady=10)
        self.acc_entry = tk.Entry(main_frame, font=('Microsoft YaHei', 16), width=24)
        self.acc_entry.grid(row=2, column=1, pady=10, sticky="w")

        tk.Label(main_frame, text="使用者密碼：", font=('Microsoft YaHei', 20)).grid(row=3, column=0, sticky="e", pady=10)
        self.pw_entry = tk.Entry(main_frame, font=('Microsoft YaHei', 16), width=24, show="*")
        self.pw_entry.grid(row=3, column=1, pady=10, sticky="w")

        tk.Label(main_frame, text="使用者類別：", font=('Microsoft YaHei', 20)).grid(row=4, column=0, sticky="e", pady=10)
        self.type_combo = ttk.Combobox(main_frame, font=('Microsoft YaHei', 16), width=22, state="readonly")
        self.type_combo['values'] = ("agent", "admin")
        self.type_combo.grid(row=4, column=1, pady=10, sticky="w")

        # 修改按鈕
        tk.Button(self, text="修改使用者", font=('Microsoft YaHei', 20), command=self.update_user)\
            .place(relx=0.85, rely=0.85)

        # 返回按鈕
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16), command=lambda: switch_frame("user_menu"))\
            .place(x=15, y=15)

        self.load_user_names()

    def load_user_names(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM user")
        names = [row[0] for row in cur.fetchall()]
        self.name_combo['values'] = names
        self.name_combo.set("請選擇使用者")
        self.clear_entries()

    def fill_user_info(self, event=None):
        user_name = self.name_combo.get()
        if not user_name or user_name == "請選擇使用者":
            self.clear_entries()
            return
        cur = self.conn.cursor()
        cur.execute("SELECT user_accont, password, name, user_type FROM user WHERE name=%s", (user_name,))
        row = cur.fetchone()
        if row:
            self.acc_entry.delete(0, tk.END)
            self.acc_entry.insert(0, row[0])
            self.pw_entry.delete(0, tk.END)
            self.pw_entry.insert(0, row[1])
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, row[2])
            self.type_combo.set(row[3])
        else:
            self.clear_entries()

    def clear_entries(self):
        self.acc_entry.delete(0, tk.END)
        self.pw_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.type_combo.set("")

    def update_user(self):
        ori_name = self.name_combo.get()
        new_name = self.name_entry.get()
        acc = self.acc_entry.get()
        pw = self.pw_entry.get()
        user_type = self.type_combo.get()
        if not (ori_name and new_name and acc and pw and user_type and ori_name != "請選擇使用者"):
            messagebox.showerror("錯誤", "請完整填寫所有欄位")
            return
        cur = self.conn.cursor()
        # 若帳號或名稱變動，建議也做重複檢查（可再加強）
        cur.execute("""
            UPDATE user SET user_accont=%s, password=%s, name=%s, user_type=%s WHERE name=%s
        """, (acc, pw, new_name, user_type, ori_name))
        self.conn.commit()
        messagebox.showinfo("完成", "使用者資訊已更新")
        self.load_user_names()
        self.name_combo.set(new_name)

    def refresh(self):
        self.load_user_names()
        self.clear_entries()
        self.name_combo.set("請選擇使用者")

class UserDeleteFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn

        tk.Label(self, text="使用者刪除", font=('Microsoft YaHei', 36, "bold")).pack(pady=40)
        main_frame = tk.Frame(self)
        main_frame.pack(pady=10)

        # 使用者名稱下拉選單
        tk.Label(main_frame, text="使用者名稱：", font=('Microsoft YaHei', 20)).grid(row=0, column=0, sticky="e", pady=10)
        self.name_combo = ttk.Combobox(main_frame, font=('Microsoft YaHei', 16), width=22, state="readonly")
        self.name_combo.grid(row=0, column=1, pady=10, sticky="w")
        self.name_combo.bind("<<ComboboxSelected>>", self.fill_user_info)

        # 只顯示不可編輯資料
        tk.Label(main_frame, text="使用者帳號：", font=('Microsoft YaHei', 20)).grid(row=1, column=0, sticky="e", pady=10)
        self.acc_label = tk.Label(main_frame, text="顯示的使用者帳號", font=('Microsoft YaHei', 16), width=22, bg="#888", fg="#fff", anchor="w")
        self.acc_label.grid(row=1, column=1, pady=10, sticky="w")

        tk.Label(main_frame, text="使用者密碼：", font=('Microsoft YaHei', 20)).grid(row=2, column=0, sticky="e", pady=10)
        self.pw_label = tk.Label(main_frame, text="顯示的使用者密碼", font=('Microsoft YaHei', 16), width=22, bg="#888", fg="#fff", anchor="w")
        self.pw_label.grid(row=2, column=1, pady=10, sticky="w")

        tk.Label(main_frame, text="使用者類別：", font=('Microsoft YaHei', 20)).grid(row=3, column=0, sticky="e", pady=10)
        self.type_label = tk.Label(main_frame, text="顯示的使用者類別", font=('Microsoft YaHei', 16), width=22, bg="#888", fg="#fff", anchor="w")
        self.type_label.grid(row=3, column=1, pady=10, sticky="w")

        # 刪除按鈕
        tk.Button(self, text="刪除使用者", font=('Microsoft YaHei', 20), command=self.delete_user)\
            .place(relx=0.85, rely=0.85)

        # 返回按鈕
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16), command=lambda: switch_frame("user_menu"))\
            .place(x=15, y=15)

        self.load_user_names()

    def load_user_names(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM user")
        names = [row[0] for row in cur.fetchall()]
        self.name_combo['values'] = names
        self.name_combo.set("請選擇使用者")
        self.clear_labels()

    def fill_user_info(self, event=None):
        user_name = self.name_combo.get()
        if not user_name or user_name == "請選擇使用者":
            self.clear_labels()
            return
        cur = self.conn.cursor()
        cur.execute("SELECT user_accont, password, user_type FROM user WHERE name=%s", (user_name,))
        row = cur.fetchone()
        if row:
            self.acc_label.config(text=row[0])
            self.pw_label.config(text=row[1])
            self.type_label.config(text=row[2])
        else:
            self.clear_labels()

    def clear_labels(self):
        self.acc_label.config(text="使用者帳號")
        self.pw_label.config(text="使用者密碼")
        self.type_label.config(text="使用者類別")

    def delete_user(self):
        user_name = self.name_combo.get()
        if not user_name or user_name == "使用者下拉選單":
            messagebox.showerror("錯誤", "請選擇要刪除的使用者")
            return
        if not messagebox.askyesno("確認刪除", f"確定要刪除「{user_name}」嗎？此操作無法還原！"):
            return
        cur = self.conn.cursor()
        cur.execute("DELETE FROM user WHERE name=%s", (user_name,))
        self.conn.commit()
        messagebox.showinfo("完成", f"已刪除使用者：{user_name}")
        self.load_user_names()
    def refresh(self):
        self.load_user_names()
        self.clear_labels()
        self.name_combo.set("請選擇使用者")

class OrderMenuFrame(tk.Frame):
    def __init__(self, master, switch_frame):
        super().__init__(master)
        tk.Label(self, text="").pack(pady=60)
        tk.Label(self, text="訂單記錄系統", font=('Microsoft YaHei',36)).pack(pady=90)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 12), command=lambda: switch_frame("agent_menu")).place(x=5, y=5)
        tk.Button(btn_frame, text="訂單新增", font=('Microsoft YaHei', 24), command=lambda: switch_frame("order_add")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="訂單查詢", font=('Microsoft YaHei', 24), command=lambda: switch_frame("order_query")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="訂單修改", font=('Microsoft YaHei', 24), command=lambda: switch_frame("order_mod")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="訂單刪除", font=('Microsoft YaHei', 24), command=lambda: switch_frame("order_delete")).pack(side="left", padx=10)

class OrderAddFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn
        self.switch_frame = switch_frame

        tk.Label(self, text="訂單新增", font=('Microsoft YaHei',36)).pack(pady=20)
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 12), command=lambda: switch_frame("order_menu")).place(x=5, y=5)

        # 置中容器
        self.center_frame = tk.Frame(self)
        self.center_frame.pack()

        # 上方顧客、日期
        tk.Label(self.center_frame, text="顧客名稱：").grid(row=0, column=0, pady=0, sticky="e")
        self.cust_combo = ttk.Combobox(self.center_frame, state="readonly", width=20)
        self.cust_combo.grid(row=0, column=1, pady=10)

        tk.Label(self.center_frame, text="訂單日期：").grid(row=0, column=2, sticky="e")
        self.date_entry = DateEntry(self.center_frame, date_pattern="yyyy-mm-dd")
        self.date_entry.grid(row=0, column=3, pady=10)

        # ====== 商品選擇標題區 ======
        tk.Label(self.center_frame, text="商品", font=('Microsoft YaHei', 16)).grid(row=1, column=0, pady=(10, 0))
        tk.Label(self.center_frame, text="數量", font=('Microsoft YaHei', 16)).grid(row=1, column=1, pady=(10, 0))
        tk.Label(self.center_frame, text="單價", font=('Microsoft YaHei', 16)).grid(row=1, column=2, pady=(10, 0))
        tk.Label(self.center_frame, text="小結", font=('Microsoft YaHei', 16)).grid(row=1, column=3, pady=(10, 0))
        # ====== 商品選擇區 ======
        self.product_combo = ttk.Combobox(self.center_frame, state="readonly", width=20)
        self.product_combo.grid(row=2, column=0, padx=5, pady=5)
        self.product_combo.bind("<<ComboboxSelected>>", self.show_price)

        self.qty_entry = tk.Entry(self.center_frame, width=8)
        self.qty_entry.grid(row=2, column=1, padx=5, pady=5)
        self.qty_entry.bind("<KeyRelease>", self.update_subtotal)

        self.price_var = tk.StringVar()
        tk.Label(self.center_frame, textvariable=self.price_var, width=10).grid(row=2, column=2, padx=5)

        self.subtotal_var = tk.StringVar()
        tk.Label(self.center_frame, textvariable=self.subtotal_var, width=10).grid(row=2, column=3, padx=5)

        tk.Button(self.center_frame, text="+", command=self.add_item).grid(row=2, column=4, padx=5)

        # ====== 已選商品區 ======
        self.items_frame = tk.Frame(self.center_frame)
        self.items_frame.grid(row=3, column=0, columnspan=5, pady=20)

        # ====== 右下角 ======
        self.total_var = tk.StringVar(value="0")
        self.right_bottom_frame = tk.Frame(self)
        self.right_bottom_frame.place(relx=1.0, rely=1.0, anchor="se")

        tk.Label(self.right_bottom_frame, text="總金額：", font=('Microsoft YaHei', 16)).grid(row=0, column=0)
        tk.Label(self.right_bottom_frame, textvariable=self.total_var, font=('Microsoft YaHei', 16)).grid(row=0, column=1)
        tk.Button(self.right_bottom_frame, text="新增訂單", font=('Microsoft YaHei', 16), command=self.submit_order).grid(row=1, column=0, columnspan=2, pady=10)

        self.selected_items = []

        self.load_customers()
        self.load_products()

    def refresh(self):
        """Reload combobox data and clear current selections."""
        self.load_customers()
        self.load_products()
        self.cust_combo.set('')
        self.product_combo.set('')
        self.qty_entry.delete(0, tk.END)
        self.price_var.set('')
        self.subtotal_var.set('')
        self.selected_items.clear()
        self.refresh_items()
        self.total_var.set('0')

    def load_customers(self):
        cur = self.conn.cursor()
        cur.execute("SELECT cust_name FROM customer")
        custs = [row[0] for row in cur.fetchall()]
        self.cust_combo["values"] = custs

    def load_products(self):
        cur = self.conn.cursor()
        cur.execute("SELECT product_name FROM product")
        prods = [row[0] for row in cur.fetchall()]
        self.product_combo["values"] = prods

    def show_price(self, event=None):
        prod = self.product_combo.get()
        cur = self.conn.cursor()
        cur.execute("SELECT price FROM product WHERE product_name=%s", (prod,))
        price = cur.fetchone()
        price_val = price[0] if price else 0
        self.price_var.set(str(price_val))
        self.update_subtotal()

    def update_subtotal(self, event=None):
        try:
            qty = int(self.qty_entry.get())
            price = int(self.price_var.get())
            subtotal = qty * price
            self.subtotal_var.set(str(subtotal))
        except:
            self.subtotal_var.set("0")

    def add_item(self):
        prod = self.product_combo.get()
        qty = self.qty_entry.get()
        price = self.price_var.get()
        subtotal = self.subtotal_var.get()
        if not (prod and qty.isdigit() and int(qty) > 0):
            messagebox.showwarning("輸入錯誤", "請選商品並輸入數量")
            return
        # 檢查是否重複
        for item in self.selected_items:
            if item["product"] == prod:
                messagebox.showwarning("重複商品", "該商品已選")
                return
        item = {"product": prod, "qty": int(qty), "price": int(price), "subtotal": int(subtotal)}
        self.selected_items.append(item)
        self.refresh_items()

    def refresh_items(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        total = 0
        for i, item in enumerate(self.selected_items):
            tk.Label(self.items_frame, text=item["product"], width=15).grid(row=i, column=0)
            tk.Label(self.items_frame, text=item["qty"], width=8).grid(row=i, column=1)
            tk.Label(self.items_frame, text=item["price"], width=10).grid(row=i, column=2)
            tk.Label(self.items_frame, text=item["subtotal"], width=10).grid(row=i, column=3)
            tk.Button(self.items_frame, text="❌", command=lambda idx=i: self.del_item(idx)).grid(row=i, column=4)
            total += item["subtotal"]
        self.total_var.set(str(total))

    def del_item(self, idx):
        self.selected_items.pop(idx)
        self.refresh_items()

    def submit_order(self):
        cust_name = self.cust_combo.get()
        order_date = self.date_entry.get_date()
        total = self.total_var.get()
        items = self.selected_items

        if not cust_name or not items:
            messagebox.showwarning("資料不完整", "請選擇顧客並新增至少一項商品！")
            return

        # 取得顧客編號
        cur = self.conn.cursor()
        cur.execute("SELECT cust_num FROM customer WHERE cust_name=%s", (cust_name,))
        cust_row = cur.fetchone()
        if not cust_row:
            messagebox.showerror("錯誤", "查無此顧客")
            return
        cust_num = cust_row[0]

        # 取得目前登入的user_num（登入驗證還沒做）
        # 實際上要根據登入資訊記錄user_num，這裡暫時都是2(2是testAdmin)
        user_num = getattr(self.master, "current_user_num", 2)

        try:
            # 新增order
            cur.execute("INSERT INTO `order` (order_date, amount, agent, customer) VALUES (%s, %s, %s, %s)",
                        (order_date, total, user_num, cust_num))
            self.conn.commit()
            order_num = cur.lastrowid

            # 新增order_recipe
            prod_nums = []
            for item in items:
                cur.execute("SELECT product_num FROM product WHERE product_name=%s", (item["product"],))
                prod_row = cur.fetchone()
                if not prod_row:
                    raise Exception("查無商品")
                prod_num = prod_row[0]
                prod_nums.append(prod_num)
                cur.execute(
                    "INSERT INTO order_receipt (order_num, product_num, quantity, price, sum) VALUES (%s, %s, %s, %s, %s)",
                    (order_num, prod_num, item["qty"], item["price"], item["subtotal"]),
                )
            self.conn.commit()
            for pn in prod_nums:
                warn_below_safe_stock(self.conn, pn)
            messagebox.showinfo("成功", "訂單新增成功！")
            self.selected_items.clear()
            self.refresh_items()
            # 可視情況切換頁面
            # self.switch_frame("order_menu")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("新增失敗", str(e))

    def refresh(self):
        """Reload combobox data and clear current selections."""
        self.load_customers()
        self.load_products()
        self.cust_combo.set('')
        self.product_combo.set('')
        self.qty_entry.delete(0, tk.END)
        self.price_var.set('')
        self.subtotal_var.set('')
        self.selected_items.clear()
        self.refresh_items()
        self.total_var.set('0')

class OrderQueryFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn
        self.switch_frame = switch_frame

        # 回到上一頁按鈕
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16), command=lambda: switch_frame("order_menu")).place(x=20, y=20)

        # 標題
        tk.Label(self, text="訂單查詢", font=('Microsoft YaHei',36)).pack(pady=40)

        # 置中 frame
        center = tk.Frame(self)
        center.pack(pady=30)

        # 顧客名稱
        tk.Label(center, text="顧客名稱：", font=('Microsoft YaHei', 20)).grid(row=0, column=0, sticky="e", pady=20, padx=10)
        self.cust_combo = ttk.Combobox(center, font=('Microsoft YaHei', 16), state="readonly", width=18)
        self.cust_combo.grid(row=0, column=1, padx=10)

        # 訂單日期
        tk.Label(center, text="訂單日期：", font=('Microsoft YaHei', 20)).grid(row=1, column=0, sticky="e", pady=20, padx=10)
        self.date_combo = ttk.Combobox(center, font=('Microsoft YaHei', 16), state="readonly", width=18)
        self.date_combo.grid(row=1, column=1, padx=10)

        # 商品
        tk.Label(center, text="商品：", font=('Microsoft YaHei', 20)).grid(row=2, column=0, sticky="e", pady=20, padx=10)
        self.product_combo = ttk.Combobox(center, font=('Microsoft YaHei', 16), state="readonly", width=18)
        self.product_combo.grid(row=2, column=1, padx=10)

        # 查詢按鈕
        tk.Button(self, text="查詢訂單", font=('Microsoft YaHei', 20), width=12,
                  command=self.query_order).place(relx=0.9, rely=0.9, anchor="se")

        # 載入下拉選單資料
        self.load_comboboxes()

    def refresh(self):
        """Reload combobox data and clear selections."""
        self.load_comboboxes()
        self.cust_combo.set('')
        self.date_combo.set('')
        self.product_combo.set('')

    def load_comboboxes(self):
        # 載入顧客
        cur = self.conn.cursor()
        cur.execute("SELECT cust_name FROM customer")
        custs = [row[0] for row in cur.fetchall()]
        self.cust_combo["values"] = [""] + custs

        # 載入所有訂單日期
        cur.execute("SELECT DISTINCT order_date FROM `order` ORDER BY order_date DESC")
        dates = [row[0].strftime("%Y-%m-%d") for row in cur.fetchall()]
        self.date_combo["values"] = [""] + dates

        # 載入商品名稱
        cur.execute("SELECT product_name FROM product")
        prods = [row[0] for row in cur.fetchall()]
        self.product_combo["values"] = [""] + prods

    def query_order(self):
        cust = self.cust_combo.get()
        date = self.date_combo.get()
        prod = self.product_combo.get()

        cur = self.conn.cursor()

        # 組查詢語法
        sql = """
            SELECT o.order_num, c.cust_name, o.order_date, p.product_name, orc.quantity, orc.price, orc.sum
            FROM `order` o
            JOIN customer c ON o.customer = c.cust_num
            JOIN order_receipt orc ON o.order_num = orc.order_num
            JOIN product p ON orc.product_num = p.product_num
            WHERE 1=1
        """
        params = []
        if cust:
            sql += " AND c.cust_name = %s"
            params.append(cust)
        if date:
            sql += " AND o.order_date = %s"
            params.append(date)
        if prod:
            sql += " AND p.product_name = %s"
            params.append(prod)
        sql += " ORDER BY o.order_num ASC"

        cur.execute(sql, params)
        results = cur.fetchall()

        # 顯示結果
        if not results:
            messagebox.showinfo("查詢結果", "查無符合條件的訂單。")
            return

        # 定義每個欄位寬度
        fmt = "{:<8} {:<12} {:<12} {:<12} {:>6} {:>8} {:>8}\n"
        result_text = fmt.format("訂單編號", "顧客", "日期", "商品", "數量", "單價", "小結")
        result_text += "-"*70 + "\n"
        for row in results:
            result_text += fmt.format(str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4]), str(row[5]), str(row[6]))

        # 彈窗顯示
        result_win = tk.Toplevel(self)
        result_win.title("查詢結果")
        result_win_width = 960
        result_win_height = 400
        result_win_anchor_left = int((result_win.winfo_screenwidth() - result_win_width)/2) #置中視窗
        result_win_anchor_top = int((result_win.winfo_screenheight() - result_win_height)/2)
        result_win.geometry(f'{result_win_width}x{result_win_height}+{result_win_anchor_left}+{result_win_anchor_top}')
        text = tk.Text(result_win, font=("Consolas", 14), width=70, height=20)
        text.insert(tk.END, result_text)
        text.config(state=tk.DISABLED)
        text.pack(expand=True, fill="both", padx=15, pady=15)

class OrderModFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn
        self.switch_frame = switch_frame
        self.selected_items = []

        # 回上一頁
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16),
                  command=lambda: switch_frame("order_menu"),).place(x=20, y=20)

        # 標題
        tk.Label(self, text="訂單修改", font=('Microsoft YaHei',36)).pack(pady=10)

        # 置中 frame
        center = tk.Frame(self)
        center.pack(pady=15)

        # 左側查詢區塊
        tk.Label(center, text="顧客名稱：", font=('Microsoft YaHei', 16)).grid(row=0, column=0, pady=10, sticky="e")
        self.cust_combo = ttk.Combobox(center, font=('Microsoft YaHei', 14), state="readonly", width=16)
        self.cust_combo.grid(row=0, column=1, padx=8)
        self.cust_combo.bind("<<ComboboxSelected>>", self.update_dates)

        tk.Label(center, text="訂單日期：", font=('Microsoft YaHei', 16)).grid(row=1, column=0, pady=10, sticky="e")
        self.date_combo = ttk.Combobox(center, font=('Microsoft YaHei', 14), state="readonly", width=16)
        self.date_combo.grid(row=1, column=1, padx=8)
        self.date_combo.bind("<<ComboboxSelected>>", self.update_orders)

        tk.Label(center, text="訂單編號：", font=('Microsoft YaHei', 16)).grid(row=2, column=0, pady=10, sticky="e")
        self.order_combo = ttk.Combobox(center, font=('Microsoft YaHei', 14), state="readonly", width=16)
        self.order_combo.grid(row=2, column=1, padx=8)
        self.order_combo.bind("<<ComboboxSelected>>", self.load_order_details)

        # 明細表頭
        table = tk.Frame(self)
        table.pack(pady=10)
        for i, txt in enumerate(["商品", "數量", "單價", "小結", ""]):
            tk.Label(table, text=txt, font=('Microsoft YaHei', 16, "bold")).grid(row=0, column=i, padx=10)

        # 商品明細
        self.items_frame = tk.Frame(self)
        self.items_frame.pack()

        # 商品選擇區
        self.product_combo = ttk.Combobox(self.items_frame, font=('Microsoft YaHei', 14), state="readonly", width=15)
        self.qty_entry = tk.Entry(self.items_frame, font=('Microsoft YaHei', 14), width=8)
        self.price_var = tk.StringVar()
        tk.Label(self.items_frame, textvariable=self.price_var, font=('Microsoft YaHei', 14), width=10).grid(row=0, column=2)
        self.subtotal_var = tk.StringVar()
        tk.Label(self.items_frame, textvariable=self.subtotal_var, font=('Microsoft YaHei', 14), width=10).grid(row=0, column=3)
        tk.Button(self.items_frame, text="+", font=('Microsoft YaHei', 14), width=2, command=self.add_item).grid(row=0, column=4)
        self.product_combo.grid(row=0, column=0)
        self.qty_entry.grid(row=0, column=1)
        self.product_combo.bind("<<ComboboxSelected>>", self.update_price)
        self.qty_entry.bind("<KeyRelease>", self.update_subtotal)

        # 總金額與修改按鈕
        self.total_var = tk.StringVar(value="0")
        tk.Label(self, text="總金額：", font=('Microsoft YaHei', 16)).place(relx=0.70, rely=0.82)
        tk.Label(self, textvariable=self.total_var, font=('Microsoft YaHei', 16)).place(relx=0.76, rely=0.82)
        tk.Button(self, text="修改訂單", font=('Microsoft YaHei', 16), width=12,
                  command=self.update_order).place(relx=0.83, rely=0.9)

        self.load_customers()
        self.load_products()

    def refresh(self):
        """Reload dropdown values and clear selections."""
        self.load_customers()
        self.load_products()
        self.cust_combo.set('')
        self.date_combo.set('')
        self.order_combo.set('')
        self.clear_items()

    def load_customers(self):
        cur = self.conn.cursor()
        cur.execute("SELECT cust_name FROM customer")
        self.cust_combo["values"] = [row[0] for row in cur.fetchall()]

    def update_dates(self, event=None):
        cust = self.cust_combo.get()
        cur = self.conn.cursor()
        cur.execute("""SELECT DISTINCT o.order_date 
                       FROM `order` o 
                       JOIN customer c ON o.customer = c.cust_num 
                       WHERE c.cust_name=%s
                       ORDER BY o.order_date""", (cust,))
        self.date_combo["values"] = [row[0].strftime("%Y-%m-%d") for row in cur.fetchall()]
        self.date_combo.set("")
        self.order_combo.set("")
        self.clear_items()

    def update_orders(self, event=None):
        cust = self.cust_combo.get()
        date = self.date_combo.get()
        cur = self.conn.cursor()
        cur.execute("""SELECT o.order_num 
                       FROM `order` o 
                       JOIN customer c ON o.customer = c.cust_num 
                       WHERE c.cust_name=%s AND o.order_date=%s""", (cust, date))
        self.order_combo["values"] = [str(row[0]) for row in cur.fetchall()]
        self.order_combo.set("")
        self.clear_items()

    def load_products(self):
        cur = self.conn.cursor()
        cur.execute("SELECT product_name FROM product")
        self.products = [row[0] for row in cur.fetchall()]
        self.product_combo["values"] = self.products

    def update_price(self, event=None):
        prod = self.product_combo.get()
        cur = self.conn.cursor()
        cur.execute("SELECT price FROM product WHERE product_name=%s", (prod,))
        price = cur.fetchone()
        self.price_var.set(str(price[0]) if price else "0")
        self.update_subtotal()

    def update_subtotal(self, event=None):
        try:
            qty = int(self.qty_entry.get())
            price = int(self.price_var.get())
            self.subtotal_var.set(str(qty * price))
        except:
            self.subtotal_var.set("0")

    def add_item(self):
        prod = self.product_combo.get()
        qty = self.qty_entry.get()
        price = self.price_var.get()
        subtotal = self.subtotal_var.get()
        if not (prod and qty.isdigit() and int(qty) > 0):
            messagebox.showwarning("輸入錯誤", "請選商品並輸入正確數量")
            return
        for item in self.selected_items:
            if item["product"] == prod:
                messagebox.showwarning("重複商品", "該商品已在明細中")
                return
        item = {"product": prod, "qty": int(qty), "price": int(price), "subtotal": int(subtotal)}
        self.selected_items.append(item)
        self.refresh_items()

    def clear_items(self):
        self.selected_items.clear()
        self.refresh_items()
        self.total_var.set("0")

    def load_order_details(self, event=None):
        self.selected_items.clear()
        order_num = self.order_combo.get()
        cur = self.conn.cursor()
        cur.execute("""
            SELECT p.product_name, r.quantity, r.price, r.sum
            FROM order_receipt r
            JOIN product p ON r.product_num = p.product_num
            WHERE r.order_num = %s
        """, (order_num,))
        for prod, qty, price, subtotal in cur.fetchall():
            self.selected_items.append({"product": prod, "qty": qty, "price": price, "subtotal": subtotal})
        self.refresh_items()

    def refresh_items(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        # 第一行是新增
        self.product_combo = ttk.Combobox(self.items_frame, font=('Microsoft YaHei', 14), state="readonly", width=15, values=self.products)
        self.qty_entry = tk.Entry(self.items_frame, font=('Microsoft YaHei', 14), width=8)
        self.price_var = tk.StringVar()
        self.subtotal_var = tk.StringVar()
        tk.Label(self.items_frame, textvariable=self.price_var, font=('Microsoft YaHei', 14), width=10).grid(row=0, column=2)
        tk.Label(self.items_frame, textvariable=self.subtotal_var, font=('Microsoft YaHei', 14), width=10).grid(row=0, column=3)
        self.product_combo.grid(row=0, column=0)
        self.qty_entry.grid(row=0, column=1)
        tk.Button(self.items_frame, text="+", font=('Microsoft YaHei', 14), width=2, command=self.add_item).grid(row=0, column=4)
        self.product_combo.bind("<<ComboboxSelected>>", self.update_price)
        self.qty_entry.bind("<KeyRelease>", self.update_subtotal)
        # 已選明細
        for i, item in enumerate(self.selected_items, start=1):
            tk.Label(self.items_frame, text=item["product"], font=('Microsoft YaHei', 14), width=15).grid(row=i, column=0)
            qty_entry = tk.Entry(self.items_frame, font=('Microsoft YaHei', 14), width=8)
            qty_entry.insert(0, str(item["qty"]))
            qty_entry.grid(row=i, column=1)
            qty_entry.bind("<KeyRelease>", lambda e, idx=i-1: self.modify_qty(idx, qty_entry))
            tk.Label(self.items_frame, text=item["price"], font=('Microsoft YaHei', 14), width=10).grid(row=i, column=2)
            subtotal_label = tk.Label(self.items_frame, text=item["qty"] * item["price"], font=('Microsoft YaHei', 14), width=10)
            subtotal_label.grid(row=i, column=3)
            tk.Button(self.items_frame, text="❌", command=lambda idx=i-1: self.del_item(idx), font=('Microsoft YaHei', 14)).grid(row=i, column=4)
        # 計算總金額
        total = sum(item["qty"] * item["price"] for item in self.selected_items)
        self.total_var.set(str(total))

    def modify_qty(self, idx, entry):
        try:
            qty = int(entry.get())
            self.selected_items[idx]["qty"] = qty
            self.selected_items[idx]["subtotal"] = qty * self.selected_items[idx]["price"]
            self.refresh_items()
        except:
            pass

    def del_item(self, idx):
        self.selected_items.pop(idx)
        self.refresh_items()

    def update_order(self):
        if not self.selected_items or not self.order_combo.get():
            messagebox.showwarning("錯誤", "請先選擇訂單並確保有明細")
            return
        order_num = int(self.order_combo.get())
        total = sum(item["qty"] * item["price"] for item in self.selected_items)
        try:
            cur = self.conn.cursor()
            # 更新主檔
            cur.execute("UPDATE `order` SET amount=%s WHERE order_num=%s", (total, order_num))
            # 刪除舊明細
            cur.execute("DELETE FROM order_receipt WHERE order_num=%s", (order_num,))
            # 新增新明細
            for item in self.selected_items:
                cur.execute("""
                    INSERT INTO order_receipt (order_num, product_num, quantity, price, sum)
                    VALUES (%s, (SELECT product_num FROM product WHERE product_name=%s), %s, %s, %s)
                """, (order_num, item["product"], item["qty"], item["price"], item["subtotal"]))
            self.conn.commit()
            messagebox.showinfo("成功", "訂單已成功修改！")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("錯誤", f"訂單修改失敗：{e}")

class OrderDeleteFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn
        self.switch_frame = switch_frame

        # 回上一頁
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16),
                  command=lambda: switch_frame("order_menu")).place(x=20, y=20)

        # 標題
        tk.Label(self, text="訂單刪除", font=('Microsoft YaHei',36)).pack(pady=10)

        # 置中 frame
        center = tk.Frame(self)
        center.pack(pady=15)

        # 左側查詢區塊
        tk.Label(center, text="顧客名稱：", font=('Microsoft YaHei', 16)).grid(row=0, column=0, pady=10, sticky="e")
        self.cust_combo = ttk.Combobox(center, font=('Microsoft YaHei', 14), state="readonly", width=16)
        self.cust_combo.grid(row=0, column=1, padx=8)
        self.cust_combo.bind("<<ComboboxSelected>>", self.update_dates)

        tk.Label(center, text="訂單日期：", font=('Microsoft YaHei', 16)).grid(row=1, column=0, pady=10, sticky="e")
        self.date_combo = ttk.Combobox(center, font=('Microsoft YaHei', 14), state="readonly", width=16)
        self.date_combo.grid(row=1, column=1, padx=8)
        self.date_combo.bind("<<ComboboxSelected>>", self.update_orders)

        tk.Label(center, text="訂單編號：", font=('Microsoft YaHei', 16)).grid(row=2, column=0, pady=10, sticky="e")
        self.order_combo = ttk.Combobox(center, font=('Microsoft YaHei', 14), state="readonly", width=16)
        self.order_combo.grid(row=2, column=1, padx=8)
        self.order_combo.bind("<<ComboboxSelected>>", self.load_order_details)

        # 明細表頭
        table = tk.Frame(self)
        table.pack(pady=10)
        for i, txt in enumerate(["商品", "數量", "單價", "小結"]):
            tk.Label(table, text=txt, font=('Microsoft YaHei', 16, "bold")).grid(row=0, column=i, padx=10)

        # 商品明細
        self.items_frame = tk.Frame(self)
        self.items_frame.pack()

        # 總金額與刪除按鈕
        self.total_var = tk.StringVar(value="0")
        tk.Label(self, text="總金額：", font=('Microsoft YaHei', 16)).place(relx=0.70, rely=0.82)
        tk.Label(self, textvariable=self.total_var, font=('Microsoft YaHei', 16)).place(relx=0.76, rely=0.82)
        tk.Button(self, text="刪除訂單", font=('Microsoft YaHei', 16), width=12,
                  command=self.delete_order).place(relx=0.83, rely=0.9)

        self.load_customers()

    def refresh(self):
        """Reload combobox data and clear selections."""
        self.load_customers()
        self.cust_combo.set('')
        self.date_combo.set('')
        self.order_combo.set('')
        self.clear_items()

    def load_customers(self):
        cur = self.conn.cursor()
        cur.execute("SELECT cust_name FROM customer")
        self.cust_combo["values"] = [row[0] for row in cur.fetchall()]

    def update_dates(self, event=None):
        cust = self.cust_combo.get()
        cur = self.conn.cursor()
        cur.execute("""SELECT DISTINCT o.order_date 
                       FROM `order` o 
                       JOIN customer c ON o.customer = c.cust_num 
                       WHERE c.cust_name=%s
                       ORDER BY o.order_date""", (cust,))
        self.date_combo["values"] = [row[0].strftime("%Y-%m-%d") for row in cur.fetchall()]
        self.date_combo.set("")
        self.order_combo.set("")
        self.clear_items()

    def update_orders(self, event=None):
        cust = self.cust_combo.get()
        date = self.date_combo.get()
        cur = self.conn.cursor()
        cur.execute("""SELECT o.order_num 
                       FROM `order` o 
                       JOIN customer c ON o.customer = c.cust_num 
                       WHERE c.cust_name=%s AND o.order_date=%s""", (cust, date))
        self.order_combo["values"] = [str(row[0]) for row in cur.fetchall()]
        self.order_combo.set("")
        self.clear_items()

    def clear_items(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        self.total_var.set("0")

    def load_order_details(self, event=None):
        self.clear_items()
        order_num = self.order_combo.get()
        if not order_num:
            return
        cur = self.conn.cursor()
        cur.execute("""
            SELECT p.product_name, r.quantity, r.price, r.sum
            FROM order_receipt r
            JOIN product p ON r.product_num = p.product_num
            WHERE r.order_num = %s
        """, (order_num,))
        total = 0
        for i, (prod, qty, price, subtotal) in enumerate(cur.fetchall()):
            tk.Label(self.items_frame, text=prod, font=('Microsoft YaHei', 14), width=15).grid(row=i, column=0)
            tk.Label(self.items_frame, text=qty, font=('Microsoft YaHei', 14), width=8).grid(row=i, column=1)
            tk.Label(self.items_frame, text=price, font=('Microsoft YaHei', 14), width=10).grid(row=i, column=2)
            tk.Label(self.items_frame, text=subtotal, font=('Microsoft YaHei', 14), width=10).grid(row=i, column=3)
            total += subtotal
        self.total_var.set(str(total))

    def delete_order(self):
        order_num = self.order_combo.get()
        if not order_num:
            messagebox.showwarning("錯誤", "請先選擇訂單")
            return
        if messagebox.askyesno("確認", "確定要刪除此訂單？此操作不可復原。"):
            try:
                cur = self.conn.cursor()
                cur.execute("DELETE FROM order_receipt WHERE order_num=%s", (order_num,))
                cur.execute("DELETE FROM `order` WHERE order_num=%s", (order_num,))
                self.conn.commit()
                messagebox.showinfo("成功", "訂單已刪除")
                self.clear_items()
                self.update_orders()
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("錯誤", f"訂單刪除失敗：{e}")

class CustomerMenuFrame(tk.Frame):
    def __init__(self, master, switch_frame):
        super().__init__(master)
        tk.Label(self, text="").pack(pady=60)
        tk.Label(self, text="顧客維護系統", font=('Microsoft YaHei',36)).pack(pady=90)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 12), command=lambda: switch_frame("agent_menu")).place(x=5, y=5)
        tk.Button(btn_frame, text="顧客新增", font=('Microsoft YaHei', 24), command=lambda: switch_frame("customer_add")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="顧客查詢", font=('Microsoft YaHei', 24), command=lambda: switch_frame("customer_query")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="顧客修改", font=('Microsoft YaHei', 24), command=lambda: switch_frame("customer_mod")).pack(side="left", padx=10)

class CustomerAddFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn
        self.switch_frame = switch_frame

        # 回上一頁按鈕
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16),
                  command=lambda: switch_frame("customer_menu")).place(x=20, y=20)

        # 標題
        tk.Label(self, text="顧客新增", font=('Microsoft YaHei',36)).pack(pady=40)

        # 置中 Frame
        center = tk.Frame(self)
        center.pack(pady=20)

        # 顧客名稱
        tk.Label(center, text="顧客名稱：", font=('Microsoft YaHei', 18)).grid(row=0, column=0, pady=15, sticky="e")
        self.name_entry = tk.Entry(center, font=('Microsoft YaHei', 16), width=18)
        self.name_entry.insert(0, "輸入顧客名稱")
        self.name_entry.grid(row=0, column=1, padx=10)
        self.name_entry.bind("<FocusIn>", lambda e: self.name_entry.delete(0, tk.END))

        # 顧客地址
        tk.Label(center, text="顧客地址：", font=('Microsoft YaHei', 18)).grid(row=1, column=0, pady=15, sticky="e")
        self.addr_entry = tk.Entry(center, font=('Microsoft YaHei', 16), width=18)
        self.addr_entry.insert(0, "輸入顧客地址")
        self.addr_entry.grid(row=1, column=1, padx=10)
        self.addr_entry.bind("<FocusIn>", lambda e: self.addr_entry.delete(0, tk.END))

        # 顧客電話
        tk.Label(center, text="顧客電話：", font=('Microsoft YaHei', 18)).grid(row=2, column=0, pady=15, sticky="e")
        self.phone_entry = tk.Entry(center, font=('Microsoft YaHei', 16), width=18)
        self.phone_entry.insert(0, "輸入顧客電話")
        self.phone_entry.grid(row=2, column=1, padx=10)
        self.phone_entry.bind("<FocusIn>", lambda e: self.phone_entry.delete(0, tk.END))

        # 新增顧客按鈕
        tk.Button(self, text="新增顧客", font=('Microsoft YaHei', 18), width=12,
                  command=self.add_customer).place(relx=0.83, rely=0.83)

    def add_customer(self):
        name = self.name_entry.get().strip()
        addr = self.addr_entry.get().strip()
        phone = self.phone_entry.get().strip()

        if not name or not addr or not phone:
            messagebox.showwarning("輸入錯誤", "請完整填寫顧客資訊！")
            return

        try:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO customer (cust_name, cust_address, cust_phone) VALUES (%s, %s, %s)",
                        (name, addr, phone))
            self.conn.commit()
            messagebox.showinfo("新增成功", f"已新增顧客：{name}")
            self.name_entry.delete(0, tk.END)
            self.addr_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("資料庫錯誤", f"無法新增顧客：{e}")

class CustomerQueryFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn
        self.switch_frame = switch_frame

        # 回上一頁按鈕
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16),
                  command=lambda: switch_frame("customer_menu")).place(x=20, y=20)

        # 標題
        tk.Label(self, text="顧客查詢", font=('Microsoft YaHei',36)).pack(pady=60)

        # 置中 Frame
        center = tk.Frame(self)
        center.pack(pady=10)

        # 顧客名稱下拉
        tk.Label(center, text="顧客名稱：", font=('Microsoft YaHei', 18)).grid(row=0, column=0, pady=15, sticky="e")
        self.cust_combo = ttk.Combobox(center, font=('Microsoft YaHei', 16), state="readonly", width=18)
        self.cust_combo.grid(row=0, column=1, padx=10)
        self.load_customers()

        # 查詢顧客按鈕
        tk.Button(self, text="查詢顧客", font=('Microsoft YaHei', 18), width=12,
                  command=self.query_customer).place(relx=0.83, rely=0.83)

    def load_customers(self):
        cur = self.conn.cursor()
        cur.execute("SELECT cust_name FROM customer")
        custs = [row[0] for row in cur.fetchall()]
        self.cust_combo["values"] = custs

    def query_customer(self):
        cust_name = self.cust_combo.get()
        if not cust_name:
            messagebox.showwarning("提示", "請選擇顧客！")
            return
        cur = self.conn.cursor()
        cur.execute("SELECT cust_name, cust_address, cust_phone FROM customer WHERE cust_name=%s", (cust_name,))
        result = cur.fetchone()
        if result:
            info = f"顧客名稱：{result[0]}\n顧客地址：{result[1]}\n顧客電話：{result[2]}"
            show_info_popup("顧客資訊", info)
        else:
            messagebox.showerror("查無資料", "找不到該顧客資料。")
    
    def refresh(self):
        self.load_customers()
        self.cust_combo.set('')

class CustomerModFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn
        self.switch_frame = switch_frame

        # 回上一頁按鈕
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16),
                  command=lambda: switch_frame("customer_menu")).place(x=20, y=20)

        # 標題
        tk.Label(self, text="顧客修改", font=('Microsoft YaHei',36)).pack(pady=40)

        # 置中 Frame
        center = tk.Frame(self)
        center.pack(pady=10)

        # 顧客下拉
        tk.Label(center, text="顧客名稱：", font=('Microsoft YaHei', 18)).grid(row=0, column=0, pady=15, sticky="e")
        self.cust_combo = ttk.Combobox(center, font=('Microsoft YaHei', 16), state="readonly", width=18)
        self.cust_combo.grid(row=0, column=1, padx=10)
        self.cust_combo.bind("<<ComboboxSelected>>", self.on_select_customer)
        self.load_customers()

        # 可編輯欄位
        tk.Label(center, text="顧客名稱：", font=('Microsoft YaHei', 18)).grid(row=1, column=0, pady=15, sticky="e")
        self.entry_name = tk.Entry(center, font=('Microsoft YaHei', 16), width=18)
        self.entry_name.grid(row=1, column=1, padx=10)

        tk.Label(center, text="顧客地址：", font=('Microsoft YaHei', 18)).grid(row=2, column=0, pady=15, sticky="e")
        self.entry_address = tk.Entry(center, font=('Microsoft YaHei', 16), width=18)
        self.entry_address.grid(row=2, column=1, padx=10)

        tk.Label(center, text="顧客電話：", font=('Microsoft YaHei', 18)).grid(row=3, column=0, pady=15, sticky="e")
        self.entry_phone = tk.Entry(center, font=('Microsoft YaHei', 16), width=18)
        self.entry_phone.grid(row=3, column=1, padx=10)

        # 修改按鈕
        tk.Button(self, text="修改顧客", font=('Microsoft YaHei', 18), width=12,
                  command=self.update_customer).place(relx=0.83, rely=0.83)

    def load_customers(self):
        cur = self.conn.cursor()
        cur.execute("SELECT cust_name FROM customer")
        custs = [row[0] for row in cur.fetchall()]
        self.cust_combo["values"] = custs

    def on_select_customer(self, event=None):
        name = self.cust_combo.get()
        cur = self.conn.cursor()
        cur.execute("SELECT cust_name, cust_address, cust_phone FROM customer WHERE cust_name=%s", (name,))
        row = cur.fetchone()
        if row:
            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, row[0])
            self.entry_address.delete(0, tk.END)
            self.entry_address.insert(0, row[1])
            self.entry_phone.delete(0, tk.END)
            self.entry_phone.insert(0, row[2])
        else:
            self.entry_name.delete(0, tk.END)
            self.entry_address.delete(0, tk.END)
            self.entry_phone.delete(0, tk.END)

    def update_customer(self):
        ori_name = self.cust_combo.get()
        name = self.entry_name.get().strip()
        address = self.entry_address.get().strip()
        phone = self.entry_phone.get().strip()
        if not ori_name or not name:
            messagebox.showwarning("資料不足", "請選擇顧客並填寫完整資料")
            return
        cur = self.conn.cursor()
        sql = "UPDATE customer SET cust_name=%s, cust_address=%s, cust_phone=%s WHERE cust_name=%s"
        cur.execute(sql, (name, address, phone, ori_name))
        self.conn.commit()
        messagebox.showinfo("修改成功", f"已成功修改顧客 {ori_name}！")
        self.load_customers()
        self.cust_combo.set(name)  # 設定新的顧客名稱
    
    def refresh(self):
        self.load_customers()
        self.cust_combo.set('')
        self.entry_name.delete(0, tk.END)
        self.entry_address.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)

class ProductMenuFrame(tk.Frame):
    def __init__(self, master, switch_frame):
        super().__init__(master)
        tk.Label(self, text="").pack(pady=60)
        tk.Label(self, text="商品項目系統", font=('Microsoft YaHei',36)).pack(pady=90)
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 12), command=lambda: switch_frame("admin_menu")).place(x=5, y=5)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="商品新增", font=('Microsoft YaHei', 24), command=lambda: switch_frame("product_add")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="商品查詢", font=('Microsoft YaHei', 24), command=lambda: switch_frame("product_query")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="商品修改", font=('Microsoft YaHei', 24), command=lambda: switch_frame("product_mod")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="商品刪除", font=('Microsoft YaHei', 24), command=lambda: switch_frame("product_delete")).pack(side="left", padx=10)

class ProductAddFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn

        tk.Button(self, text="返回上一頁", font=("Microsoft YaHei", 16),
                  command=lambda: switch_frame("product_menu")).place(x=20, y=20)

        tk.Label(self, text="商品新增", font=("Microsoft YaHei", 36, "bold")).pack(pady=40)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=20)

        # 商品名稱
        tk.Label(form_frame, text="商品名稱：", font=("Microsoft YaHei", 18)).grid(row=0, column=0, pady=15, sticky="e")
        self.product_name_entry = tk.Entry(form_frame, font=("Microsoft YaHei", 14), width=18)
        self.product_name_entry.grid(row=0, column=1, pady=15)

        # 單價
        tk.Label(form_frame, text="單價：", font=("Microsoft YaHei", 18)).grid(row=1, column=0, pady=15, sticky="e")
        self.price_entry = tk.Entry(form_frame, font=("Microsoft YaHei", 14), width=18)
        self.price_entry.grid(row=1, column=1, pady=15)

        # 成本
        tk.Label(form_frame, text="成本：", font=("Microsoft YaHei", 18)).grid(row=2, column=0, pady=15, sticky="e")
        self.cost_entry = tk.Entry(form_frame, font=("Microsoft YaHei", 14), width=18)
        self.cost_entry.grid(row=2, column=1, pady=15)

        # 安全庫存
        tk.Label(form_frame, text="安全庫存：", font=("Microsoft YaHei", 18)).grid(row=3, column=0, pady=15, sticky="e")
        self.safe_stock_entry = tk.Entry(form_frame, font=("Microsoft YaHei", 14), width=18)
        self.safe_stock_entry.grid(row=3, column=1, pady=15)

        # 供應商下拉選單
        tk.Label(form_frame, text="供應商：", font=("Microsoft YaHei", 18)).grid(row=4, column=0, pady=15, sticky="e")
        self.supplier_combo = ttk.Combobox(form_frame, state="readonly", font=("Microsoft YaHei", 14), width=16)
        self.supplier_combo.grid(row=4, column=1, pady=15)
        self.load_suppliers()

        # 新增商品按鈕
        tk.Button(self, text="新增商品", font=("Microsoft YaHei", 18), width=12, 
                  command=self.add_product).place(relx=0.90, rely=0.90, anchor="center")

    def load_suppliers(self):
        cur = self.conn.cursor()
        cur.execute("SELECT sup_com FROM supplier")
        sup_com = [row[0] for row in cur.fetchall()]
        self.supplier_combo['values'] = sup_com

    def add_product(self):
        name = self.product_name_entry.get().strip()
        price = self.price_entry.get().strip()
        cost = self.cost_entry.get().strip()
        safe_stock = self.safe_stock_entry.get().strip()
        supplier = self.supplier_combo.get().strip()

        if not all([name, price, cost, safe_stock, supplier]):
            messagebox.showwarning("欄位缺漏", "所有欄位都必須填寫")
            return

        try:
            price = int(price)
            cost = int(cost)
            safe_stock = int(safe_stock)
        except ValueError:
            messagebox.showwarning("輸入錯誤", "單價、成本和安全庫存必須是數字")
            return

        # 查找 supplier 對應的 sup_num
        cur = self.conn.cursor()
        cur.execute("SELECT sup_num FROM supplier WHERE sup_com=%s", (supplier,))
        sup_num = cur.fetchone()
        if not sup_num:
            messagebox.showerror("供應商錯誤", "找不到對應的供應商")
            return
        sup_num = sup_num[0]

        # 寫入資料庫
        try:
            cur.execute(
                "INSERT INTO product (product_name, price, cost, supplier, safe_stock) VALUES (%s, %s, %s, %s, %s)",
                (name, price, cost, sup_num, safe_stock)
            )
            self.conn.commit()
            messagebox.showinfo("成功", "商品新增成功")
            # 清空欄位
            self.product_name_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            self.cost_entry.delete(0, tk.END)
            self.safe_stock_entry.delete(0, tk.END)
            self.supplier_combo.set('')
        except Exception as e:
            messagebox.showerror("新增失敗", f"錯誤原因：{e}")

class ProductQueryFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn
        self.show_info_popup = show_info_popup

        tk.Button(self, text="返回上一頁", font=("Microsoft YaHei", 16),
                  command=lambda: switch_frame("product_menu")).place(x=20, y=20)

        tk.Label(self, text="商品查詢", font=("Microsoft YaHei", 36, "bold")).pack(pady=40)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=40)

        tk.Label(form_frame, text="商品名稱：", font=("Microsoft YaHei", 18)).grid(row=0, column=0, pady=15, sticky="e")
        self.product_combo = ttk.Combobox(form_frame, state="readonly", font=("Microsoft YaHei", 14), width=18)
        self.product_combo.grid(row=0, column=1, pady=15)
        self.load_products()

        tk.Button(self, text="查詢商品", font=("Microsoft YaHei", 18), width=12, 
                  command=self.query_product).place(relx=0.90, rely=0.90, anchor="center")

    def load_products(self):
        cur = self.conn.cursor()
        cur.execute("SELECT product_name FROM product")
        names = [row[0] for row in cur.fetchall()]
        self.product_combo['values'] = names

    def query_product(self):
        product_name = self.product_combo.get().strip()
        if not product_name:
            messagebox.showwarning("未選擇", "請先選擇商品名稱")
            return

        cur = self.conn.cursor()
        cur.execute("""
            SELECT p.product_name, p.price, p.cost, p.safe_stock, s.sup_com
            FROM product p
            LEFT JOIN supplier s ON p.supplier = s.sup_num
            WHERE p.product_name = %s
        """, (product_name,))
        data = cur.fetchone()

        if data:
            info = (f"商品名稱：{data[0]}\n"
                    f"單價：{data[1]}\n"
                    f"成本：{data[2]}\n"
                    f"安全庫存：{data[3]}\n"
                    f"供應商：{data[4] if data[4] else '-'}")
            show_info_popup("商品資訊", info)
        else:
            messagebox.showinfo("查無資料", "找不到此商品的詳細資料")

    def refresh(self):
        self.load_products()
        self.product_combo.set('')

class ProductModFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn

        tk.Button(self, text="返回上一頁", font=("Microsoft YaHei", 16),
                  command=lambda: switch_frame("product_menu")).place(x=20, y=20)

        tk.Label(self, text="商品修改", font=("Microsoft YaHei", 36, "bold")).pack(pady=40)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=20)

        # 1. 商品下拉
        tk.Label(form_frame, text="商品名稱：", font=("Microsoft YaHei", 18)).grid(row=0, column=0, pady=12, sticky="e")
        self.product_combo = ttk.Combobox(form_frame, state="readonly", font=("Microsoft YaHei", 14), width=18)
        self.product_combo.grid(row=0, column=1, pady=12)
        self.product_combo.bind("<<ComboboxSelected>>", self.load_product_detail)

        # 2. 商品資訊欄
        tk.Label(form_frame, text="商品名稱：", font=("Microsoft YaHei", 18)).grid(row=1, column=0, pady=12, sticky="e")
        self.name_entry = tk.Entry(form_frame, font=("Microsoft YaHei", 14), width=20)
        self.name_entry.grid(row=1, column=1, pady=12)

        tk.Label(form_frame, text="單價：", font=("Microsoft YaHei", 18)).grid(row=2, column=0, pady=12, sticky="e")
        self.price_entry = tk.Entry(form_frame, font=("Microsoft YaHei", 14), width=20)
        self.price_entry.grid(row=2, column=1, pady=12)

        tk.Label(form_frame, text="成本：", font=("Microsoft YaHei", 18)).grid(row=3, column=0, pady=12, sticky="e")
        self.cost_entry = tk.Entry(form_frame, font=("Microsoft YaHei", 14), width=20)
        self.cost_entry.grid(row=3, column=1, pady=12)

        tk.Label(form_frame, text="安全庫存：", font=("Microsoft YaHei", 18)).grid(row=4, column=0, pady=12, sticky="e")
        self.safestock_entry = tk.Entry(form_frame, font=("Microsoft YaHei", 14), width=20)
        self.safestock_entry.grid(row=4, column=1, pady=12)

        tk.Label(form_frame, text="供應商：", font=("Microsoft YaHei", 18)).grid(row=5, column=0, pady=12, sticky="e")
        self.supplier_combo = ttk.Combobox(form_frame, state="readonly", font=("Microsoft YaHei", 14), width=18)
        self.supplier_combo.grid(row=5, column=1, pady=12)

        # 右下角「修改商品」按鈕
        tk.Button(self, text="修改商品", font=("Microsoft YaHei", 18), width=12,
                  command=self.modify_product).place(relx=0.90, rely=0.90, anchor="center")

        self.load_products()
        self.load_suppliers()

    def load_products(self):
        cur = self.conn.cursor()
        cur.execute("SELECT product_name FROM product")
        products = [row[0] for row in cur.fetchall()]
        self.product_combo['values'] = products

    def load_suppliers(self):
        cur = self.conn.cursor()
        cur.execute("SELECT sup_num, sup_com FROM supplier")
        self.supplier_map = {name: num for num, name in cur.fetchall()}
        self.supplier_combo['values'] = list(self.supplier_map.keys())

    def load_product_detail(self, event=None):
        name = self.product_combo.get().strip()
        cur = self.conn.cursor()
        cur.execute("""
            SELECT product_name, price, cost, safe_stock, supplier
            FROM product WHERE product_name=%s
        """, (name,))
        data = cur.fetchone()
        if data:
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, data[0])
            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, str(data[1]))
            self.cost_entry.delete(0, tk.END)
            self.cost_entry.insert(0, str(data[2]))
            self.safestock_entry.delete(0, tk.END)
            self.safestock_entry.insert(0, str(data[3]))
            # 供應商反查名稱
            cur.execute("SELECT sup_com FROM supplier WHERE sup_num=%s", (data[4],))
            sup_name = cur.fetchone()
            if sup_name:
                self.supplier_combo.set(sup_name[0])
            else:
                self.supplier_combo.set('')

    def modify_product(self):
        old_name = self.product_combo.get().strip()
        new_name = self.name_entry.get().strip()
        price = self.price_entry.get().strip()
        cost = self.cost_entry.get().strip()
        safestock = self.safestock_entry.get().strip()
        sup_name = self.supplier_combo.get().strip()
        sup_num = self.supplier_map.get(sup_name, None)

        if not (old_name and new_name and price.isdigit() and cost.isdigit() and safestock.isdigit() and sup_num):
            messagebox.showerror("錯誤", "請填寫完整資料（數字欄請填數字）")
            return

        cur = self.conn.cursor()
        cur.execute("""
            UPDATE product
            SET product_name=%s, price=%s, cost=%s, safe_stock=%s, supplier=%s
            WHERE product_name=%s
        """, (new_name, int(price), int(cost), int(safestock), sup_num, old_name))
        self.conn.commit()
        messagebox.showinfo("完成", f"商品「{old_name}」已修改。")
        self.load_products()  # 重新載入商品清單

    def refresh(self):
        self.load_products()
        self.load_suppliers()
        self.product_combo.set('')
        self.name_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.cost_entry.delete(0, tk.END)
        self.safestock_entry.delete(0, tk.END)
        self.supplier_combo.set('')

class ProductDeleteFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn

        tk.Button(self, text="返回上一頁", font=("Microsoft YaHei", 16),
                  command=lambda: switch_frame("product_menu")).place(x=20, y=20)

        tk.Label(self, text="商品刪除", font=("Microsoft YaHei", 36, "bold")).pack(pady=40)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=20)

        # 1. 商品下拉
        tk.Label(form_frame, text="商品名稱：", font=("Microsoft YaHei", 18)).grid(row=0, column=0, pady=12, sticky="e")
        self.product_combo = ttk.Combobox(form_frame, state="readonly", font=("Microsoft YaHei", 14), width=18)
        self.product_combo.grid(row=0, column=1, pady=12)
        self.product_combo.bind("<<ComboboxSelected>>", self.load_product_detail)

        # 2. 各欄資訊（僅顯示，不可編輯）
        self.price_var = tk.StringVar(value="商品單價")
        tk.Label(form_frame, text="單價：", font=("Microsoft YaHei", 18)).grid(row=1, column=0, pady=12, sticky="e")
        tk.Label(form_frame, textvariable=self.price_var, font=("Microsoft YaHei", 14), bg="#888", fg="#fff", width=18).grid(row=1, column=1, pady=12)

        self.cost_var = tk.StringVar(value="商品成本")
        tk.Label(form_frame, text="成本：", font=("Microsoft YaHei", 18)).grid(row=2, column=0, pady=12, sticky="e")
        tk.Label(form_frame, textvariable=self.cost_var, font=("Microsoft YaHei", 14), bg="#888", fg="#fff", width=18).grid(row=2, column=1, pady=12)

        self.safestock_var = tk.StringVar(value="安全庫存")
        tk.Label(form_frame, text="安全庫存：", font=("Microsoft YaHei", 18)).grid(row=3, column=0, pady=12, sticky="e")
        tk.Label(form_frame, textvariable=self.safestock_var, font=("Microsoft YaHei", 14), bg="#888", fg="#fff", width=18).grid(row=3, column=1, pady=12)

        self.supplier_var = tk.StringVar(value="供應商")
        tk.Label(form_frame, text="供應商：", font=("Microsoft YaHei", 18)).grid(row=4, column=0, pady=12, sticky="e")
        tk.Label(form_frame, textvariable=self.supplier_var, font=("Microsoft YaHei", 14), bg="#888", fg="#fff", width=18).grid(row=4, column=1, pady=12)

        # 右下角刪除按鈕
        tk.Button(self, text="刪除商品", font=("Microsoft YaHei", 18), width=12,
                  command=self.delete_product).place(relx=0.90, rely=0.90, anchor="center")

        self.load_products()

    def load_products(self):
        cur = self.conn.cursor()
        cur.execute("SELECT product_name FROM product")
        products = [row[0] for row in cur.fetchall()]
        self.product_combo['values'] = products

    def load_product_detail(self, event=None):
        name = self.product_combo.get().strip()
        cur = self.conn.cursor()
        cur.execute("""
            SELECT price, cost, safe_stock, supplier
            FROM product WHERE product_name=%s
        """, (name,))
        data = cur.fetchone()
        if data:
            self.price_var.set(str(data[0]))
            self.cost_var.set(str(data[1]))
            self.safestock_var.set(str(data[2]))
            # 反查供應商名稱
            cur.execute("SELECT sup_com FROM supplier WHERE sup_num=%s", (data[3],))
            sup_name = cur.fetchone()
            self.supplier_var.set(sup_name[0] if sup_name else "")
        else:
            self.price_var.set("顯示商品單價")
            self.cost_var.set("顯示商品成本")
            self.safestock_var.set("顯示安全庫存")
            self.supplier_var.set("顯示供應商")

    def delete_product(self):
        name = self.product_combo.get().strip()
        if not name:
            messagebox.showerror("錯誤", "請先選擇商品")
            return
        if not messagebox.askyesno("確認", f"確定要刪除「{name}」這個商品嗎？"):
            return
        cur = self.conn.cursor()
        cur.execute("DELETE FROM product WHERE product_name=%s", (name,))
        self.conn.commit()
        messagebox.showinfo("完成", f"商品「{name}」已刪除。")
        self.load_products()
        self.price_var.set("顯示商品單價")
        self.cost_var.set("顯示商品成本")
        self.safestock_var.set("顯示安全庫存")
        self.supplier_var.set("顯示供應商")
        self.product_combo.set('')

    def refresh(self):
        self.load_products()
        self.product_combo.set('')
        self.price_var.set("商品單價")
        self.cost_var.set("商品成本")
        self.safestock_var.set("安全庫存")
        self.supplier_var.set("供應商")

class InventoryMenuFrame(tk.Frame):
    def __init__(self, master, switch_frame):
        super().__init__(master)
        tk.Label(self, text="").pack(pady=60)
        tk.Label(self, text="進銷存管理系統", font=('Microsoft YaHei',36)).pack(pady=90)
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 12), command=lambda: switch_frame("admin_menu")).place(x=5, y=5)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="供應商維護系統", font=('Microsoft YaHei', 24), command=lambda: switch_frame("supplier_menu")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="進貨系統", font=('Microsoft YaHei', 24), command=lambda: switch_frame("purchase_menu")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="銷貨系統", font=('Microsoft YaHei', 24), command=lambda: switch_frame("sales_menu")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="存貨系統", font=('Microsoft YaHei', 24), command=lambda: switch_frame("stock_menu")).pack(side="left", padx=10)

class SupplierMenuFrame(tk.Frame):
    def __init__(self, master, switch_frame):
        super().__init__(master)
        tk.Label(self, text="").pack(pady=60)
        tk.Label(self, text="供應商維護系統", font=('Microsoft YaHei',36)).pack(pady=90)
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 12), command=lambda: switch_frame("inventory_menu")).place(x=5, y=5)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="供應商新增", font=('Microsoft YaHei', 24), command=lambda: switch_frame("supplier_add")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="供應商查詢", font=('Microsoft YaHei', 24), command=lambda: switch_frame("supplier_query")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="供應商修改", font=('Microsoft YaHei', 24), command=lambda: switch_frame("supplier_mod")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="供應商刪除", font=('Microsoft YaHei', 24), command=lambda: switch_frame("supplier_delete")).pack(side="left", padx=10)

class SupplierAddFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn
        self.switch_frame = switch_frame

        # 回上一頁按鈕
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16),
                  command=lambda: switch_frame("supplier_menu")).place(x=20, y=20)

        # 標題
        tk.Label(self, text="供應商新增", font=('Microsoft YaHei',36)).pack(pady=40)

        # 置中 Frame
        center = tk.Frame(self)
        center.pack(pady=10)

        # 欄位設計
        tk.Label(center, text="供應商公司：", font=('Microsoft YaHei', 18)).grid(row=0, column=0, pady=15, sticky="e")
        self.entry_com = tk.Entry(center, font=('Microsoft YaHei', 16), width=18)
        self.entry_com.grid(row=0, column=1, padx=10)

        tk.Label(center, text="供應商地址：", font=('Microsoft YaHei', 18)).grid(row=1, column=0, pady=15, sticky="e")
        self.entry_address = tk.Entry(center, font=('Microsoft YaHei', 16), width=18)
        self.entry_address.grid(row=1, column=1, padx=10)

        tk.Label(center, text="供應商電話：", font=('Microsoft YaHei', 18)).grid(row=2, column=0, pady=15, sticky="e")
        self.entry_phone = tk.Entry(center, font=('Microsoft YaHei', 16), width=18)
        self.entry_phone.grid(row=2, column=1, padx=10)

        tk.Label(center, text="聯絡人名稱：", font=('Microsoft YaHei', 18)).grid(row=3, column=0, pady=15, sticky="e")
        self.entry_name = tk.Entry(center, font=('Microsoft YaHei', 16), width=18)
        self.entry_name.grid(row=3, column=1, padx=10)

        # 新增按鈕
        tk.Button(self, text="新增供應商", font=('Microsoft YaHei', 18), width=14,
                  command=self.add_supplier).place(relx=0.83, rely=0.83)

    def add_supplier(self):
        com = self.entry_com.get().strip()
        address = self.entry_address.get().strip()
        phone = self.entry_phone.get().strip()
        name = self.entry_name.get().strip()
        if not com or not name:
            messagebox.showwarning("資料不足", "請填寫完整公司與聯絡人名稱")
            return
        cur = self.conn.cursor()
        sql = "INSERT INTO supplier (sup_com, sup_address, sup_phone, sup_name) VALUES (%s, %s, %s, %s)"
        cur.execute(sql, (com, address, phone, name))
        self.conn.commit()
        messagebox.showinfo("新增成功", f"已成功新增供應商：{com}")
        # 清空欄位
        self.entry_com.delete(0, tk.END)
        self.entry_address.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)

class SupplierQueryFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn
        self.switch_frame = switch_frame

        tk.Label(self, text="供應商查詢", font=('Microsoft YaHei',36)).pack(pady=90)
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 12),
                  command=lambda: switch_frame("supplier_menu")).place(x=5, y=5)

        # 置中 Frame
        center = tk.Frame(self)
        center.pack(pady=10)

        tk.Label(center, text="供應商名稱：", font=('Microsoft YaHei', 18)).grid(row=0, column=0, pady=15, sticky="e")
        self.sup_combo = ttk.Combobox(center, font=('Microsoft YaHei', 16), state="readonly", width=18)
        self.sup_combo.grid(row=0, column=1, padx=10)
        self.load_suppliers()

        tk.Button(self, text="查詢供應商", font=('Microsoft YaHei', 18), width=12,
                  command=self.query_supplier).place(relx=0.83, rely=0.83)

    def load_suppliers(self):
        cur = self.conn.cursor()
        cur.execute("SELECT sup_com FROM supplier")
        sups = [row[0] for row in cur.fetchall()]
        self.sup_combo["values"] = sups

    def query_supplier(self):
        sup_name = self.sup_combo.get()
        if not sup_name:
            messagebox.showwarning("提示", "請選擇供應商！")
            return
        cur = self.conn.cursor()
        cur.execute("SELECT sup_com, sup_address, sup_phone, sup_name FROM supplier WHERE sup_com=%s", (sup_name,))
        result = cur.fetchone()
        if result:
            info = f"公司名稱：{result[0]}\n公司地址：{result[1]}\n公司電話：{result[2]}\n聯絡人名稱：{result[3]}"
            show_info_popup("供應商資訊", info)
        else:
            messagebox.showerror("查無資料", "找不到該供應商資料。")

    def refresh(self):
        self.load_suppliers()
        self.sup_combo.set('')

class SupplierModFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn
        self.switch_frame = switch_frame

        tk.Label(self, text="供應商修改", font=('Microsoft YaHei',36)).pack(pady=40)

        center = tk.Frame(self)
        center.pack(pady=10)

        # 供應商下拉選單
        tk.Label(center, text="供應商公司：", font=('Microsoft YaHei', 18)).grid(row=0, column=0, pady=10, sticky="e")
        self.sup_combo = ttk.Combobox(center, font=('Microsoft YaHei', 16), state="readonly", width=18)
        self.sup_combo.grid(row=0, column=1, padx=10)
        self.sup_combo.bind("<<ComboboxSelected>>", self.load_supplier_info)
        self.load_suppliers()

        # 修改欄位
        tk.Label(center, text="供應商公司：", font=('Microsoft YaHei', 16)).grid(row=1, column=0, pady=10, sticky="e")
        self.entry_com = tk.Entry(center, font=('Microsoft YaHei', 16), width=18)
        self.entry_com.grid(row=1, column=1, padx=10)

        tk.Label(center, text="供應商地址：", font=('Microsoft YaHei', 16)).grid(row=2, column=0, pady=10, sticky="e")
        self.entry_addr = tk.Entry(center, font=('Microsoft YaHei', 16), width=18)
        self.entry_addr.grid(row=2, column=1, padx=10)

        tk.Label(center, text="供應商電話：", font=('Microsoft YaHei', 16)).grid(row=3, column=0, pady=10, sticky="e")
        self.entry_phone = tk.Entry(center, font=('Microsoft YaHei', 16), width=18)
        self.entry_phone.grid(row=3, column=1, padx=10)

        tk.Label(center, text="聯絡人名稱：", font=('Microsoft YaHei', 16)).grid(row=4, column=0, pady=10, sticky="e")
        self.entry_name = tk.Entry(center, font=('Microsoft YaHei', 16), width=18)
        self.entry_name.grid(row=4, column=1, padx=10)

        # 返回與確認按鈕
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 12),
                  command=lambda: switch_frame("supplier_menu")).place(x=5, y=5)
        tk.Button(self, text="修改供應商", font=('Microsoft YaHei', 18), width=12,
                  command=self.modify_supplier).place(relx=0.83, rely=0.87)

    def load_suppliers(self):
        cur = self.conn.cursor()
        cur.execute("SELECT sup_com FROM supplier")
        sups = [row[0] for row in cur.fetchall()]
        self.sup_combo["values"] = sups

    def load_supplier_info(self, event=None):
        sup_com = self.sup_combo.get()
        cur = self.conn.cursor()
        cur.execute("SELECT sup_com, sup_address, sup_phone, sup_name FROM supplier WHERE sup_com=%s", (sup_com,))
        result = cur.fetchone()
        if result:
            self.entry_com.delete(0, tk.END)
            self.entry_addr.delete(0, tk.END)
            self.entry_phone.delete(0, tk.END)
            self.entry_name.delete(0, tk.END)
            self.entry_com.insert(0, result[0])
            self.entry_addr.insert(0, result[1])
            self.entry_phone.insert(0, result[2])
            self.entry_name.insert(0, result[3])
        else:
            self.entry_com.delete(0, tk.END)
            self.entry_addr.delete(0, tk.END)
            self.entry_phone.delete(0, tk.END)
            self.entry_name.delete(0, tk.END)

    def modify_supplier(self):
        old_com = self.sup_combo.get()
        new_com = self.entry_com.get()
        addr = self.entry_addr.get()
        phone = self.entry_phone.get()
        name = self.entry_name.get()
        if not old_com:
            messagebox.showwarning("提示", "請選擇要修改的供應商！")
            return
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE supplier
            SET sup_com=%s, sup_address=%s, sup_phone=%s, sup_name=%s
            WHERE sup_com=%s
        """, (new_com, addr, phone, name, old_com))
        self.conn.commit()
        messagebox.showinfo("成功", "供應商資料已修改！")
        self.load_suppliers()
        self.sup_combo.set(new_com)

    def refresh(self):
        self.load_suppliers()
        self.sup_combo.set('')
        self.entry_com.delete(0, tk.END)
        self.entry_addr.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)

class SupplierDeleteFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn
        self.switch_frame = switch_frame

        tk.Label(self, text="供應商刪除", font=('Microsoft YaHei',36)).pack(pady=40)

        center = tk.Frame(self)
        center.pack(pady=10)

        # 供應商下拉選單
        tk.Label(center, text="供應商公司：", font=('Microsoft YaHei', 18)).grid(row=0, column=0, pady=10, sticky="e")
        self.sup_combo = ttk.Combobox(center, font=('Microsoft YaHei', 16), state="readonly", width=18)
        self.sup_combo.grid(row=0, column=1, padx=10)
        self.sup_combo.bind("<<ComboboxSelected>>", self.show_supplier_info)
        self.load_suppliers()

        # 顯示用標籤
        tk.Label(center, text="供應商地址：", font=('Microsoft YaHei', 16)).grid(row=1, column=0, pady=10, sticky="e")
        self.lbl_addr = tk.Label(center, text="", font=('Microsoft YaHei', 16), width=18, bg="#bdbdbd")
        self.lbl_addr.grid(row=1, column=1, padx=10)

        tk.Label(center, text="供應商電話：", font=('Microsoft YaHei', 16)).grid(row=2, column=0, pady=10, sticky="e")
        self.lbl_phone = tk.Label(center, text="", font=('Microsoft YaHei', 16), width=18, bg="#bdbdbd")
        self.lbl_phone.grid(row=2, column=1, padx=10)

        tk.Label(center, text="聯絡人名稱：", font=('Microsoft YaHei', 16)).grid(row=3, column=0, pady=10, sticky="e")
        self.lbl_name = tk.Label(center, text="", font=('Microsoft YaHei', 16), width=18, bg="#bdbdbd")
        self.lbl_name.grid(row=3, column=1, padx=10)

        # 返回與刪除按鈕
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 12),
                  command=lambda: switch_frame("supplier_menu")).place(x=5, y=5)
        tk.Button(self, text="刪除供應商", font=('Microsoft YaHei', 18), width=12,
                  command=self.delete_supplier).place(relx=0.83, rely=0.87)

    def load_suppliers(self):
        cur = self.conn.cursor()
        cur.execute("SELECT sup_com FROM supplier")
        sups = [row[0] for row in cur.fetchall()]
        self.sup_combo["values"] = sups

    def show_supplier_info(self, event=None):
        sup_com = self.sup_combo.get()
        cur = self.conn.cursor()
        cur.execute("SELECT sup_address, sup_phone, sup_name FROM supplier WHERE sup_com=%s", (sup_com,))
        result = cur.fetchone()
        if result:
            self.lbl_addr.config(text=result[0])
            self.lbl_phone.config(text=result[1])
            self.lbl_name.config(text=result[2])
        else:
            self.lbl_addr.config(text="")
            self.lbl_phone.config(text="")
            self.lbl_name.config(text="")

    def delete_supplier(self):
        sup_com = self.sup_combo.get()
        if not sup_com:
            messagebox.showwarning("提示", "請選擇要刪除的供應商！")
            return
        if messagebox.askyesno("確認", f"確定要刪除供應商 '{sup_com}' 嗎？"):
            cur = self.conn.cursor()
            cur.execute("DELETE FROM supplier WHERE sup_com=%s", (sup_com,))
            self.conn.commit()
            messagebox.showinfo("成功", "供應商已刪除！")
            self.load_suppliers()
            self.sup_combo.set('')
            self.lbl_addr.config(text="")
            self.lbl_phone.config(text="")
            self.lbl_name.config(text="")

    def refresh(self):
        self.load_suppliers()
        self.sup_combo.set('')
        self.lbl_addr.config(text="")
        self.lbl_phone.config(text="")
        self.lbl_name.config(text="")

class PurchaseMenuFrame(tk.Frame):
    def __init__(self, master, switch_frame):
        super().__init__(master)
        tk.Label(self, text="").pack(pady=60)
        tk.Label(self, text="進貨系統", font=('Microsoft YaHei',36)).pack(pady=90)
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 12), command=lambda: switch_frame("inventory_menu")).place(x=5, y=5)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="進貨新增", font=('Microsoft YaHei', 24), command=lambda: switch_frame("purchase_add")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="進貨查詢", font=('Microsoft YaHei', 24), command=lambda: switch_frame("purchase_query")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="進貨修改", font=('Microsoft YaHei', 24), command=lambda: switch_frame("purchase_mod")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="進貨刪除", font=('Microsoft YaHei', 24), command=lambda: switch_frame("purchase_delete")).pack(side="left", padx=10)

class PurchaseAddFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn

        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16),
                  command=lambda: switch_frame("purchase_menu")).place(x=20, y=20)
        tk.Label(self, text="進貨新增", font=('Microsoft YaHei',36)).pack(pady=30)
        
        main_frame = tk.Frame(self)
        main_frame.pack(pady=10)

        # 日期
        tk.Label(main_frame, text="訂貨日期：", font=('Microsoft YaHei', 22)).grid(row=0, column=0, sticky="e", padx=5, pady=15)
        self.date_entry = DateEntry(main_frame, font=('Microsoft YaHei', 18), date_pattern="yyyy-mm-dd", width=15)
        self.date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=15, columnspan=2)

        # 標題
        tk.Label(main_frame, text="商品", font=('Microsoft YaHei', 22)).grid(row=1, column=0)
        tk.Label(main_frame, text="數量", font=('Microsoft YaHei', 22)).grid(row=1, column=1)
        tk.Label(main_frame, text="成本單價", font=('Microsoft YaHei', 22)).grid(row=1, column=2)
        tk.Label(main_frame, text="小結", font=('Microsoft YaHei', 22)).grid(row=1, column=3)

        # 商品選擇區
        self.product_combo = ttk.Combobox(main_frame, state="readonly", font=('Microsoft YaHei', 16), width=14)
        self.product_combo.grid(row=2, column=0, padx=3, pady=10)
        self.product_combo.bind("<<ComboboxSelected>>", self.show_cost)

        self.qty_entry = tk.Entry(main_frame, font=('Microsoft YaHei', 16), width=8)
        self.qty_entry.grid(row=2, column=1, padx=3, pady=10)
        self.qty_entry.bind("<KeyRelease>", self.update_subtotal)

        self.cost_var = tk.StringVar()
        tk.Label(main_frame, textvariable=self.cost_var, font=('Microsoft YaHei', 16), width=12, bg="#888", fg="#fff").grid(row=2, column=2, padx=3, pady=10)

        self.subtotal_var = tk.StringVar()
        tk.Label(main_frame, textvariable=self.subtotal_var, font=('Microsoft YaHei', 16), width=12, bg="#888", fg="#fff").grid(row=2, column=3, padx=3, pady=10)

        tk.Button(main_frame, text="+", font=('Microsoft YaHei', 18), width=3, command=self.add_item).grid(row=2, column=4, padx=3, pady=10)

        # 已選商品區
        self.items_frame = tk.Frame(main_frame)
        self.items_frame.grid(row=3, column=0, columnspan=5, pady=20)
        self.selected_items = []  # list of dict: {product, qty, cost, subtotal, product_num}

        # 右下角總金額、按鈕
        self.total_var = tk.IntVar(value=0)
        tk.Label(self, text="總金額：", font=('Microsoft YaHei', 20)).place(relx=0.75, rely=0.75)
        tk.Label(self, textvariable=self.total_var, font=('Microsoft YaHei', 20)).place(relx=0.85, rely=0.75)
        tk.Button(self, text="新增進貨單", font=('Microsoft YaHei', 18), width=12, command=self.submit_purchase).place(relx=0.88, rely=0.85)

        self.load_products()

    def load_products(self):
        cur = self.conn.cursor()
        cur.execute("SELECT product_name, product_num FROM product")
        self.products = {row[0]: row[1] for row in cur.fetchall()}
        self.product_combo['values'] = list(self.products.keys())

    def show_cost(self, event=None):
        prod = self.product_combo.get()
        cur = self.conn.cursor()
        cur.execute("SELECT cost FROM product WHERE product_name=%s", (prod,))
        row = cur.fetchone()
        cost_val = row[0] if row else 0
        self.cost_var.set(str(cost_val))
        self.update_subtotal()

    def update_subtotal(self, event=None):
        try:
            qty = int(self.qty_entry.get())
            cost = int(self.cost_var.get())
            subtotal = qty * cost
            self.subtotal_var.set(str(subtotal))
        except:
            self.subtotal_var.set("0")

    def add_item(self):
        prod = self.product_combo.get()
        qty = self.qty_entry.get()
        cost = self.cost_var.get()
        subtotal = self.subtotal_var.get()
        if not (prod and qty.isdigit() and int(qty) > 0):
            messagebox.showwarning("輸入錯誤", "請選商品並輸入數量")
            return
        for item in self.selected_items:
            if item["product"] == prod:
                messagebox.showwarning("重複商品", "該商品已選")
                return
        item = {
            "product": prod,
            "qty": int(qty),
            "cost": int(cost),
            "subtotal": int(subtotal),
            "product_num": self.products[prod]
        }
        self.selected_items.append(item)
        self.refresh_items()

    def refresh_items(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        for i, item in enumerate(self.selected_items):
            tk.Label(self.items_frame, text=item["product"], font=('Microsoft YaHei', 14), width=15).grid(row=i, column=0)
            tk.Label(self.items_frame, text=item["qty"], font=('Microsoft YaHei', 14), width=8).grid(row=i, column=1)
            tk.Label(self.items_frame, text=item["cost"], font=('Microsoft YaHei', 14), width=12).grid(row=i, column=2)
            tk.Label(self.items_frame, text=item["subtotal"], font=('Microsoft YaHei', 14), width=12).grid(row=i, column=3)
            tk.Button(self.items_frame, text="❌", font=('Microsoft YaHei', 14),
                      command=lambda idx=i: self.del_item(idx)).grid(row=i, column=4)
        self.total_var.set(sum(item['subtotal'] for item in self.selected_items))

    def del_item(self, idx):
        self.selected_items.pop(idx)
        self.refresh_items()

    def submit_purchase(self):
        if not self.selected_items:
            messagebox.showerror("錯誤", "請先新增進貨商品！")
            return
        date_str = self.date_entry.get()
        total = self.total_var.get()
        cur = self.conn.cursor()

        # 用 getattr 安全取得 user_num
        agent_id = getattr(self.master, "current_user_num", None)
        if not agent_id:
            messagebox.showerror("錯誤", "請重新登入！")
            return

        # 寫入 purchase 主表
        cur.execute(
            "INSERT INTO purchase (purchase_date, purchase_amount, agent) VALUES (%s, %s, %s)",
            (date_str, total, agent_id)
        )
        purchase_num = cur.lastrowid

        # 寫入 purchase_receipt 明細
        prod_nums = []
        for item in self.selected_items:
            prod_nums.append(item["product_num"])
            cur.execute(
                "INSERT INTO purchase_receipt (purchase_number, product_num, quantity, cost, sum) VALUES (%s, %s, %s, %s, %s)",
                (purchase_num, item["product_num"], item["qty"], item["cost"], item["subtotal"])
            )
        self.conn.commit()
        for pn in prod_nums:
            warn_below_safe_stock(self.conn, pn)
        messagebox.showinfo("完成", f"已新增進貨單（編號 {purchase_num}）")
        # 重置
        self.selected_items = []
        self.refresh_items()
        self.qty_entry.delete(0, tk.END)
        self.cost_var.set("")
        self.subtotal_var.set("")
        self.product_combo.set("")
        self.total_var.set(0)

class PurchaseQueryFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn

        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16),
                  command=lambda: switch_frame("purchase_menu")).place(x=20, y=20)
        tk.Label(self, text="進貨查詢", font=('Microsoft YaHei',36)).pack(pady=30)

        main_frame = tk.Frame(self)
        main_frame.pack(pady=30)

        # 訂貨日期下拉
        tk.Label(main_frame, text="訂單日期：", font=('Microsoft YaHei', 22)).grid(row=0, column=0, pady=15, sticky="e")
        self.date_combo = ttk.Combobox(main_frame, font=('Microsoft YaHei', 16), width=20, state="readonly")
        self.date_combo.grid(row=0, column=1, padx=10, pady=15)

        # 商品下拉
        tk.Label(main_frame, text="商品：", font=('Microsoft YaHei', 22)).grid(row=1, column=0, pady=15, sticky="e")
        self.product_combo = ttk.Combobox(main_frame, font=('Microsoft YaHei', 16), width=20, state="readonly")
        self.product_combo.grid(row=1, column=1, padx=10, pady=15)

        # 查詢按鈕
        tk.Button(self, text="查詢進貨單", font=('Microsoft YaHei', 18),
                  command=self.query_purchase).place(relx=0.88, rely=0.85)

        self.load_dates()
        self.load_products()

    def load_dates(self):
        cur = self.conn.cursor()
        cur.execute("SELECT DISTINCT purchase_date FROM purchase ORDER BY purchase_date DESC")
        dates = [row[0].strftime("%Y-%m-%d") for row in cur.fetchall()]
        self.date_combo["values"] = [""] + dates

    def load_products(self):
        cur = self.conn.cursor()
        cur.execute("SELECT DISTINCT product_name FROM product ORDER BY product_name")
        products = [row[0] for row in cur.fetchall()]
        self.product_combo["values"] = [""] + products

    def query_purchase(self):
        date = self.date_combo.get()
        product = self.product_combo.get()
        cur = self.conn.cursor()

        # 組 SQL 條件
        sql = '''
            SELECT p.purchase_num, p.purchase_date, pr.product_num, pr.quantity, pr.cost, pr.sum, pd.product_name
            FROM purchase p
            JOIN purchase_receipt pr ON p.purchase_num = pr.purchase_number
            JOIN product pd ON pr.product_num = pd.product_num
            WHERE 1=1
        '''
        params = []
        if date:
            sql += " AND p.purchase_date = %s"
            params.append(date)
        if product:
            sql += " AND pd.product_name = %s"
            params.append(product)
        sql += " ORDER BY p.purchase_num"

        cur.execute(sql, params)
        results = cur.fetchall()

        # 顯示結果
        if not results:
            messagebox.showinfo("查詢結果", "查無相關進貨單")
            return

        info = "{:<8}{:<12}{:<12}{:<8}{:<8}{:<8}\n".format("編號", "日期", "商品", "數量", "單價", "小結")
        info += "-" * 60 + "\n"
        for row in results:
            purchase_number, purchase_date, _, quantity, cost, sum_val, product_name = row
            info += "{:<8}{:<12}{:<12}{:<8}{:<8}{:<8}\n".format(
                purchase_number, str(purchase_date), product_name, quantity, cost, sum_val
            )
        # 使用你現有的 show_info_popup 或 messagebox 顯示
        self.show_info_popup("查詢結果", info)

    def show_info_popup(self, title, info):
        popup = tk.Toplevel(self)
        popup.title(title)
        popup.geometry("600x400")
        text = tk.Text(popup, font=('Microsoft YaHei', 14))
        text.pack(expand=True, fill=tk.BOTH)
        text.insert(tk.END, info)
        text.config(state=tk.DISABLED)
    def refresh(self):
        self.load_dates()
        self.load_products()
        self.date_combo.set('')
        self.product_combo.set('')

class PurchaseModFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn
        self.selected_items = []
    
        # 標題區
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16),
                  command=lambda: switch_frame("purchase_menu")).grid(row=0, column=0, sticky="w", padx=10, pady=10, columnspan=2)
        tk.Label(self, text="進貨修改", font=('Microsoft YaHei',36)).grid(row=0, column=1, sticky="n", pady=30, columnspan=4)

        # 主框分兩側
        main_frame = tk.Frame(self)
        main_frame.grid(row=1, column=0, columnspan=5, sticky="nsew", padx=40)

        # 左側條件區
        left_frame = tk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        tk.Label(left_frame, text="訂單日期：", font=('Microsoft YaHei', 20)).grid(row=0, column=0, sticky="e", pady=10)
        self.date_combo = ttk.Combobox(left_frame, state="readonly", font=('Microsoft YaHei', 16), width=16)
        self.date_combo.grid(row=0, column=1, sticky="w", pady=10)
        self.date_combo.bind("<<ComboboxSelected>>", self.load_purchase_nums)

        tk.Label(left_frame, text="訂單編號：", font=('Microsoft YaHei', 20)).grid(row=1, column=0, sticky="e", pady=10)
        self.num_combo = ttk.Combobox(left_frame, state="readonly", font=('Microsoft YaHei', 16), width=16)
        self.num_combo.grid(row=1, column=1, sticky="w", pady=10)
        self.num_combo.bind("<<ComboboxSelected>>", self.load_purchase_details)

        # 右側商品區
        right_frame = tk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nw", padx=40, pady=10)

        tk.Label(right_frame, text="商品", font=('Microsoft YaHei', 22)).grid(row=0, column=0)
        tk.Label(right_frame, text="數量", font=('Microsoft YaHei', 22)).grid(row=0, column=1)
        tk.Label(right_frame, text="成本", font=('Microsoft YaHei', 22)).grid(row=0, column=2)
        tk.Label(right_frame, text="小結", font=('Microsoft YaHei', 22)).grid(row=0, column=3)
        tk.Label(right_frame, text="", font=('Microsoft YaHei', 22)).grid(row=0, column=4)

        self.product_combo = ttk.Combobox(right_frame, state="readonly", font=('Microsoft YaHei', 16), width=14)
        self.product_combo.grid(row=1, column=0, padx=2, pady=8)
        self.product_combo.bind("<<ComboboxSelected>>", self.show_cost)
        self.qty_entry = tk.Entry(right_frame, font=('Microsoft YaHei', 16), width=8)
        self.qty_entry.grid(row=1, column=1, padx=2, pady=8)
        self.qty_entry.bind("<KeyRelease>", self.update_subtotal)
        self.cost_var = tk.StringVar()
        tk.Label(right_frame, textvariable=self.cost_var, font=('Microsoft YaHei', 16), width=10, bg="#888", fg="#fff").grid(row=1, column=2, padx=2, pady=8)
        self.subtotal_var = tk.StringVar()
        tk.Label(right_frame, textvariable=self.subtotal_var, font=('Microsoft YaHei', 16), width=10, bg="#888", fg="#fff").grid(row=1, column=3, padx=2, pady=8)
        tk.Button(right_frame, text="+", font=('Microsoft YaHei', 18), width=3, command=self.add_item).grid(row=1, column=4, padx=2, pady=8)

        # 已選商品區
        self.items_frame = tk.Frame(right_frame)
        self.items_frame.grid(row=2, column=0, columnspan=5, sticky="w")

        # 右下角
        self.total_var = tk.IntVar(value=0)
        tk.Label(self, text="總金額：", font=('Microsoft YaHei', 20)).place(relx=0.75, rely=0.80)
        tk.Label(self, textvariable=self.total_var, font=('Microsoft YaHei', 20)).place(relx=0.85, rely=0.80)
        tk.Button(self, text="修改進貨單", font=('Microsoft YaHei', 18), width=12, command=self.update_purchase).place(relx=0.88, rely=0.88)

        self.load_dates()
        self.load_products()

    def load_dates(self):
        cur = self.conn.cursor()
        cur.execute("SELECT DISTINCT purchase_date FROM purchase ORDER BY purchase_date")
        dates = [row[0].strftime('%Y-%m-%d') for row in cur.fetchall()]
        self.date_combo['values'] = dates

    def load_purchase_nums(self, event=None):
        date = self.date_combo.get()
        cur = self.conn.cursor()
        cur.execute("SELECT purchase_num FROM purchase WHERE purchase_date=%s ORDER BY purchase_num", (date,))
        nums = [str(row[0]) for row in cur.fetchall()]
        self.num_combo['values'] = nums
        self.num_combo.set('')
        self.selected_items = []
        self.refresh_items()

    def load_products(self):
        cur = self.conn.cursor()
        cur.execute("SELECT product_name, product_num, cost FROM product")
        self.products = {row[0]: (row[1], row[2]) for row in cur.fetchall()}
        self.product_combo['values'] = list(self.products.keys())
        self.product_combo.bind("<<ComboboxSelected>>", self.show_cost)

    def show_cost(self, event=None):
        prod = self.product_combo.get()
        cost = self.products[prod][1] if prod in self.products else 0
        self.cost_var.set(str(cost))
        self.update_subtotal()

    def update_subtotal(self, event=None):
        try:
            qty = int(self.qty_entry.get())
            cost = int(self.cost_var.get())
            subtotal = qty * cost
            self.subtotal_var.set(str(subtotal))
        except:
            self.subtotal_var.set("0")

    def add_item(self):
        prod = self.product_combo.get()
        qty = self.qty_entry.get()
        cost = self.cost_var.get()
        subtotal = self.subtotal_var.get()
        if not (prod and qty.isdigit() and int(qty) > 0):
            messagebox.showwarning("輸入錯誤", "請選商品並輸入數量")
            return
        for item in self.selected_items:
            if item["product"] == prod:
                messagebox.showwarning("重複商品", "該商品已選")
                return
        item = {
            "product": prod,
            "qty": int(qty),
            "cost": int(cost),
            "subtotal": int(subtotal),
            "product_num": self.products[prod][0]
        }
        self.selected_items.append(item)
        self.refresh_items()

    def refresh_items(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        for i, item in enumerate(self.selected_items):
            tk.Label(self.items_frame, text=item["product"], font=('Microsoft YaHei', 14), width=15).grid(row=i, column=0)
            tk.Label(self.items_frame, text=item["qty"], font=('Microsoft YaHei', 14), width=8).grid(row=i, column=1)
            tk.Label(self.items_frame, text=item["cost"], font=('Microsoft YaHei', 14), width=10).grid(row=i, column=2)
            tk.Label(self.items_frame, text=item["subtotal"], font=('Microsoft YaHei', 14), width=10).grid(row=i, column=3)
            tk.Button(self.items_frame, text="❌", font=('Microsoft YaHei', 14), command=lambda idx=i: self.del_item(idx)).grid(row=i, column=4)
        self.total_var.set(sum(item['subtotal'] for item in self.selected_items))

    def del_item(self, idx):
        self.selected_items.pop(idx)
        self.refresh_items()

    def load_purchase_details(self, event=None):
        purchase_num = self.num_combo.get()
        if not purchase_num:
            self.selected_items = []
            self.refresh_items()
            return
        cur = self.conn.cursor()
        cur.execute("""
            SELECT pr.product_num, p.product_name, pr.quantity, pr.cost, pr.sum
            FROM purchase_receipt pr
            JOIN product p ON pr.product_num = p.product_num
            WHERE pr.purchase_number=%s
        """, (purchase_num,))
        self.selected_items = []
        for row in cur.fetchall():
            item = {
                "product": row[1],
                "qty": row[2],
                "cost": row[3],
                "subtotal": row[4],
                "product_num": row[0]
            }
            self.selected_items.append(item)
        self.refresh_items()

    def update_purchase(self):
        purchase_num = self.num_combo.get()
        date_str = self.date_combo.get()
        total = self.total_var.get()
        if not (purchase_num and self.selected_items):
            messagebox.showerror("錯誤", "請選擇訂單並修改明細！")
            return
        cur = self.conn.cursor()
        # 刪除原明細
        cur.execute("DELETE FROM purchase_receipt WHERE purchase_number=%s", (purchase_num,))
        # 新增明細
        for item in self.selected_items:
            cur.execute(
                "INSERT INTO purchase_receipt (purchase_number, product_num, quantity, cost, sum) VALUES (%s, %s, %s, %s, %s)",
                (purchase_num, item["product_num"], item["qty"], item["cost"], item["subtotal"])
            )
        # 更新主表
        cur.execute(
            "UPDATE purchase SET purchase_date=%s, purchase_amount=%s WHERE purchase_num=%s",
            (date_str, total, purchase_num)
        )
        self.conn.commit()
        messagebox.showinfo("完成", f"已修改進貨單（編號 {purchase_num}）")
        self.selected_items = []
        self.refresh_items()
        self.qty_entry.delete(0, tk.END)
        self.cost_var.set("")
        self.subtotal_var.set("")
        self.product_combo.set("")
        self.total_var.set(0)

    def refresh(self):
        self.load_dates()
        self.load_products()
        self.date_combo.set('')
        self.num_combo.set('')
        self.selected_items = []
        self.refresh_items()

class PurchaseDeleteFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn

        # 標題與返回按鈕
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16),
                  command=lambda: switch_frame("purchase_menu")).grid(row=0, column=0, sticky="w", padx=10, pady=10, columnspan=2)
        tk.Label(self, text="進貨刪除", font=('Microsoft YaHei',36)).grid(row=0, column=1, sticky="n", columnspan=4, pady=30)

        # 主框體（左右兩側）
        main_frame = tk.Frame(self)
        main_frame.grid(row=1, column=0, columnspan=5, sticky="nsew", padx=40)

        # 左側條件選擇
        left_frame = tk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        tk.Label(left_frame, text="訂單日期：", font=('Microsoft YaHei', 20)).grid(row=0, column=0, sticky="e", pady=10)
        self.date_combo = ttk.Combobox(left_frame, state="readonly", font=('Microsoft YaHei', 16), width=16)
        self.date_combo.grid(row=0, column=1, sticky="w", pady=10)
        self.date_combo.bind("<<ComboboxSelected>>", self.load_purchase_nums)

        tk.Label(left_frame, text="訂單編號：", font=('Microsoft YaHei', 20)).grid(row=1, column=0, sticky="e", pady=10)
        self.num_combo = ttk.Combobox(left_frame, state="readonly", font=('Microsoft YaHei', 16), width=16)
        self.num_combo.grid(row=1, column=1, sticky="w", pady=10)
        self.num_combo.bind("<<ComboboxSelected>>", self.load_purchase_details)

        # 右側明細區
        right_frame = tk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nw", padx=40, pady=10)

        # 明細區標題列
        tk.Label(right_frame, text="商品", font=('Microsoft YaHei', 22)).grid(row=0, column=0)
        tk.Label(right_frame, text="數量", font=('Microsoft YaHei', 22)).grid(row=0, column=1)
        tk.Label(right_frame, text="成本", font=('Microsoft YaHei', 22)).grid(row=0, column=2)
        tk.Label(right_frame, text="小結", font=('Microsoft YaHei', 22)).grid(row=0, column=3)
        tk.Label(right_frame, text="", font=('Microsoft YaHei', 22)).grid(row=0, column=4)

        # 商品明細顯示區（僅顯示，不可修改）
        self.items_frame = tk.Frame(right_frame)
        self.items_frame.grid(row=1, column=0, columnspan=5, sticky="w")

        # 右下角
        self.total_var = tk.IntVar(value=0)
        tk.Label(self, text="總金額：", font=('Microsoft YaHei', 20)).place(relx=0.75, rely=0.80)
        tk.Label(self, textvariable=self.total_var, font=('Microsoft YaHei', 20)).place(relx=0.85, rely=0.80)
        tk.Button(self, text="刪除進貨單", font=('Microsoft YaHei', 18), width=12, command=self.delete_purchase).place(relx=0.88, rely=0.88)

        self.selected_items = []
        self.load_dates()

    def load_dates(self):
        cur = self.conn.cursor()
        cur.execute("SELECT DISTINCT purchase_date FROM purchase ORDER BY purchase_date")
        dates = [row[0].strftime('%Y-%m-%d') for row in cur.fetchall()]
        self.date_combo['values'] = dates

    def load_purchase_nums(self, event=None):
        date = self.date_combo.get()
        cur = self.conn.cursor()
        cur.execute("SELECT purchase_num FROM purchase WHERE purchase_date=%s ORDER BY purchase_num", (date,))
        nums = [str(row[0]) for row in cur.fetchall()]
        self.num_combo['values'] = nums
        self.num_combo.set('')
        self.selected_items = []
        self.refresh_items()

    def load_purchase_details(self, event=None):
        purchase_num = self.num_combo.get()
        if not purchase_num:
            self.selected_items = []
            self.refresh_items()
            return
        cur = self.conn.cursor()
        cur.execute("""
            SELECT pr.product_num, p.product_name, pr.quantity, pr.cost, pr.sum
            FROM purchase_receipt pr
            JOIN product p ON pr.product_num = p.product_num
            WHERE pr.purchase_number=%s
        """, (purchase_num,))
        self.selected_items = []
        for row in cur.fetchall():
            item = {
                "product": row[1],
                "qty": row[2],
                "cost": row[3],
                "subtotal": row[4],
                "product_num": row[0]
            }
            self.selected_items.append(item)
        self.refresh_items()

    def refresh_items(self):
        # 僅顯示每個明細，**不可修改**
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        for i, item in enumerate(self.selected_items):
            tk.Label(self.items_frame, text=item["product"], font=('Microsoft YaHei', 14), width=15).grid(row=i, column=0)
            tk.Label(self.items_frame, text=item["qty"], font=('Microsoft YaHei', 14), width=8).grid(row=i, column=1)
            tk.Label(self.items_frame, text=item["cost"], font=('Microsoft YaHei', 14), width=10).grid(row=i, column=2)
            tk.Label(self.items_frame, text=item["subtotal"], font=('Microsoft YaHei', 14), width=10).grid(row=i, column=3)
        self.total_var.set(sum(item['subtotal'] for item in self.selected_items))

    def delete_purchase(self):
        purchase_num = self.num_combo.get()
        if not purchase_num:
            messagebox.showerror("錯誤", "請選擇進貨單！")
            return
        if not messagebox.askyesno("確認刪除", f"確定要刪除進貨單 {purchase_num} 嗎？\n此操作無法復原。"):
            return
        cur = self.conn.cursor()
        # 先刪除明細
        cur.execute("DELETE FROM purchase_receipt WHERE purchase_number=%s", (purchase_num,))
        # 再刪除主表
        cur.execute("DELETE FROM purchase WHERE purchase_num=%s", (purchase_num,))
        self.conn.commit()
        messagebox.showinfo("完成", f"已刪除進貨單（編號 {purchase_num}）")
        self.selected_items = []
        self.refresh_items()
        self.num_combo.set('')
        self.total_var.set(0)

    def refresh(self):
        self.load_dates()
        self.date_combo.set('')
        self.num_combo.set('')
        self.selected_items = []
        self.refresh_items()

class SalesMenuFrame(tk.Frame):
    def __init__(self, master, switch_frame):
        super().__init__(master)
        tk.Label(self, text="").pack(pady=60)
        tk.Label(self, text="銷貨系統", font=('Microsoft YaHei',36)).pack(pady=90)
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 12), command=lambda: switch_frame("inventory_menu")).place(x=5, y=5)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="銷貨查詢", font=('Microsoft YaHei', 24), command=lambda: switch_frame("sales_query")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="查詢銷貨報表", font=('Microsoft YaHei', 24), command=lambda: switch_frame("sales_report")).pack(side="left", padx=10)

class SalesReportFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn
        self.switch_frame = switch_frame

        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16),
                  command=lambda: self.switch_frame("sales_menu")).place(x=20, y=20)
        tk.Label(self, text="查詢銷貨報表", font=('Microsoft YaHei', 36)).pack(pady=30)

        main_frame = tk.Frame(self)
        main_frame.pack(pady=10)

        tk.Label(main_frame, text="選擇報表日期區間", font=('Microsoft YaHei', 20)).grid(row=0, column=0, columnspan=2, pady=20)

        tk.Label(main_frame, text="區間開始：", font=('Microsoft YaHei', 20)).grid(row=1, column=0, sticky='e', pady=15)
        self.start_entry = DateEntry(main_frame, font=('Microsoft YaHei', 16), width=16, date_pattern="yyyy-mm-dd")
        self.start_entry.grid(row=1, column=1, sticky='w', pady=15)

        tk.Label(main_frame, text="區間結束：", font=('Microsoft YaHei', 20)).grid(row=2, column=0, sticky='e', pady=15)
        self.end_entry = DateEntry(main_frame, font=('Microsoft YaHei', 16), width=16, date_pattern="yyyy-mm-dd")
        self.end_entry.grid(row=2, column=1, sticky='w', pady=15)

        tk.Button(self, text="查詢報表", font=('Microsoft YaHei', 20), command=self.export_report).place(relx=0.85, rely=0.85)

    def export_report(self):
        start = self.start_entry.get()
        end = self.end_entry.get()
        if not start or not end:
            messagebox.showerror("錯誤", "請選擇完整日期區間")
            return
        cur = self.conn.cursor()
        sql = """
        SELECT o.order_num AS 訂單編號, o.order_date AS 日期, c.cust_name AS 顧客, 
               p.product_name AS 商品, r.quantity AS 數量, r.price AS 單價, r.sum AS 小計
        FROM `order` o
        JOIN order_receipt r ON o.order_num = r.order_num
        JOIN product p ON r.product_num = p.product_num
        JOIN customer c ON o.customer = c.cust_num
        WHERE o.order_date BETWEEN %s AND %s
        ORDER BY o.order_date, o.order_num
        """
        cur.execute(sql, (start, end))
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        if not rows:
            messagebox.showinfo("查詢結果", "此區間無訂單資料")
            return

        df = pd.DataFrame(rows, columns=columns)
        file_path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel 檔案', '*.xlsx')])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("成功", f"報表已儲存：\n{file_path}")

class SalesQueryFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn
        self.switch_frame = switch_frame

        # 回到上一頁按鈕
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16), command=lambda: switch_frame("sales_menu")).place(x=20, y=20)

        # 標題
        tk.Label(self, text="銷貨查詢", font=('Microsoft YaHei',36)).pack(pady=40)

        # 置中 frame
        center = tk.Frame(self)
        center.pack(pady=30)

        # 顧客名稱
        tk.Label(center, text="顧客名稱：", font=('Microsoft YaHei', 20)).grid(row=0, column=0, sticky="e", pady=20, padx=10)
        self.cust_combo = ttk.Combobox(center, font=('Microsoft YaHei', 16), state="readonly", width=18)
        self.cust_combo.grid(row=0, column=1, padx=10)

        # 訂單日期
        tk.Label(center, text="訂單日期：", font=('Microsoft YaHei', 20)).grid(row=1, column=0, sticky="e", pady=20, padx=10)
        self.date_combo = ttk.Combobox(center, font=('Microsoft YaHei', 16), state="readonly", width=18)
        self.date_combo.grid(row=1, column=1, padx=10)

        # 商品
        tk.Label(center, text="商品：", font=('Microsoft YaHei', 20)).grid(row=2, column=0, sticky="e", pady=20, padx=10)
        self.product_combo = ttk.Combobox(center, font=('Microsoft YaHei', 16), state="readonly", width=18)
        self.product_combo.grid(row=2, column=1, padx=10)

        # 查詢按鈕
        tk.Button(self, text="查詢銷貨", font=('Microsoft YaHei', 20), width=12,
                  command=self.query_order).place(relx=0.9, rely=0.9, anchor="se")

        # 載入下拉選單資料
        self.load_comboboxes()

    def load_comboboxes(self):
        # 載入顧客
        cur = self.conn.cursor()
        cur.execute("SELECT cust_name FROM customer")
        custs = [row[0] for row in cur.fetchall()]
        self.cust_combo["values"] = [""] + custs

        # 載入所有訂單日期
        cur.execute("SELECT DISTINCT order_date FROM `order` ORDER BY order_date DESC")
        dates = [row[0].strftime("%Y-%m-%d") for row in cur.fetchall()]
        self.date_combo["values"] = [""] + dates

        # 載入商品名稱
        cur.execute("SELECT product_name FROM product")
        prods = [row[0] for row in cur.fetchall()]
        self.product_combo["values"] = [""] + prods

    def query_order(self):
        cust = self.cust_combo.get()
        date = self.date_combo.get()
        prod = self.product_combo.get()

        cur = self.conn.cursor()

        # 組查詢語法
        sql = """
            SELECT o.order_num, c.cust_name, o.order_date, p.product_name, orc.quantity, orc.price, orc.sum
            FROM `order` o
            JOIN customer c ON o.customer = c.cust_num
            JOIN order_receipt orc ON o.order_num = orc.order_num
            JOIN product p ON orc.product_num = p.product_num
            WHERE 1=1
        """
        params = []
        if cust:
            sql += " AND c.cust_name = %s"
            params.append(cust)
        if date:
            sql += " AND o.order_date = %s"
            params.append(date)
        if prod:
            sql += " AND p.product_name = %s"
            params.append(prod)
        sql += " ORDER BY o.order_num ASC"

        cur.execute(sql, params)
        results = cur.fetchall()

        # 顯示結果
        if not results:
            messagebox.showinfo("查詢結果", "查無符合條件的銷貨紀錄。")
            return

        # 定義每個欄位寬度
        fmt = "{:<8} {:<12} {:<12} {:<12} {:>6} {:>8} {:>8}\n"
        result_text = fmt.format("訂單編號", "顧客", "日期", "商品", "數量", "單價", "小結")
        result_text += "-"*70 + "\n"
        for row in results:
            result_text += fmt.format(str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4]), str(row[5]), str(row[6]))

        # 彈窗顯示
        result_win = tk.Toplevel(self)
        result_win.title("查詢結果")
        result_win_width = 960
        result_win_height = 400
        result_win_anchor_left = int((result_win.winfo_screenwidth() - result_win_width)/2) #置中視窗
        result_win_anchor_top = int((result_win.winfo_screenheight() - result_win_height)/2)
        result_win.geometry(f'{result_win_width}x{result_win_height}+{result_win_anchor_left}+{result_win_anchor_top}')
        text = tk.Text(result_win, font=("Consolas", 14), width=70, height=20)
        text.insert(tk.END, result_text)
        text.config(state=tk.DISABLED)
        text.pack(expand=True, fill="both", padx=15, pady=15)

class StockMenuFrame(tk.Frame):
    def __init__(self, master, switch_frame):
        super().__init__(master)
        tk.Label(self, text="").pack(pady=60)
        tk.Label(self, text="存貨系統", font=('Microsoft YaHei',36)).pack(pady=90)
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 12), command=lambda: switch_frame("inventory_menu")).place(x=5, y=5)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="存貨查詢", font=('Microsoft YaHei', 24), command=lambda: switch_frame("stock_query")).pack(side="left", padx=10)
        #tk.Button(btn_frame, text="存貨修改", font=('Microsoft YaHei', 24), command=lambda: switch_frame("stock_mod")).pack(side="left", padx=10)

class StockQueryFrame(tk.Frame):
    def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        self.conn = conn

        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 16),
                  command=lambda: switch_frame("stock_menu")).place(x=20, y=20)
        tk.Label(self, text="存貨查詢", font=('Microsoft YaHei',36)).pack(pady=40)

        main_frame = tk.Frame(self)
        main_frame.pack(pady=30)

        tk.Label(main_frame, text="商品：", font=('Microsoft YaHei', 22)).grid(row=0, column=0, padx=10, pady=10)
        self.product_combo = ttk.Combobox(main_frame, state="readonly", font=('Microsoft YaHei', 16), width=20)
        self.product_combo.grid(row=0, column=1, padx=5, pady=10)

        self.load_products()

        tk.Button(self, text="查詢存貨", font=('Microsoft YaHei', 18), width=10,
                  command=self.query_stock).place(relx=0.88, rely=0.85)

    def load_products(self):
        cur = self.conn.cursor()
        cur.execute("SELECT product_name FROM product ORDER BY product_name")
        products = [row[0] for row in cur.fetchall()]
        self.product_combo['values'] = products

    def query_stock(self):
        prod_name = self.product_combo.get()
        if not prod_name:
            messagebox.showerror("錯誤", "請選擇商品")
            return
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT sv.product_num, sv.product_name, sv.stock_quantity, sv.stock_value, p.safe_stock
            FROM stock_view sv
            JOIN product p ON sv.product_num = p.product_num
            WHERE sv.product_name=%s
            """,
            (prod_name,)
        )
        row = cur.fetchone()
        if not row:
            messagebox.showinfo("查無資料", "資料庫中沒有該商品存貨資訊")
            return
        # 彈窗顯示
        info = (
            f"商品編號：{row[0]}\n"
            f"商品名稱：{row[1]}\n"
            f"商品存量：{row[2]}\n"
            f"安全庫存：{row[4]}\n"
            f"庫存價值：{row[3]}"
        )
        # 如果你有 show_info_popup，可以這樣呼叫：
        show_info_popup("商品存貨資訊", info)
        # 否則用 messagebox:
        #messagebox.showinfo("商品存貨資訊", info)
        if row[2] < row[4]:
            messagebox.showwarning(
                "存量警告",
                f"商品存量({row[2]})低於安全庫存({row[4]})，請盡速補貨",
            )


    '''def __init__(self, master, switch_frame, conn):
        super().__init__(master)
        tk.Label(self, text="存貨修改", font=('Microsoft YaHei',36)).pack(pady=90)
        tk.Button(self, text="返回上一頁", font=('Microsoft YaHei', 12), command=lambda: switch_frame("stock_menu")).place(x=5, y=5)'''

class App(tk.Tk):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.current_user_num = None

        self.title("生芳髮品")
        width = 960
        height = 720
        anchor_left = int((self.winfo_screenwidth() - width)/2) #置中視窗
        anchor_top = int((self.winfo_screenheight() - height)/2)
        self.geometry(f'{width}x{height}+{anchor_left}+{anchor_top}')
        self.minsize(960, 720)
        self.maxsize(1920, 1080)
        self.resizable(True, True)
        self.state('zoomed')
        self.configure(background="#C79A31")

        self.frames = {}

        def switch_frame(page):
            frame = self.frames[page]
            frame.tkraise()
            if hasattr(frame, "refresh"):
                frame.refresh()

        self.frames["login"] = LoginFrame(self, switch_frame, self.conn)
        self.frames["agent_menu"] = AgentMenuFrame(self, switch_frame)
        self.frames["admin_menu"] = AdminMenuFrame(self, switch_frame)
        self.frames["user_menu"] = UserMenuFrame(self, switch_frame)
        self.frames["user_add"] = UserAddFrame(self, switch_frame, self.conn)
        self.frames["user_query"] = UserQueryFrame(self, switch_frame, self.conn)
        self.frames["user_mod"] = UserModFrame(self, switch_frame, self.conn)
        self.frames["user_delete"] = UserDeleteFrame(self, switch_frame, self.conn)
        self.frames["order_menu"] = OrderMenuFrame(self, switch_frame)
        self.frames["order_add"] = OrderAddFrame(self, switch_frame, self.conn)
        self.frames["order_query"] = OrderQueryFrame(self, switch_frame, self.conn)
        self.frames["order_mod"] = OrderModFrame(self, switch_frame, self.conn)
        self.frames["order_delete"] = OrderDeleteFrame(self, switch_frame, self.conn)
        self.frames["customer_menu"] = CustomerMenuFrame(self, switch_frame)
        self.frames["customer_add"] = CustomerAddFrame(self, switch_frame, self.conn)
        self.frames["customer_query"] = CustomerQueryFrame(self, switch_frame, self.conn)
        self.frames["customer_mod"] = CustomerModFrame(self, switch_frame, self.conn)
        self.frames["product_menu"] = ProductMenuFrame(self, switch_frame)
        self.frames["product_add"] = ProductAddFrame(self, switch_frame, self.conn)
        self.frames["product_query"] = ProductQueryFrame(self, switch_frame, self.conn)
        self.frames["product_mod"] = ProductModFrame(self, switch_frame, self.conn)
        self.frames["product_delete"] = ProductDeleteFrame(self, switch_frame, self.conn)
        self.frames["inventory_menu"] = InventoryMenuFrame(self, switch_frame)
        self.frames["supplier_menu"] = SupplierMenuFrame(self, switch_frame)
        self.frames["supplier_add"] = SupplierAddFrame(self, switch_frame, self.conn)
        self.frames["supplier_query"] = SupplierQueryFrame(self, switch_frame, self.conn)
        self.frames["supplier_mod"] = SupplierModFrame(self, switch_frame, self.conn)
        self.frames["supplier_delete"] = SupplierDeleteFrame(self, switch_frame, self.conn)
        self.frames["purchase_menu"] = PurchaseMenuFrame(self, switch_frame)
        self.frames["purchase_add"] = PurchaseAddFrame(self, switch_frame, self.conn)
        self.frames["purchase_query"] = PurchaseQueryFrame(self, switch_frame, self.conn)
        self.frames["purchase_mod"] = PurchaseModFrame(self, switch_frame, self.conn)
        self.frames["purchase_delete"] = PurchaseDeleteFrame(self, switch_frame, self.conn)
        self.frames["sales_menu"] = SalesMenuFrame(self, switch_frame)
        self.frames["sales_report"] = SalesReportFrame(self, switch_frame, self.conn)
        self.frames["sales_query"] = SalesQueryFrame(self, switch_frame, self.conn)
        self.frames["stock_menu"] = StockMenuFrame(self, switch_frame)
        self.frames["stock_query"] = StockQueryFrame(self, switch_frame, self.conn)
        #self.frames["stock_mod"] = StockModFrame(self, switch_frame, self.conn)

        for f in self.frames.values():
            f.place(relwidth=1, relheight=1)

        switch_frame("login")  # 預設顯示登入頁

if __name__ == "__main__":
    import pymysql
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="Kumura_To_71",
        db="salon_db",
        charset="utf8mb4")

    app = App(conn)
    app.mainloop()
    conn.close()
