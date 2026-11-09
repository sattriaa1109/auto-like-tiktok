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
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS akun (
                id SERIAL PRIMARY KEY,
                nama_profil VARCHAR(255) UNIQUE NOT NULL,
                browser_type VARCHAR(50) DEFAULT 'chrome',
                proxy VARCHAR(255) DEFAULT NULL
            )
        ''')
        
        cursor.execute('''
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='akun' AND column_name='proxy') THEN
                    ALTER TABLE akun ADD COLUMN proxy VARCHAR(255) DEFAULT NULL;
                END IF;
            END $$;
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
        logging.info("Database PostgreSQL berhasil diinisialisasi.")
    except Exception as e:
        logging.error(f"Gagal menghubungkan ke PostgreSQL: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def tambah_akun_db(nama, browser, proxy=None):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO akun (nama_profil, browser_type, proxy) VALUES (%s, %s, %s) ON CONFLICT (nama_profil) DO UPDATE SET browser_type = EXCLUDED.browser_type, proxy = EXCLUDED.proxy", 
            (nama, browser, proxy)
        )
        conn.commit()
        logging.info(f"Profil '{nama}' ({browser}, proxy: {proxy}) berhasil disimpan ke database.")
    except Exception as e:
        logging.error(f"Gagal menambah akun: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def ambil_akun_list():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama_profil, browser_type, proxy FROM akun")
        result = cursor.fetchall()
        return result
    except Exception as e:
        logging.error(f"Gagal mengambil daftar akun: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def tambah_tugas_db(profil_id, url):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tugas_like (profil_id, url_video, status) VALUES (%s, %s, 'Pending')", 
            (profil_id, url)
        )
        conn.commit()
    except Exception as e:
        logging.error(f"Gagal menambah tugas: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_statistik_tugas():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM tugas_like GROUP BY status")
        result = cursor.fetchall()
        return dict(result)
    except Exception as e:
        logging.error(f"Gagal mengambil statistik: {e}")
        return {}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
