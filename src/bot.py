import os
import subprocess
import time
import random
import logging
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
from src.database import get_connection

IS_HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

def jalankan_bot_multiprofil():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id, a.nama_profil, a.browser_type, a.proxy, t.url_video 
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

        for index, (tugas_id, nama_profil, browser_type, proxy, url_video) in enumerate(tugas_list):
            logging.info(f"[Tugas {tugas_id}] Menggunakan {browser_type.upper()} | Profil: '{nama_profil}' | Proxy: {proxy or 'None'} | URL: {url_video}")
            
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
                    
                    chrome_args = [
                        jalur_chrome,
                        f"--remote-debugging-port={debug_port}",
                        f"--user-data-dir={direktori_data}",
                        "--no-sandbox",
                        "--disable-dev-shm-usage"
                    ]
                    
                    if proxy:
                        chrome_args.append(f"--proxy-server={proxy}")
                    if IS_HEADLESS:
                        chrome_args.append("--headless=new")
                        
                    proses_chrome = subprocess.Popen(chrome_args)
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
                    
                    if IS_HEADLESS:
                        firefox_options.add_argument("-headless")
                        
                    if proxy and ":" in proxy:
                        ip, port = proxy.split(":")
                        firefox_options.set_preference("network.proxy.type", 1)
                        firefox_options.set_preference("network.proxy.http", ip)
                        firefox_options.set_preference("network.proxy.http_port", int(port))
                        firefox_options.set_preference("network.proxy.ssl", ip)
                        firefox_options.set_preference("network.proxy.ssl_port", int(port))
                            
                    service = FirefoxService(GeckoDriverManager().install())
                    driver = webdriver.Firefox(service=service, options=firefox_options)
                else:
                    logging.warning(f"Browser '{browser_type}' tidak didukung.")
                    continue

                # Buka URL video target
                driver.get(url_video)
                
                # Human-like behavior: Jeda acak & Scroll halaman ke bawah sedikit
                time.sleep(random.uniform(3.0, 5.0))
                try:
                    driver.execute_script("window.scrollBy(0, 300);")
                except:
                    pass
                time.sleep(random.uniform(1.5, 2.5))
                
                # Explicit Wait untuk tombol like
                wait = WebDriverWait(driver, 15)
                tombol_like = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//span[@data-e2e="like-icon"]'))
                )
                
                tombol_like.click()
                logging.info("-> Berhasil memberikan Like (Human-like action applied)!")
                
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
