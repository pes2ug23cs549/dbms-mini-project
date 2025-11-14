# Lost & Found DBMS Project - Tkinter GUI (MySQL)
# ------------------------------------------------
# Covers rubric:
# - Users creation/varied privileges (via 'role')
# - Full CRUD with GUI (Users, Locations, Items, Claims)
# - Uses Procedures: add_item(), update_claim_status()
# - Uses Function: count_items_by_user()
# - Shows Queries with GUI: Nested, Join, Aggregate
#
# Requirements: pip install mysql-connector-python

import mysql.connector
from mysql.connector import Error
from tkinter import *
from tkinter import ttk, messagebox

# ---------------------- CONFIG ----------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "shivam@123",        
    "database": "lostfound"
}

# ---------------------- DB HELPERS ----------------------
def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def run_query(sql, params=None):
    con = get_conn()
    try:
        cur = con.cursor()
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        return rows
    finally:
        con.close()

def run_exec(sql, params=None, many=False):
    con = get_conn()
    try:
        cur = con.cursor()
        if many:
            cur.executemany(sql, params)
        else:
            cur.execute(sql, params or ())
        con.commit()
        return cur.rowcount
    finally:
        con.close()

def call_proc(name, params=()):
    con = get_conn()
    try:
        cur = con.cursor()
        cur.callproc(name, params)
        con.commit()
        # Collect any result sets from procedures (if they SELECT)
        results = []
        for result in cur.stored_results():
            results.extend(result.fetchall())
        return results
    finally:
        con.close()

# ---------------------- COMMON UI HELPERS ----------------------
def clear_tree(tree):
    for i in tree.get_children():
        tree.delete(i)

def fill_tree(tree, rows, columns=None):
    # Clear old data
    for i in tree.get_children():
        tree.delete(i)

    # Reset columns dynamically if given
    if columns:
        tree["columns"] = columns
        tree["show"] = "headings"
        for col in columns:
            tree.heading(col, text=col.upper())
            tree.column(col, width=150, anchor="center")

    # Insert new data
    for r in rows:
        tree.insert("", "end", values=r)

def msg_info(text):
    messagebox.showinfo("Info", text)

def msg_err(e):
    messagebox.showerror("Error", str(e))

# ---------------------- MAIN WINDOW ----------------------
root = Tk()
root.title("Lost & Found - DBMS Project (MySQL + Tkinter)")
root.geometry("1100x700")

nb = ttk.Notebook(root)
nb.pack(fill=BOTH, expand=True)

# ============================================================
# TAB 1: USERS (Create/Read/Update/Delete + role)
# ============================================================
tab_users = Frame(nb)
nb.add(tab_users, text="Users")

u_cols = ("user_id", "name", "email", "phone", "role")
tree_users = ttk.Treeview(tab_users, columns=u_cols, show="headings", height=12)
for c in u_cols:
    tree_users.heading(c, text=c.upper())
    tree_users.column(c, width=150 if c!="email" else 220)
tree_users.pack(fill=BOTH, expand=True, padx=10, pady=10)

frm_u = Frame(tab_users)
frm_u.pack(fill=X, padx=10, pady=6)

Label(frm_u, text="Name").grid(row=0, column=0, sticky="w")
ent_u_name = Entry(frm_u, width=20)
ent_u_name.grid(row=0, column=1, padx=5)

Label(frm_u, text="Email").grid(row=0, column=2, sticky="w")
ent_u_email = Entry(frm_u, width=28)
ent_u_email.grid(row=0, column=3, padx=5)

Label(frm_u, text="Phone").grid(row=0, column=4, sticky="w")
ent_u_phone = Entry(frm_u, width=16)
ent_u_phone.grid(row=0, column=5, padx=5)

Label(frm_u, text="Role").grid(row=0, column=6, sticky="w")
cmb_u_role = ttk.Combobox(frm_u, values=["student","staff","admin"], width=12, state="readonly")
cmb_u_role.set("student")
cmb_u_role.grid(row=0, column=7, padx=5)

def refresh_users():
    try:
        rows = run_query("SELECT user_id, name, email, phone, role FROM users ORDER BY user_id")
        fill_tree(tree_users, rows)
    except Exception as e:
        msg_err(e)

def user_add():
    try:
        name = ent_u_name.get().strip()
        email = ent_u_email.get().strip()
        phone = ent_u_phone.get().strip()
        role = cmb_u_role.get()
        if not name or not email:
            return msg_info("Name and Email are required.")
        run_exec("INSERT INTO users(name,email,phone,role) VALUES(%s,%s,%s,%s)",
                 (name, email, phone, role))
        refresh_users()
        refresh_dropdowns()   # 🔥 Add this line
        msg_info("User added.")
    except Error as e:
        msg_err(e)


def user_update():
    sel = tree_users.selection()
    if not sel:
        return msg_info("Select a user row to update.")
    user_id = tree_users.item(sel[0])["values"][0]
    try:
        run_exec("UPDATE users SET name=%s, email=%s, phone=%s, role=%s WHERE user_id=%s",
                 (ent_u_name.get().strip(), ent_u_email.get().strip(),
                  ent_u_phone.get().strip(), cmb_u_role.get(), user_id))
        refresh_users()
        refresh_dropdowns()   # 🔥 Add this line
        msg_info("User updated.")
    except Error as e:
        msg_err(e)


def user_delete():
    sel = tree_users.selection()
    if not sel:
        return msg_info("Select a user row to delete.")
    user_id = tree_users.item(sel[0])["values"][0]
    try:
        run_exec("DELETE FROM users WHERE user_id=%s", (user_id,))
        refresh_users()
        refresh_dropdowns()   # 🔥 Add this line
        msg_info("User deleted.")
    except Error as e:
        msg_err(e)

def user_on_select(event):
    sel = tree_users.selection()
    if not sel: return
    vals = tree_users.item(sel[0])["values"]
    ent_u_name.delete(0, END); ent_u_name.insert(0, vals[1])
    ent_u_email.delete(0, END); ent_u_email.insert(0, vals[2])
    ent_u_phone.delete(0, END); ent_u_phone.insert(0, vals[3])
    cmb_u_role.set(vals[4])

tree_users.bind("<<TreeviewSelect>>", user_on_select)

btn_u_bar = Frame(tab_users)
btn_u_bar.pack(fill=X, padx=10, pady=6)
Button(btn_u_bar, text="Add User", command=user_add, bg="#b6f2b6").pack(side=LEFT, padx=4)
Button(btn_u_bar, text="Update User", command=user_update, bg="#ffd27f").pack(side=LEFT, padx=4)
Button(btn_u_bar, text="Delete User", command=user_delete, bg="#ff9a9a").pack(side=LEFT, padx=4)
Button(btn_u_bar, text="Refresh", command=refresh_users).pack(side=LEFT, padx=4)

# ============================================================
# TAB 2: LOCATIONS (CRUD)
# ============================================================
tab_locs = Frame(nb)
nb.add(tab_locs, text="Locations")

l_cols = ("location_id", "location_name", "building", "floor_no")
tree_locs = ttk.Treeview(tab_locs, columns=l_cols, show="headings", height=10)
for c in l_cols:
    tree_locs.heading(c, text=c.upper())
    tree_locs.column(c, width=200 if c=="location_name" else 120)
tree_locs.pack(fill=BOTH, expand=True, padx=10, pady=10)

frm_l = Frame(tab_locs)
frm_l.pack(fill=X, padx=10, pady=6)

Label(frm_l, text="Location Name").grid(row=0, column=0, sticky="w")
ent_l_name = Entry(frm_l, width=24)
ent_l_name.grid(row=0, column=1, padx=5)

Label(frm_l, text="Building").grid(row=0, column=2, sticky="w")
ent_l_building = Entry(frm_l, width=16)
ent_l_building.grid(row=0, column=3, padx=5)

Label(frm_l, text="Floor No").grid(row=0, column=4, sticky="w")
ent_l_floor = Entry(frm_l, width=8)
ent_l_floor.grid(row=0, column=5, padx=5)

