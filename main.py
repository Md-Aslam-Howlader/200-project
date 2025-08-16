import mysql.connector
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv

# ===================== Database =====================
DB_NAME = "citizen_portal"

def connect_db(db_name=None):
    config = {"host": "localhost", "user": "root", "password": ""}
    if db_name:
        config["database"] = db_name
    return mysql.connector.connect(**config)

def create_database():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    conn.close()

def create_tables():
    conn = connect_db(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            citizen_name VARCHAR(100) NOT NULL,
            problem_type VARCHAR(50) NOT NULL,
            description TEXT NOT NULL,
            location VARCHAR(100) NOT NULL,
            status VARCHAR(20) DEFAULT 'Pending',
            report_date DATETIME
        )
    """)
    conn.commit()
    conn.close()

create_database()
create_tables()

# ===================== Admin Credentials =====================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ===================== Functions =====================
def submit_report():
    name = entry_name.get()
    problem = combo_problem.get()
    desc = text_desc.get("1.0", END).strip()
    location = entry_location.get()
    if not (name and problem and desc and location):
        messagebox.showerror("Error", "All fields are required!")
        return
    conn = connect_db(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reports (citizen_name, problem_type, description, location, report_date)
        VALUES (%s,%s,%s,%s,%s)
    """, (name, problem, desc, location, datetime.now()))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Report submitted successfully!")
    clear_form()

def view_my_reports():
    name = entry_view_name.get()
    conn = connect_db(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE citizen_name=%s", (name,))
    rows = cursor.fetchall()
    conn.close()
    update_tree(rows)

def view_all_reports():
    conn = connect_db(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports")
    rows = cursor.fetchall()
    conn.close()
    update_tree(rows)

def update_status():
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "Select a report!")
        return
    report_id = tree.item(selected)["values"][0]
    new_status = combo_status.get()
    if not new_status:
        messagebox.showerror("Error", "Select a new status!")
        return
    conn = connect_db(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE reports SET status=%s WHERE id=%s", (new_status, report_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Status updated successfully!")
    view_all_reports()

def delete_report():
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "Select a report to delete!")
        return
    report_id = tree.item(selected)["values"][0]
    conn = connect_db(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reports WHERE id=%s", (report_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Report deleted successfully!")
    view_all_reports()

def search_by_problem():
    problem = combo_search_problem.get()
    if not problem:
        messagebox.showerror("Error", "Select a problem type!")
        return
    conn = connect_db(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE problem_type=%s", (problem,))
    rows = cursor.fetchall()
    conn.close()
    update_tree(rows)

def filter_by_status():
    status = combo_filter_status.get()
    if not status:
        messagebox.showerror("Error", "Select a status!")
        return
    conn = connect_db(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE status=%s", (status,))
    rows = cursor.fetchall()
    conn.close()
    update_tree(rows)

def sort_by_date():
    conn = connect_db(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports ORDER BY report_date DESC")
    rows = cursor.fetchall()
    conn.close()
    update_tree(rows)

def export_to_csv():
    if not tree.get_children():
        messagebox.showerror("Error", "No reports to export!")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
    if not file_path:
        return
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID","Name","Problem","Description","Location","Status","Date"])
        for row_id in tree.get_children():
            row = tree.item(row_id)["values"]
            writer.writerow(row)
    messagebox.showinfo("Success", f"Reports exported to {file_path}")

def clear_form():
    entry_name.delete(0, END)
    combo_problem.set("")
    text_desc.delete("1.0", END)
    entry_location.delete(0, END)

def update_tree(rows):
    for row in tree.get_children():
        tree.delete(row)
    for row in rows:
        tree.insert("", END, values=row)

def login():
    username = entry_login_user.get()
    password = entry_login_pass.get()
    login_frame.pack_forget()
    main_frame.pack(fill="both", expand=True)

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        messagebox.showinfo("Welcome", "Logged in as Admin")
        # Admin buttons show
        btn_view_my.grid_remove()  # Citizen button hide
        btn_view_all.grid()
        btn_update_status.grid()
        btn_delete.grid()
        btn_export.grid()
        btn_filter.grid()
        btn_search.grid()
        btn_sort.grid()
    else:
        messagebox.showinfo("Welcome", f"Logged in as {username}")
        # Citizen buttons show
        btn_view_my.grid()
        btn_view_all.grid_remove()
        btn_update_status.grid_remove()
        btn_delete.grid_remove()
        btn_export.grid_remove()
        btn_filter.grid_remove()
        btn_search.grid_remove()
        btn_sort.grid_remove()

# ===================== GUI =====================
root = Tk()
root.title("Citizen Help Portal")
root.geometry("1000x650")

# ===== Login Frame =====
login_frame = Frame(root)
login_frame.pack(fill="both", expand=True)

Label(login_frame, text="Username:").grid(row=0, column=0, padx=10, pady=10)
entry_login_user = Entry(login_frame)
entry_login_user.grid(row=0, column=1, padx=10, pady=10)

Label(login_frame, text="Password:").grid(row=1, column=0, padx=10, pady=10)
entry_login_pass = Entry(login_frame, show="*")
entry_login_pass.grid(row=1, column=1, padx=10, pady=10)

Button(login_frame, text="Login", command=login).grid(row=2, column=0, columnspan=2, pady=10)

# ===== Main Frame =====
main_frame = Frame(root)

# Submit Frame
frame_submit = LabelFrame(main_frame, text="Submit Report", padx=10, pady=10)
frame_submit.pack(fill="x", padx=10, pady=5)

Label(frame_submit, text="Name:").grid(row=0, column=0)
entry_name = Entry(frame_submit, width=30)
entry_name.grid(row=0, column=1)

Label(frame_submit, text="Problem Type:").grid(row=1, column=0)
combo_problem = ttk.Combobox(frame_submit, values=["Health","Corruption","Extortion","Other"], width=28)
combo_problem.grid(row=1, column=1)

Label(frame_submit, text="Description:").grid(row=2, column=0)
text_desc = Text(frame_submit, width=40, height=3)
text_desc.grid(row=2, column=1)

Label(frame_submit, text="Location:").grid(row=3, column=0)
entry_location = Entry(frame_submit, width=30)
entry_location.grid(row=3, column=1)

Button(frame_submit, text="Submit Report", command=submit_report).grid(row=4, column=0, pady=5)
Button(frame_submit, text="Clear Form", command=clear_form).grid(row=4, column=1, pady=5)

# View Frame
frame_view = LabelFrame(main_frame, text="View Reports", padx=10, pady=10)
frame_view.pack(fill="x", padx=10, pady=5)

Label(frame_view, text="Enter Your Name:").grid(row=0, column=0)
entry_view_name = Entry(frame_view, width=30)
entry_view_name.grid(row=0, column=1)

btn_view_my = Button(frame_view, text="View My Reports", command=view_my_reports)
btn_view_my.grid(row=0, column=2, padx=5)

btn_view_all = Button(frame_view, text="View All Reports (Admin)", command=view_all_reports)
btn_view_all.grid(row=0, column=3, padx=5)

# Treeview
columns = ("ID","Name","Problem","Description","Location","Status","Date")
tree = ttk.Treeview(main_frame, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)
tree.pack(fill="both", expand=True, padx=10, pady=5)

# Admin Controls
frame_admin = LabelFrame(main_frame, text="Admin Controls", padx=10, pady=10)
frame_admin.pack(fill="x", padx=10, pady=5)

combo_status = ttk.Combobox(frame_admin, values=["Pending","In Progress","Resolved"], width=20)
combo_status.grid(row=0, column=0, padx=5, pady=5)
btn_update_status = Button(frame_admin, text="Update Status", command=update_status)
btn_update_status.grid(row=0, column=1, padx=5, pady=5)

btn_delete = Button(frame_admin, text="Delete Selected", command=delete_report)
btn_delete.grid(row=0, column=2, padx=5, pady=5)

btn_export = Button(frame_admin, text="Export CSV", command=export_to_csv)
btn_export.grid(row=0, column=3, padx=5, pady=5)

combo_filter_status = ttk.Combobox(frame_admin, values=["Pending","In Progress","Resolved"], width=20)
combo_filter_status.grid(row=1, column=0, padx=5, pady=5)
btn_filter = Button(frame_admin, text="Filter by Status", command=filter_by_status)
btn_filter.grid(row=1, column=1, padx=5, pady=5)

combo_search_problem = ttk.Combobox(frame_admin, values=["Health","Corruption","Extortion","Other"], width=20)
combo_search_problem.grid(row=1, column=2, padx=5, pady=5)
btn_search = Button(frame_admin, text="Search by Problem", command=search_by_problem)
btn_search.grid(row=1, column=3, padx=5, pady=5)

btn_sort = Button(frame_admin, text="Sort by Date", command=sort_by_date)
btn_sort.grid(row=2, column=0, padx=5, pady=5)

root.mainloop()
