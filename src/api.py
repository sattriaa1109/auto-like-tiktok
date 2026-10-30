from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.database import inisialisasi_database, tambah_akun_db, ambil_akun_list, tambah_tugas_db, get_statistik_tugas
from src.bot import jalankan_bot_multiprofil

app = FastAPI(title="TikTok Bot API", version="1.1.0")

@app.on_event("startup")
def startup_event():
    inisialisasi_database()

class AccountCreate(BaseModel):
    nama_profil: str
    browser_type: Optional[str] = "chrome"
    proxy: Optional[str] = None

class TaskCreate(BaseModel):
    url_video: str
    profil_id: Optional[int] = None

@app.post("/accounts", summary="Tambah Akun / Profil Baru (Support Proxy)")
def create_account(account: AccountCreate):
    tambah_akun_db(account.nama_profil, account.browser_type, account.proxy)
    return {
        "status": "success", 
        "message": f"Profil '{account.nama_profil}' ({account.browser_type}) dengan proxy '{account.proxy}' berhasil ditambahkan."
    }

@app.get("/accounts", summary="Daftar Akun")
def list_accounts():
    accounts = ambil_akun_list()
    return [{"id": acc[0], "nama_profil": acc[1], "browser_type": acc[2], "proxy": acc[3]} for acc in accounts]

@app.post("/tasks", summary="Input Link TikTok dan Tambah ke Antrean")
def create_task(task: TaskCreate):
    accounts = ambil_akun_list()
    if not accounts:
        raise HTTPException(status_code=400, detail="Belum ada akun terdaftar.")
    
    added_count = 0
    if task.profil_id:
        valid_ids = [acc[0] for acc in accounts]
        if task.profil_id not in valid_ids:
            raise HTTPException(status_code=404, detail="Profil ID tidak ditemukan.")
        tambah_tugas_db(task.profil_id, task.url_video)
        added_count = 1
    else:
        for acc in accounts:
            tambah_tugas_db(acc[0], task.url_video)
            added_count += 1
            
    return {
        "status": "success",
        "message": f"Berhasil menambahkan {added_count} tugas ke database.",
        "url_video": task.url_video
    }

@app.post("/tasks/run", summary="Jalankan Bot Antrean Pending (Mendukung Headless & Proxy)")
def run_bot_task():
    try:
        jalankan_bot_multiprofil()
        return {"status": "success", "message": "Eksekusi bot selesai."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", summary="Statistik Tugas")
def get_stats():
    stats = get_statistik_tugas()
    return {"status": "success", "statistics": stats}