def refresh_locs():
    try:
        rows = run_query("SELECT location_id, location_name, building, floor_no FROM locations ORDER BY location_id")
        fill_tree(tree_locs, rows)
        refresh_dropdowns()  # keep dependent dropdowns in sync
    except Exception as e:
        msg_err(e)

def loc_add():
    try:
        run_exec("INSERT INTO locations(location_name,building,floor_no) VALUES(%s,%s,%s)",
                 (ent_l_name.get().strip(), ent_l_building.get().strip(), ent_l_floor.get() or None))
        refresh_locs()
        msg_info("Location added.")
    except Error as e:
        msg_err(e)

def loc_update():
    sel = tree_locs.selection()
    if not sel:
        return msg_info("Select a location row to update.")
    loc_id = tree_locs.item(sel[0])["values"][0]
    try:
        run_exec("UPDATE locations SET location_name=%s,building=%s,floor_no=%s WHERE location_id=%s",
                 (ent_l_name.get().strip(), ent_l_building.get().strip(),
                  ent_l_floor.get() or None, loc_id))
        refresh_locs()
        msg_info("Location updated.")
    except Error as e:
        msg_err(e)

def loc_delete():
    sel = tree_locs.selection()
    if not sel:
        return msg_info("Select a location row to delete.")
    loc_id = tree_locs.item(sel[0])["values"][0]
    try:
        run_exec("DELETE FROM locations WHERE location_id=%s", (loc_id,))
        refresh_locs()
        msg_info("Location deleted.")
    except Error as e:
        msg_err(e)

def loc_on_select(event):
    sel = tree_locs.selection()
    if not sel: return
    vals = tree_locs.item(sel[0])["values"]
    ent_l_name.delete(0, END); ent_l_name.insert(0, vals[1])
    ent_l_building.delete(0, END); ent_l_building.insert(0, vals[2] if vals[2] is not None else "")
    ent_l_floor.delete(0, END); ent_l_floor.insert(0, "" if vals[3] is None else vals[3])

tree_locs.bind("<<TreeviewSelect>>", loc_on_select)

btn_l_bar = Frame(tab_locs)
btn_l_bar.pack(fill=X, padx=10, pady=6)
Button(btn_l_bar, text="Add Location", command=loc_add, bg="#b6f2b6").pack(side=LEFT, padx=4)
Button(btn_l_bar, text="Update", command=loc_update, bg="#ffd27f").pack(side=LEFT, padx=4)
Button(btn_l_bar, text="Delete", command=loc_delete, bg="#ff9a9a").pack(side=LEFT, padx=4)
Button(btn_l_bar, text="Refresh", command=refresh_locs).pack(side=LEFT, padx=4)

# ============================================================
# TAB 3: ITEMS (CRUD + Procedure add_item + Trigger on insert)
# ============================================================
tab_items = Frame(nb)
nb.add(tab_items, text="Items")

i_cols = ("item_id","item_name","description","category","status","report_date","reported_by","location_id")
tree_items = ttk.Treeview(tab_items, columns=i_cols, show="headings", height=12)
for c in i_cols:
    tree_items.heading(c, text=c.upper())
    tree_items.column(c, width=150 if c not in ("description","item_name") else 240)
tree_items.pack(fill=BOTH, expand=True, padx=10, pady=10)

frm_i = Frame(tab_items)
frm_i.pack(fill=X, padx=10, pady=6)

Label(frm_i, text="Name").grid(row=0, column=0, sticky="w")
ent_i_name = Entry(frm_i, width=22); ent_i_name.grid(row=0, column=1, padx=5)

Label(frm_i, text="Category").grid(row=0, column=2, sticky="w")
ent_i_cat = Entry(frm_i, width=14); ent_i_cat.grid(row=0, column=3, padx=5)

Label(frm_i, text="Status").grid(row=0, column=4, sticky="w")
cmb_i_status = ttk.Combobox(frm_i, values=["lost","found"], width=10, state="readonly")
cmb_i_status.set("lost"); cmb_i_status.grid(row=0, column=5, padx=5)

Label(frm_i, text="User (reported_by)").grid(row=1, column=0, sticky="w")
cmb_i_user = ttk.Combobox(frm_i, width=22, state="readonly")
cmb_i_user.grid(row=1, column=1, padx=5)

