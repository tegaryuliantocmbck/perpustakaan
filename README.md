# SIPUSTAKA — Sistem Peminjaman Buku (Django + PostgreSQL + Raw SQL)

Aplikasi perpustakaan sederhana untuk Tugas Akhir CRUD Django.

## Fitur
- Dashboard counter (Total Buku, Total Judul, Sedang Dipinjam, Sudah Dikembalikan) + grafik distribusi stok.
- CRUD **Buku** (judul, pengarang, kategori [dropdown], penerbit, tahun, ISBN, rak [dropdown], stok, deskripsi).
- CRUD **User / Siswa** (nama, kelas, NIS unik, status aktif).
- **Peminjaman** (form dropdown siswa & buku, tanggal pinjam, jatuh tempo, keperluan, petugas) + tombol **Kembalikan**.
- Semua query memakai **Raw SQL** lewat `connection.cursor()`.
- Foreign Key `peminjaman → siswa`, `peminjaman → buku` (tabel penghubung many-to-many).
- UI rapi memakai CSS custom (tanpa framework eksternal yang berat).

## Cara Menjalankan

```bash
pip install -r requirements.txt
```

### 1) Pakai PostgreSQL (sesuai instruksi tugas)
Buat database lebih dulu:
```sql
CREATE DATABASE sipustaka_db;
```
Atur kredensial via environment variable (opsional):
```
DB_NAME=sipustaka_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5432
```
Lalu:
```bash
python manage.py migrate
python manage.py runserver
```

### 2) Mode cepat tanpa PostgreSQL (SQLite)
```bash
USE_SQLITE=1 python manage.py migrate
USE_SQLITE=1 python manage.py runserver
```

Buka: http://127.0.0.1:8000/

## Struktur Database (Raw SQL — migrasi `0001_initial.py`)
- `buku(id, judul, pengarang, kategori, penerbit, tahun_terbit, isbn, rak, stok, deskripsi)`
- `siswa(id, nama, kelas, nis UNIQUE, is_active)`
- `peminjaman(id, siswa_id FK, buku_id FK, tanggal_pinjam, jatuh_tempo, keperluan, petugas, status)`

## Catatan
- Admin/Petugas default: **Budi Siregar**.
- Saat peminjaman dibuat, stok buku otomatis berkurang. Saat dikembalikan, stok ditambah kembali.
