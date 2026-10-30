import logging
from src.database import inisialisasi_database, tambah_akun_db, ambil_akun_list, tambah_tugas_db
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
    tambah_akun_db(nama, browser)

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
    for idx, (acc_id, nama, b_type) in enumerate(akun_list):
        print(f"{idx + 1}. {nama} ({b_type})")
        
    pilihan_akun = input("Pilih nomor profil (atau ketik 'all' untuk semua akun): ").strip()
    
    if pilihan_akun.lower() == 'all':
        for acc_id, nama, b_type in akun_list:
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

if __name__ == "__main__":
    inisialisasi_database()
    while True:
        print("\n=== TIKTOK BOT MENU ===")
        print("1. Jalankan semua tugas 'Pending' dari Database")
        print("2. Input Link TikTok Manual & Pilih Profil")
        print("3. Tambah Akun / Profil Baru")
        print("4. Keluar")
        
        pilihan = input("Pilih menu (1-4): ").strip()
        
        if pilihan == "1":
            jalankan_bot_multiprofil()
        elif pilihan == "2":
            input_link_menu()
        elif pilihan == "3":
            tambah_akun_menu()
        elif pilihan == "4":
            print("Keluar dari program.")
            break
        else:
            print("Pilihan tidak valid, silakan coba lagi.")
