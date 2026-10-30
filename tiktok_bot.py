import os
import subprocess
import time
import random
import logging
import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

# Setup Logging profesional dengan timestamp
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# Konfigurasi Koneksi PostgreSQL (Mendukung Environment Variables)
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "tiktok_bot"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "your_password"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

# 1. INISIALISASI DATABASE POSTGRESQL
def inisialisasi_database():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
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

# 2. PROSES UTAMA RUNNER BOT
def jalankan_bot_multiprofil():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id, a.nama_profil, a.browser_type, t.url_video 
            FROM tugas_like t 
            JOIN akun a ON t.profil_id = a.id 
            WHERE t.status = 'Pending'
        """)
        tugas_list = cursor.fetchall()
        
        if not tugas_list:
            logging.info("Tidak ada tugas antrean like di database.")
            cursor.close()
            conn.close()
            return

        for index, (tugas_id, nama_profil, browser_type, url_video) in enumerate(tugas_list):
            logging.info(f"[Tugas {tugas_id}] Menggunakan {browser_type.upper()} dengan profil '{nama_profil}' untuk menyukai: {url_video}")
            
            driver = None
            proses_chrome = None
            browser_type = browser_type.lower()
            
            try:
                if browser_type == 'chrome':
                    jalur_chrome = "/usr/bin/google-chrome"
                    if not os.path.exists(jalur_chrome):
                        jalur_chrome = "/usr/bin/chromium"
                    if not os.path.exists(jalur_chrome):
                        jalur_chrome = "/usr/bin/chromium-browser"
                        
                    direktori_data = os.path.abspath(f"./chrome_profiles/{nama_profil}")
                    os.makedirs(direktori_data, exist_ok=True)
                    
                    debug_port = 9222 + index
                    
                    proses_chrome = subprocess.Popen([
                        jalur_chrome,
                        f"--remote-debugging-port={debug_port}",
                        f"--user-data-dir={direktori_data}",
                        "--no-sandbox",
                        "--disable-dev-shm-usage"
                    ])
                    time.sleep(3)
                    
                    chrome_options = ChromeOptions()
                    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
                    
                    service = ChromeService(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)

                elif browser_type == 'firefox':
                    direktori_data = os.path.abspath(f"./firefox_profiles/{nama_profil}")
                    os.makedirs(direktori_data, exist_ok=True)
                    
                    firefox_options = FirefoxOptions()
                    firefox_options.profile = direktori_data
                    
                    service = FirefoxService(GeckoDriverManager().install())
                    driver = webdriver.Firefox(service=service, options=firefox_options)
                else:
                    logging.warning(f"Browser '{browser_type}' tidak didukung.")
                    continue

                # Buka URL video target
                driver.get(url_video)
                
                # Menggunakan Explicit Wait agar lebih handal mendesak elemen
                wait = WebDriverWait(driver, 15)
                tombol_like = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//span[@data-e2e="like-icon"]'))
                )
                
                time.sleep(random.uniform(1.0, 2.0))
                tombol_like.click()
                logging.info("-> Berhasil memberikan Like!")
                
                cursor.execute("UPDATE tugas_like SET status = 'Sukses' WHERE id = %s", (tugas_id,))
                conn.commit()
                
            except Exception as err:
                logging.error(f"-> Gagal menekan tombol / error browser: {err}")
                conn.rollback()
                cursor.execute("UPDATE tugas_like SET status = 'Gagal' WHERE id = %s", (tugas_id,))
                conn.commit()
            
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
                if proses_chrome:
                    try:
                        proses_chrome.terminate()
                    except:
                        pass
                time.sleep(2)
                
        cursor.close()
        conn.close()
        logging.info("Semua tugas di database selesai diproses.")
    except Exception as e:
        logging.error(f"Koneksi/Eksekusi database error: {e}")

if __name__ == "__main__":
    inisialisasi_database()
    jalankan_bot_multiprofil()