Label(frm_i, text="Location").grid(row=1, column=2, sticky="w")
cmb_i_loc = ttk.Combobox(frm_i, width=16, state="readonly")
cmb_i_loc.grid(row=1, column=3, padx=5)

Label(frm_i, text="Description").grid(row=1, column=4, sticky="w")
ent_i_desc = Entry(frm_i, width=40); ent_i_desc.grid(row=1, column=5, padx=5)

def refresh_dropdowns():
    # Users
    users = run_query("SELECT user_id, name FROM users ORDER BY name")
    if users:
        cmb_i_user["values"] = [f"{u[0]} - {u[1]}" for u in users]
        cmb_c_claimer["values"] = [f"{u[0]} - {u[1]}" for u in users]
        cmb_q_user["values"] = [f"{u[0]} - {u[1]}" for u in users]
    # Locations
    locs = run_query("SELECT location_id, location_name FROM locations ORDER BY location_name")
    if locs:
        cmb_i_loc["values"] = [f"{l[0]} - {l[1]}" for l in locs]

def get_selected_id_from_combo(combo):
    val = combo.get().strip()
    if not val or "-" not in val: return None
    return int(val.split("-")[0].strip())

def refresh_items():
    try:
        rows = run_query("""SELECT item_id,item_name,description,category,status,report_date,reported_by,location_id
                            FROM items ORDER BY item_id""")
        fill_tree(tree_items, rows)
    except Exception as e:
        msg_err(e)

def item_add_via_proc():
    try:
        name = ent_i_name.get().strip()
        desc = ent_i_desc.get().strip()
        cat = ent_i_cat.get().strip()
        status = cmb_i_status.get()
        uid = get_selected_id_from_combo(cmb_i_user)
        lid = get_selected_id_from_combo(cmb_i_loc)
        if not (name and uid and lid and status):
            return msg_info("Name, Status, User, Location required.")
        # CALL add_item(p_name, p_desc, p_cat, p_status, p_user, p_loc)
        call_proc('add_item', (name, desc, cat, status, uid, lid))
        refresh_items()
        msg_info("Item added via procedure. (Insert trigger auto-appended timestamp to description.)")
    except Error as e:
        msg_err(e)

def item_update():
    sel = tree_items.selection()
    if not sel:
        return msg_info("Select an item row to update.")
    item_id = tree_items.item(sel[0])["values"][0]
    try:
        run_exec("""UPDATE items SET item_name=%s, description=%s, category=%s, status=%s,
                                reported_by=%s, location_id=%s WHERE item_id=%s""",
                 (ent_i_name.get().strip(), ent_i_desc.get().strip(), ent_i_cat.get().strip(),
                  cmb_i_status.get(), get_selected_id_from_combo(cmb_i_user),
                  get_selected_id_from_combo(cmb_i_loc), item_id))
        refresh_items()
        msg_info("Item updated.")
    except Error as e:
        msg_err(e)

def item_delete():
    sel = tree_items.selection()
    if not sel:
        return msg_info("Select an item row to delete.")
    item_id = tree_items.item(sel[0])["values"][0]
    try:
        run_exec("DELETE FROM items WHERE item_id=%s", (item_id,))
        refresh_items()
        msg_info("Item deleted.")
    except Error as e:
        msg_err(e)

def item_on_select(event):
    sel = tree_items.selection()
    if not sel: return
    vals = tree_items.item(sel[0])["values"]
    ent_i_name.delete(0, END); ent_i_name.insert(0, vals[1])
    ent_i_desc.delete(0, END); ent_i_desc.insert(0, vals[2] if vals[2] else "")
    ent_i_cat.delete(0, END); ent_i_cat.insert(0, vals[3] if vals[3] else "")
    cmb_i_status.set(vals[4])
    # set user and location combos to matching id prefix
    uid = vals[6]; lid = vals[7]
    for v in cmb_i_user["values"]:
        if v.startswith(str(uid) + " -"):
            cmb_i_user.set(v); break
    for v in cmb_i_loc["values"]:
        if v.startswith(str(lid) + " -"):
            cmb_i_loc.set(v); break

