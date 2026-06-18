from django.db import migrations

SQL = """
CREATE TABLE IF NOT EXISTS buku (
    id SERIAL PRIMARY KEY,
    judul VARCHAR(200) NOT NULL,
    pengarang VARCHAR(150) NOT NULL,
    kategori VARCHAR(50) NOT NULL,
    penerbit VARCHAR(150) NOT NULL,
    tahun_terbit INTEGER NOT NULL,
    isbn VARCHAR(40) DEFAULT '',
    rak VARCHAR(20) NOT NULL,
    stok INTEGER NOT NULL DEFAULT 0,
    deskripsi TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS siswa (
    id SERIAL PRIMARY KEY,
    nama VARCHAR(150) NOT NULL,
    kelas VARCHAR(50) NOT NULL,
    nis VARCHAR(30) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE IF NOT EXISTS peminjaman (
    id SERIAL PRIMARY KEY,
    siswa_id INTEGER NOT NULL REFERENCES siswa(id) ON DELETE CASCADE,
    buku_id INTEGER NOT NULL REFERENCES buku(id) ON DELETE CASCADE,
    tanggal_pinjam DATE NOT NULL,
    jatuh_tempo DATE NOT NULL,
    keperluan TEXT DEFAULT '',
    petugas VARCHAR(100) DEFAULT 'Budi Siregar',
    status VARCHAR(20) NOT NULL DEFAULT 'Dipinjam'
);
"""

REVERSE = """
DROP TABLE IF EXISTS peminjaman;
DROP TABLE IF EXISTS siswa;
DROP TABLE IF EXISTS buku;
"""

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.RunSQL(SQL, REVERSE)]
