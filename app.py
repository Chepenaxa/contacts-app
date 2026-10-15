import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# Настройка базы данных
DB_NAME = 'contacts.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 1. Получить все контакты
@app.route('/contacts', methods=['GET'])
def get_contacts():
    conn = get_db_connection()
    contacts = conn.execute('SELECT * FROM contacts').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in contacts])

# 2. Получить контакт по ID
@app.route('/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    conn = get_db_connection()
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)).fetchone()
    conn.close()
    if contact is None:
        return jsonify({'error': 'Контакт не найден'}), 404
    return jsonify(dict(contact))

# 3. Создать новый контакт
@app.route('/contacts', methods=['POST'])
def add_contact():
    data = request.get_json()
    if not data or 'name' not in data or 'phone' not in data:
        return jsonify({'error': 'Необходимо указать name и phone'}), 400
    
    conn = get_db_connection()
    cursor = conn.execute('INSERT INTO contacts (name, phone) VALUES (?, ?)', 
                          (data['name'], data['phone']))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'id': new_id, 'name': data['name'], 'phone': data['phone']}), 201

# 4. Обновить контакт
@app.route('/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    data = request.get_json()
    if not data or 'name' not in data or 'phone' not in data:
        return jsonify({'error': 'Необходимо указать name и phone'}), 400
    
    conn = get_db_connection()
    conn.execute('UPDATE contacts SET name = ?, phone = ? WHERE id = ?', 
                 (data['name'], data['phone'], contact_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Контакт обновлён'})

# 5. Удалить контакт
@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Контакт удалён'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)