tree_items.bind("<<TreeviewSelect>>", item_on_select)

btn_i_bar = Frame(tab_items)
btn_i_bar.pack(fill=X, padx=10, pady=6)
Button(btn_i_bar, text="Add Item (Procedure)", command=item_add_via_proc, bg="#b6f2b6").pack(side=LEFT, padx=4)
Button(btn_i_bar, text="Update", command=item_update, bg="#ffd27f").pack(side=LEFT, padx=4)
Button(btn_i_bar, text="Delete", command=item_delete, bg="#ff9a9a").pack(side=LEFT, padx=4)
Button(btn_i_bar, text="Refresh", command=refresh_items).pack(side=LEFT, padx=4)

# ============================================================
# TAB 4: CLAIMS (CRUD + Procedure approve/reject + Trigger updates item)
# ============================================================
tab_claims = Frame(nb)
nb.add(tab_claims, text="Claims")

c_cols = ("claim_id","item_id","claimer_id","claim_date","status","remarks")
tree_claims = ttk.Treeview(tab_claims, columns=c_cols, show="headings", height=12)
for c in c_cols:
    tree_claims.heading(c, text=c.upper())
    tree_claims.column(c, width=150)
tree_claims.pack(fill=BOTH, expand=True, padx=10, pady=10)

frm_c1 = Frame(tab_claims); frm_c1.pack(fill=X, padx=10, pady=6)

Label(frm_c1, text="Item ID").grid(row=0, column=0, sticky="w")
ent_c_item = Entry(frm_c1, width=10); ent_c_item.grid(row=0, column=1, padx=5)

Label(frm_c1, text="Claimer").grid(row=0, column=2, sticky="w")
cmb_c_claimer = ttk.Combobox(frm_c1, width=28, state="readonly"); cmb_c_claimer.grid(row=0, column=3, padx=5)

Label(frm_c1, text="Remarks").grid(row=0, column=4, sticky="w")
ent_c_remarks = Entry(frm_c1, width=40); ent_c_remarks.grid(row=0, column=5, padx=5)

frm_c2 = Frame(tab_claims); frm_c2.pack(fill=X, padx=10, pady=6)

def refresh_claims():
    try:
        rows = run_query("SELECT claim_id,item_id,claimer_id,claim_date,status,remarks FROM claims ORDER BY claim_id")
        fill_tree(tree_claims, rows)
    except Exception as e:
        msg_err(e)

def claim_add():
    try:
        item_id = int(ent_c_item.get())
        claimer = get_selected_id_from_combo(cmb_c_claimer)
        remarks = ent_c_remarks.get().strip()
        run_exec("INSERT INTO claims(item_id, claimer_id, remarks) VALUES(%s,%s,%s)",
                 (item_id, claimer, remarks))
        refresh_claims()
        msg_info("Claim added (status=pending).")
    except Exception as e:
        msg_err(e)

def claim_update_status(decision):
    sel = tree_claims.selection()
    if not sel:
        return msg_info("Select a claim row first.")
    claim_id = tree_claims.item(sel[0])["values"][0]
    try:
        # CALL update_claim_status(p_claim_id, p_status, p_remark)
        call_proc('update_claim_status', (int(claim_id), decision, ent_c_remarks.get().strip()))
        refresh_claims()
        refresh_items()
        msg_info(f"Claim {decision}. (Trigger updated item status/description if approved.)")
    except Exception as e:
        msg_err(e)

def claim_delete():
    sel = tree_claims.selection()
    if not sel:
        return msg_info("Select a claim row to delete.")
    cid = tree_claims.item(sel[0])["values"][0]
    try:
        run_exec("DELETE FROM claims WHERE claim_id=%s", (cid,))
        refresh_claims()
        msg_info("Claim deleted.")
    except Exception as e:
        msg_err(e)

Button(frm_c2, text="Add Claim", command=claim_add, bg="#b6f2b6").pack(side=LEFT, padx=4)
Button(frm_c2, text="Approve (Procedure+Trigger)", command=lambda: claim_update_status('approved'), bg="#99ffcc").pack(side=LEFT, padx=4)
Button(frm_c2, text="Reject (Procedure)", command=lambda: claim_update_status('rejected'), bg="#ffd27f").pack(side=LEFT, padx=4)
Button(frm_c2, text="Delete", command=claim_delete, bg="#ff9a9a").pack(side=LEFT, padx=4)
Button(frm_c2, text="Refresh", command=refresh_claims).pack(side=LEFT, padx=4)

