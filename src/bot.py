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

def inisialisasi_driver(browser_type, nama_profil, proxy=None, is_headless=False, debug_port=9222):
    """Membuat dan mengonfigurasi driver browser berdasarkan tipe dan profil."""
    browser_type = browser_type.lower()
    driver = None
    proses_chrome = None

    if browser_type == 'chrome':
        jalur_chrome = "/usr/bin/google-chrome"
        if not os.path.exists(jalur_chrome):
            jalur_chrome = "/usr/bin/chromium"
        if not os.path.exists(jalur_chrome):
            jalur_chrome = "/usr/bin/chromium-browser"

        direktori_data = os.path.abspath(f"./chrome_profiles/{nama_profil}")
        os.makedirs(direktori_data, exist_ok=True)

        chrome_args = [
            jalur_chrome,
            f"--remote-debugging-port={debug_port}",
            f"--user-data-dir={direktori_data}",
            "--no-sandbox",
            "--disable-dev-shm-usage"
        ]

        if proxy:
            chrome_args.append(f"--proxy-server={proxy}")
        if is_headless:
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
        firefox_options.add_argument("-profile")
        firefox_options.add_argument(direktori_data)

        if is_headless:
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
        raise ValueError(f"Browser '{browser_type}' tidak didukung.")

    return driver, proses_chrome

def cek_status_login(driver):
    """Mengecek apakah sesi browser saat ini sudah login ke TikTok."""
    try:
        cookies = driver.get_cookies()
        if any(c.get("name") == "sessionid" for c in cookies):
            return True
        profile_icon = driver.find_elements(By.XPATH, '//*[@data-e2e="profile-icon"]')
        if profile_icon:
            return True
    except Exception:
        pass
    return False

def buka_browser_login(nama_profil, browser_type="firefox", proxy=None):
    """Membuka browser profil secara interaktif agar pengguna dapat login manual."""
    print(f"\n[INFO] Membuka browser {browser_type.upper()} untuk profil '{nama_profil}'...")
    driver = None
    proses_chrome = None
    try:
        driver, proses_chrome = inisialisasi_driver(
            browser_type=browser_type,
            nama_profil=nama_profil,
            proxy=proxy,
            is_headless=False
        )
        driver.get("https://www.tiktok.com/login")
        print("\n" + "=" * 60)
        print(f" Jendela browser profil '{nama_profil}' telah terbuka di layar.")
        print(" Silakan lakukan login ke akun TikTok Anda.")
        print(" (Bisa scan QR Code via aplikasi TikTok di HP, email, Google, dll.)")
        print(" Setelah profil TikTok Anda berhasil masuk dan tampil di halaman:")
        input(" -> Tekan [ENTER] di terminal ini untuk menyimpan sesi & keluar...\n" + "=" * 60 + "\n")

        time.sleep(2)
        if cek_status_login(driver):
            print(f"[SUKSES] Sesi login untuk profil '{nama_profil}' berhasil terdeteksi dan tersimpan!")
        else:
            print(f"[PERINGATAN] Sesi login belum terdeteksi. Namun cookie tetap tersimpan di folder profil.")
    except Exception as e:
        print(f"[ERROR] Gagal membuka browser login: {e}")
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

def jalankan_bot_multiprofil():
    conn = None
    cursor = None
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
            return

        for index, (tugas_id, nama_profil, browser_type, proxy, url_video) in enumerate(tugas_list):
            logging.info(f"[Tugas {tugas_id}] Menggunakan {browser_type.upper()} | Profil: '{nama_profil}' | Proxy: {proxy or 'None'} | URL: {url_video}")

            driver = None
            proses_chrome = None
            browser_type = browser_type.lower()

            try:
                debug_port = 9222 + index
                driver, proses_chrome = inisialisasi_driver(
                    browser_type=browser_type,
                    nama_profil=nama_profil,
                    proxy=proxy,
                    is_headless=IS_HEADLESS,
                    debug_port=debug_port
                )

                # Buka URL video target
                driver.get(url_video)

                # Human-like behavior: Jeda acak & Scroll halaman ke bawah sedikit
                time.sleep(random.uniform(3.0, 5.0))
                try:
                    driver.execute_script("window.scrollBy(0, 300);")
                except:
                    pass
                time.sleep(random.uniform(1.5, 2.5))

                # Periksa apakah profil sudah login
                if not cek_status_login(driver):
                    logging.warning(f"-> [PERINGATAN] Profil '{nama_profil}' BELUM LOGIN ke TikTok! Sesi login tidak ditemukan.")

                # Coba tutup pop-up tutorial / dialog 'Got it' jika ada
                try:
                    tombol_got_it = driver.find_elements(By.XPATH, "//button[contains(., 'Got it') or contains(., 'Mengerti')]")
                    if tombol_got_it:
                        tombol_got_it[0].click()
                        time.sleep(1)
                except Exception:
                    pass

                # Explicit Wait untuk tombol like
                wait = WebDriverWait(driver, 15)
                tombol_like = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@data-e2e="like-icon"]'))
                )

                try:
                    tombol_like.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", tombol_like)

                logging.info("-> Berhasil memberikan Like (Human-like action applied)!")
                time.sleep(2)
                try:
                    driver.save_screenshot("tiktok_after_like.png")
                except:
                    pass

                cursor.execute("UPDATE tugas_like SET status = 'Sukses' WHERE id = %s", (tugas_id,))
                conn.commit()

            except Exception as err:
                logging.error(f"-> Gagal menekan tombol / error browser: {err}")
                if driver:
                    try:
                        driver.save_screenshot("tiktok_debug.png")
                    except:
                        pass
                if conn:
                    try:
                        conn.rollback()
                    except:
                        pass
                cursor.execute("UPDATE tugas_like SET status = 'Gagal' WHERE id = %s", (tugas_id,))
                if conn:
                    try:
                        conn.commit()
                    except:
                        pass

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

        logging.info("Semua tugas di database selesai diproses.")
    except Exception as e:
        logging.error(f"Koneksi/Eksekusi database error: {e}")
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass
