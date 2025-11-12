from flask import Flask, request, render_template, redirect
import os
import psycopg2 
import time

app = Flask(__name__)



DB_HOST = os.environ.get('DB_HOST', 'localhost') 
DB_NAME = os.environ.get('DB_NAME', 'guestbook')
DB_USER = os.environ.get('DB_USER', 'admin')
DB_PASS = os.environ.get('DB_PASS') 


def get_db_connection():
    """Подключается к БД и создает таблицу, если ее нет."""
    conn = None
    
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            break 
        except psycopg2.OperationalError:
            retries -= 1
            time.sleep(2) 

    if conn is None:
        raise Exception("Could not connect to database")

    
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                text VARCHAR(255) NOT NULL
            );
        """)
        conn.commit()
    return conn


@app.route('/')
def index():
    """Отображает главную страницу и список сообщений."""
    messages = []
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT text FROM messages ORDER BY id DESC")
            messages = [row[0] for row in cur.fetchall()]
        conn.close()
    except Exception as e:
        return f"Error connecting to database: {e}"

    
    html = f"""
    <html>
        <head><title>Guestbook</title></head>
        <body style='font-family: sans-serif;'>
            <h2>DevOps Guestbook</h2>
            <h3>DB Host: {DB_HOST}</h3> 
            <form method="POST" action="/add">
                <input type="text" name="message" placeholder="Enter your message">
                <input type="submit" value="Add Message">
            </form>
            <hr>
            <h3>Messages:</h3>
            {"<br>".join(messages) or "No messages yet."}
        </body>
    </html>
    """
    return html


@app.route('/add', methods=['POST'])
def add_message():
    """Добавляет новое сообщение в БД."""
    try:
        message_text = request.form['message']
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO messages (text) VALUES (%s)", (message_text,))
            conn.commit()
        conn.close()
    except Exception as e:
        return f"Error adding message: {e}"

    return redirect('/') 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)