# ============================================================
# TAB 5: QUERIES (Nested / Join / Aggregate) + Function call
# ============================================================
tab_queries = Frame(nb)
nb.add(tab_queries, text="Queries & Stats")

# Result grid
q_cols = ("c1","c2","c3","c4","c5","c6","c7","c8")
tree_q = ttk.Treeview(tab_queries, columns=q_cols, show="headings", height=16)
for c in q_cols:
    tree_q.heading(c, text=c.upper())
    tree_q.column(c, width=150)
tree_q.pack(fill=BOTH, expand=True, padx=10, pady=10)

frm_q = Frame(tab_queries); frm_q.pack(fill=X, padx=10, pady=6)

# Function: count_items_by_user
Label(frm_q, text="User for count_items_by_user():").grid(row=0, column=0, sticky="w")
cmb_q_user = ttk.Combobox(frm_q, width=30, state="readonly"); cmb_q_user.grid(row=0, column=1, padx=5)

def show_function_count():
    uid = get_selected_id_from_combo(cmb_q_user)
    if not uid:
        return msg_info("Choose a user.")
    try:
        rows = run_query("SELECT count_items_by_user(%s)", (uid,))
        columns = ["User ID", "Total Items Reported"]
        fill_tree(tree_q, [(uid, rows[0][0])], columns)
    except Exception as e:
        msg_err(e)

# Nested query
def run_nested_query():
    sql = """
    SELECT name, user_id
    FROM users
    WHERE user_id IN (
        SELECT reported_by
        FROM items
        GROUP BY reported_by
        HAVING COUNT(item_id) > (
            SELECT AVG(item_count)
            FROM (
                SELECT COUNT(item_id) AS item_count
                FROM items
                GROUP BY reported_by
            ) AS sub
        )
    )
    """
    try:
        rows = run_query(sql)
        columns = ["Name", "User ID"]
        fill_tree(tree_q, rows, columns)
    except Exception as e:
        msg_err(e)

# Join query
def run_join_query():
    sql = """
    SELECT 
        c.claim_id,
        i.item_name,
        u.name AS claimer_name,
        c.status AS claim_status,
        i.status AS item_status
    FROM claims c
    JOIN items i ON c.item_id = i.item_id
    JOIN users u ON c.claimer_id = u.user_id
    ORDER BY c.claim_id
    """
    try:
        rows = run_query(sql)
        columns = ["Claim ID", "Item Name", "Claimer Name", "Claim Status", "Item Status"]
        fill_tree(tree_q, rows, columns)
    except Exception as e:
        msg_err(e)

# Aggregate query
def run_aggregate_query():
    sql = """
    SELECT category, COUNT(item_id) AS total_items
    FROM items
    GROUP BY category
    ORDER BY total_items DESC
    """
    try:
        rows = run_query(sql)
        columns = ["Category", "Total Items"]
        fill_tree(tree_q, rows, columns)
    except Exception as e:
        msg_err(e)

btn_q_bar = Frame(tab_queries); btn_q_bar.pack(fill=X, padx=10, pady=6)
Button(btn_q_bar, text="Run Nested Query", command=run_nested_query, bg="#e0f7fa").pack(side=LEFT, padx=4)
Button(btn_q_bar, text="Run Join Query", command=run_join_query, bg="#e8f5e9").pack(side=LEFT, padx=4)
Button(btn_q_bar, text="Run Aggregate Query", command=run_aggregate_query, bg="#fff9c4").pack(side=LEFT, padx=4)
Button(btn_q_bar, text="Function: count_items_by_user()", command=show_function_count, bg="#d1c4e9").pack(side=LEFT, padx=4)

# ---------------------- INITIAL LOAD ----------------------
refresh_dropdowns()
refresh_users()
refresh_locs()
refresh_items()
refresh_claims()

root.mainloop()
