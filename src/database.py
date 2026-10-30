import os
import logging
import psycopg2

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "tiktok_bot"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "your_password"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def inisialisasi_database():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS akun (
                id SERIAL PRIMARY KEY,
                nama_profil VARCHAR(255) UNIQUE NOT NULL,
                browser_type VARCHAR(50) DEFAULT 'chrome'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tugas_like (
                id SERIAL PRIMARY KEY,
                profil_id INTEGER REFERENCES akun(id),
                url_video TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'Pending'
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Database PostgreSQL berhasil diinisialisasi.")
    except Exception as e:
        logging.error(f"Gagal menghubungkan ke PostgreSQL: {e}")

def tambah_akun_db(nama, browser):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO akun (nama_profil, browser_type) VALUES (%s, %s) ON CONFLICT (nama_profil) DO NOTHING", 
            (nama, browser)
        )
        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"Profil '{nama}' ({browser}) berhasil ditambahkan ke database.")
    except Exception as e:
        logging.error(f"Gagal menambah akun: {e}")

def ambil_akun_list():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama_profil, browser_type FROM akun")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        logging.error(f"Gagal mengambil daftar akun: {e}")
        return []

def tambah_tugas_db(profil_id, url):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tugas_like (profil_id, url_video, status) VALUES (%s, %s, 'Pending')", 
            (profil_id, url)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Gagal menambah tugas: {e}")

def get_statistik_tugas():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM tugas_like GROUP BY status")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return dict(result)
    except Exception as e:
        logging.error(f"Gagal mengambil statistik: {e}")
        return {}
