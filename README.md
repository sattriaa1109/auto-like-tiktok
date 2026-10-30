# Auto Like TikTok Bot (Linux, PostgreSQL & FastAPI)

Bot otomatis untuk memberikan Like pada video TikTok menggunakan Selenium WebDriver, PostgreSQL, dan REST API berbasis FastAPI.

## Struktur Folder
```text
.
├── src/
│   ├── __init__.py
│   ├── database.py
│   ├── bot.py
│   └── api.py
├── main.py
├── requirements.txt
└── README.md
```

## Instalasi
1. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
2. Jalankan CLI Interaktif:
   ```bash
   python3 main.py
   ```
3. Atau Jalankan FastAPI Server:
   ```bash
   uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
   ```
   Dokumentasi API interaktif dapat diakses di: `http://localhost:8000/docs`
