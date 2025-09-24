import sqlite3

def init_db():
    """Initializes the database and creates the contacts table if it doesn't exist."""
    conn = sqlite3.connect('contacts.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            category TEXT DEFAULT 'Other',
            notes TEXT,
            favorite INTEGER DEFAULT 0,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def add_contact_db(conn, name, phone, email, address='', category='Other', notes='', favorite=0):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO contacts (name, phone, email, address, category, notes, favorite) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, phone, email, address, category, notes, favorite)
    )
    conn.commit()

def get_all_contacts_db(conn, search_term='', category_filter='All'):
    cursor = conn.cursor()
    query = "SELECT id, name, phone, email, address, category, notes, favorite FROM contacts WHERE 1=1"
    params = []
    
    if search_term:
        query += " AND (name LIKE ? OR phone LIKE ? OR email LIKE ? OR notes LIKE ?)"
        search_param = f"%{search_term}%"
        params.extend([search_param, search_param, search_param, search_param])
    
    if category_filter != 'All':
        query += " AND category = ?"
        params.append(category_filter)
    
    query += " ORDER BY favorite DESC, name ASC"
    cursor.execute(query, params)
    return cursor.fetchall()

def update_contact_db(conn, contact_id, name, phone, email, address='', category='Other', notes='', favorite=0):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE contacts SET name = ?, phone = ?, email = ?, address = ?, category = ?, notes = ?, favorite = ? WHERE id = ?",
        (name, phone, email, address, category, notes, favorite, contact_id)
    )
    conn.commit()

def toggle_favorite_db(conn, contact_id):
    cursor = conn.cursor()
    cursor.execute("UPDATE contacts SET favorite = 1 - favorite WHERE id = ?", (contact_id,))
    conn.commit()

def delete_contact_db(conn, contact_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.commit()