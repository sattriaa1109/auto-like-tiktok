import os
import logging
from src.database import inisialisasi_database, tambah_akun_db, ambil_akun_list, tambah_tugas_db, get_statistik_tugas
from src.bot import jalankan_bot_multiprofil

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

def tambah_akun_menu():
    nama = input("Masukkan nama profil (contoh: akun1): ").strip()
    if not nama:
        print("Nama profil tidak boleh kosong.")
        return
    browser = input("Pilih browser (chrome/firefox) [default: chrome]: ").strip().lower()
    if not browser:
        browser = "chrome"
    proxy = input("Masukkan proxy (format ip:port atau kosongkan): ").strip()
    if not proxy:
        proxy = None
    tambah_akun_db(nama, browser, proxy)

def input_link_menu():
    url = input("Masukkan URL video TikTok: ").strip()
    if not url:
        print("URL tidak boleh kosong.")
        return
        
    akun_list = ambil_akun_list()
    if not akun_list:
        print("Belum ada akun di database. Tambahkan akun terlebih dahulu melalui menu.")
        return
        
    print("\nDaftar Profil Tersedia:")
    for idx, (acc_id, nama, b_type, proxy) in enumerate(akun_list):
        print(f"{idx + 1}. {nama} ({b_type}) - Proxy: {proxy or 'None'}")
        
    pilihan_akun = input("Pilih nomor profil (atau ketik 'all' untuk semua akun): ").strip()
    
    if pilihan_akun.lower() == 'all':
        for acc_id, nama, b_type, proxy in akun_list:
            tambah_tugas_db(acc_id, url)
        print("Semua profil ditambahkan ke antrean tugas.")
    else:
        try:
            idx = int(pilihan_akun) - 1
            if 0 <= idx < len(akun_list):
                acc_id = akun_list[idx][0]
                tambah_tugas_db(acc_id, url)
                print("Tugas berhasil ditambahkan ke database.")
            else:
                print("Pilihan profil tidak valid.")
        except ValueError:
            print("Input tidak valid.")
            
    jalankan = input("Jalankan tugas sekarang? (y/n): ").strip().lower()
    if jalankan == 'y':
        jalankan_bot_multiprofil()

def import_urls_from_file_menu():
    filepath = "urls.txt"
    if not os.path.exists(filepath):
        print(f"File {filepath} tidak ditemukan.")
        return
        
    akun_list = ambil_akun_list()
    if not akun_list:
        print("Belum ada akun di database. Tambahkan akun terlebih dahulu.")
        return
        
    print("\nDaftar Profil Tersedia:")
    for idx, (acc_id, nama, b_type, proxy) in enumerate(akun_list):
        print(f"{idx + 1}. {nama} ({b_type})")
        
    pilihan_akun = input("Pilih nomor profil untuk menerapkan semua URL di `urls.txt` (atau 'all'): ").strip()
    
    target_akun_ids = []
    if pilihan_akun.lower() == 'all':
        target_akun_ids = [acc[0] for acc in akun_list]
    else:
        try:
            idx = int(pilihan_akun) - 1
            if 0 <= idx < len(akun_list):
                target_akun_ids = [akun_list[idx][0]]
            else:
                print("Pilihan tidak valid.")
                return
        except ValueError:
            print("Input tidak valid.")
            return
            
    count = 0
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                for acc_id in target_akun_ids:
                    tambah_tugas_db(acc_id, line)
                    count += 1
                    
    print(f"Berhasil mengimpor {count} tugas dari {filepath}.")
    jalankan = input("Jalankan tugas sekarang? (y/n): ").strip().lower()
    if jalankan == 'y':
        jalankan_bot_multiprofil()

def tampilkan_statistik():
    stats = get_statistik_tugas()
    print("\n--- STATISTIK TUGAS ---")
    if not stats:
        print("Belum ada data tugas.")
    else:
        for status, total in stats.items():
            print(f"- {status}: {total}")
    print("-----------------------")

if __name__ == "__main__":
    inisialisasi_database()
    while True:
        print("\n=== TIKTOK BOT MENU ===")
        print("1. Jalankan semua tugas 'Pending'")
        print("2. Input Link TikTok Manual")
        print("3. Tambah Akun / Profil Baru (Support Proxy)")
        print("4. Import URL Massal dari `urls.txt`")
        print("5. Lihat Statistik Tugas")
        print("6. Keluar")
        
        pilihan = input("Pilih menu (1-6): ").strip()
        
        if pilihan == "1":
            jalankan_bot_multiprofil()
        elif pilihan == "2":
            input_link_menu()
        elif pilihan == "3":
            tambah_akun_menu()
        elif pilihan == "4":
            import_urls_from_file_menu()
        elif pilihan == "5":
            tampilkan_statistik()
        elif pilihan == "6":
            print("Keluar dari program.")
            break
        else:
            print("Pilihan tidak valid, silakan coba lagi.")
