# **Lost & Found Management System (Tkinter + MySQL)**  

A simple and complete **DBMS project** built using **Python Tkinter** as the GUI frontend and **MySQL** as the backend.  
The application manages **Users, Locations, Items, and Claims** with full CRUD support, stored procedures, functions, triggers, and advanced SQL queries.

---

## 🚀 Features
- **Tkinter GUI Frontend**
  - Tab-based interface
  - Treeview tables for records
  - Input validation & messages
- **MySQL Backend**
  - Users with roles (`student`, `staff`, `admin`)
  - Items, Locations, and Claims with foreign keys
  - Stored Procedures:
    - `add_item()`
    - `update_claim_status()`
  - Function:
    - `count_items_by_user()`
  - Triggers:
    - Auto-append timestamp on item insert  
    - Auto-update item status when a claim is approved  
- **Query Hub**
  - Nested Query  
  - Join Query  
  - Aggregate Query  
  - Function call output  

---

## 🛠 Tech Stack
- **Frontend:** Python Tkinter, ttk widgets  
- **Backend:** MySQL  
- **Connector:** `mysql-connector-python`

Install dependency:
```bash
pip install mysql-connector-python
```

---

## 📦 How to Run
1. Import the SQL schema (tables, procedures, triggers).
2. Update your DB credentials in the `DB_CONFIG` dictionary.
3. Run the Python script:
```bash
python main.py
```
