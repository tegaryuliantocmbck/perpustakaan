from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib import messages
from .db import query, execute

KATEGORI = ['Novel', 'Sejarah', 'Pendidikan']
RAK = ['Rak A-01', 'Rak A-02', 'Rak A-03', 'Rak A-04', 'Rak A-05']
STATUS = ['Dipinjam', 'Dikembalikan', 'Terlambat']


# ---------- DASHBOARD ----------
def dashboard(request):
    total_buku = (query("SELECT COALESCE(SUM(stok),0) AS s FROM buku", one=True) or {}).get('s', 0)
    total_judul = (query("SELECT COUNT(*) AS c FROM buku", one=True) or {}).get('c', 0)
    sedang = (query("SELECT COUNT(*) AS c FROM peminjaman WHERE status='Dipinjam'", one=True) or {}).get('c', 0)
    selesai = (query("SELECT COUNT(*) AS c FROM peminjaman WHERE status='Dikembalikan'", one=True) or {}).get('c', 0)
    distribusi = query("SELECT judul, stok FROM buku ORDER BY id")
    max_stok = max([d['stok'] for d in distribusi] + [1])
    for d in distribusi:
        d['pct'] = int(d['stok'] * 100 / max_stok) if max_stok else 0
    total_trx = max(sedang + selesai, 1)
    return render(request, 'perpustakaan/dashboard.html', {
        'total_buku': total_buku, 'total_judul': total_judul,
        'sedang': sedang, 'selesai': selesai,
        'distribusi': distribusi,
        'pct_sedang': int(sedang * 100 / total_trx),
        'pct_selesai': int(selesai * 100 / total_trx),
        'page': 'dashboard',
    })


# ---------- BUKU ----------
def buku_list(request):
    rows = query("SELECT * FROM buku ORDER BY id")
    return render(request, 'perpustakaan/buku_list.html', {'rows': rows, 'page': 'buku'})

def _buku_form_data(request):
    return {
        'judul': request.POST.get('judul', '').strip(),
        'pengarang': request.POST.get('pengarang', '').strip(),
        'kategori': request.POST.get('kategori', '').strip(),
        'penerbit': request.POST.get('penerbit', '').strip(),
        'tahun_terbit': request.POST.get('tahun_terbit', '').strip(),
        'isbn': request.POST.get('isbn', '').strip(),
        'rak': request.POST.get('rak', '').strip(),
        'stok': request.POST.get('stok', '').strip(),
        'deskripsi': request.POST.get('deskripsi', '').strip(),
    }

def _validate_buku(data):
    errs = []
    if not data['judul']: errs.append('Judul wajib diisi')
    if not data['pengarang']: errs.append('Pengarang wajib diisi')
    if data['kategori'] not in KATEGORI: errs.append('Kategori tidak valid')
    if data['rak'] not in RAK: errs.append('Rak tidak valid')
    try:
        data['tahun_terbit'] = int(data['tahun_terbit'])
    except: errs.append('Tahun terbit harus angka')
    try:
        data['stok'] = int(data['stok']); 
        if data['stok'] < 0: errs.append('Stok tidak boleh negatif')
    except: errs.append('Stok harus angka')
    return errs

def buku_create(request):
    if request.method == 'POST':
        data = _buku_form_data(request)
        errs = _validate_buku(data)
        if not errs:
            execute("""INSERT INTO buku(judul,pengarang,kategori,penerbit,tahun_terbit,isbn,rak,stok,deskripsi)
                       VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    [data['judul'], data['pengarang'], data['kategori'], data['penerbit'],
                     data['tahun_terbit'], data['isbn'], data['rak'], data['stok'], data['deskripsi']])
            return redirect('buku_list')
        return render(request, 'perpustakaan/buku_form.html',
                      {'data': data, 'errs': errs, 'kategori': KATEGORI, 'rak': RAK, 'mode': 'create', 'page': 'buku'})
    return render(request, 'perpustakaan/buku_form.html',
                  {'data': {}, 'errs': [], 'kategori': KATEGORI, 'rak': RAK, 'mode': 'create', 'page': 'buku'})

def buku_detail(request, pk):
    row = query("SELECT * FROM buku WHERE id=%s", [pk], one=True)
    if not row: raise Http404
    return render(request, 'perpustakaan/buku_detail.html', {'b': row, 'page': 'buku'})

def buku_edit(request, pk):
    row = query("SELECT * FROM buku WHERE id=%s", [pk], one=True)
    if not row: raise Http404
    if request.method == 'POST':
        data = _buku_form_data(request)
        errs = _validate_buku(data)
        if not errs:
            execute("""UPDATE buku SET judul=%s,pengarang=%s,kategori=%s,penerbit=%s,tahun_terbit=%s,
                       isbn=%s,rak=%s,stok=%s,deskripsi=%s WHERE id=%s""",
                    [data['judul'], data['pengarang'], data['kategori'], data['penerbit'],
                     data['tahun_terbit'], data['isbn'], data['rak'], data['stok'], data['deskripsi'], pk])
            return redirect('buku_list')
        return render(request, 'perpustakaan/buku_form.html',
                      {'data': data, 'errs': errs, 'kategori': KATEGORI, 'rak': RAK, 'mode': 'edit', 'page': 'buku'})
    return render(request, 'perpustakaan/buku_form.html',
                  {'data': row, 'errs': [], 'kategori': KATEGORI, 'rak': RAK, 'mode': 'edit', 'page': 'buku'})

def buku_delete(request, pk):
    row = query("SELECT * FROM buku WHERE id=%s", [pk], one=True)
    if not row: raise Http404
    if request.method == 'POST':
        execute("DELETE FROM buku WHERE id=%s", [pk])
        return redirect('buku_list')
    return render(request, 'perpustakaan/buku_delete.html', {'b': row, 'page': 'buku'})


# ---------- SISWA ----------
def siswa_list(request):
    rows = query("SELECT * FROM siswa ORDER BY id")
    return render(request, 'perpustakaan/siswa_list.html', {'rows': rows, 'page': 'user'})

def _siswa_data(request):
    return {
        'nama': request.POST.get('nama', '').strip(),
        'kelas': request.POST.get('kelas', '').strip(),
        'nis': request.POST.get('nis', '').strip(),
        'is_active': request.POST.get('is_active', 'true') == 'true',
    }

def _validate_siswa(d, pk=None):
    errs = []
    if not d['nama']: errs.append('Nama wajib diisi')
    if not d['kelas']: errs.append('Kelas wajib diisi')
    if not d['nis']: errs.append('NIS wajib diisi')
    else:
        sql = "SELECT id FROM siswa WHERE nis=%s" + (" AND id<>%s" if pk else "")
        params = [d['nis']] + ([pk] if pk else [])
        if query(sql, params): errs.append('NIS sudah dipakai')
    return errs

def siswa_create(request):
    if request.method == 'POST':
        d = _siswa_data(request); errs = _validate_siswa(d)
        if not errs:
            execute("INSERT INTO siswa(nama,kelas,nis,is_active) VALUES(%s,%s,%s,%s)",
                    [d['nama'], d['kelas'], d['nis'], d['is_active']])
            return redirect('siswa_list')
        return render(request, 'perpustakaan/siswa_form.html', {'data': d, 'errs': errs, 'mode': 'create', 'page': 'user'})
    return render(request, 'perpustakaan/siswa_form.html', {'data': {'is_active': True}, 'errs': [], 'mode': 'create', 'page': 'user'})

def siswa_detail(request, pk):
    row = query("SELECT * FROM siswa WHERE id=%s", [pk], one=True)
    if not row: raise Http404
    total = (query("SELECT COUNT(*) c FROM peminjaman WHERE siswa_id=%s", [pk], one=True) or {}).get('c', 0)
    aktif = (query("SELECT COUNT(*) c FROM peminjaman WHERE siswa_id=%s AND status='Dipinjam'", [pk], one=True) or {}).get('c', 0)
    return render(request, 'perpustakaan/siswa_detail.html', {'s': row, 'total': total, 'aktif': aktif, 'page': 'user'})

def siswa_edit(request, pk):
    row = query("SELECT * FROM siswa WHERE id=%s", [pk], one=True)
    if not row: raise Http404
    if request.method == 'POST':
        d = _siswa_data(request); errs = _validate_siswa(d, pk=pk)
        if not errs:
            execute("UPDATE siswa SET nama=%s,kelas=%s,nis=%s,is_active=%s WHERE id=%s",
                    [d['nama'], d['kelas'], d['nis'], d['is_active'], pk])
            return redirect('siswa_list')
        return render(request, 'perpustakaan/siswa_form.html', {'data': d, 'errs': errs, 'mode': 'edit', 'page': 'user'})
    return render(request, 'perpustakaan/siswa_form.html', {'data': row, 'errs': [], 'mode': 'edit', 'page': 'user'})

def siswa_delete(request, pk):
    row = query("SELECT * FROM siswa WHERE id=%s", [pk], one=True)
    if not row: raise Http404
    if request.method == 'POST':
        execute("DELETE FROM siswa WHERE id=%s", [pk])
        return redirect('siswa_list')
    return render(request, 'perpustakaan/siswa_delete.html', {'s': row, 'page': 'user'})


# ---------- PEMINJAMAN ----------
def peminjaman_list(request):
    rows = query("""
        SELECT p.*, s.nama AS siswa_nama, b.judul AS buku_judul
        FROM peminjaman p
        JOIN siswa s ON s.id=p.siswa_id
        JOIN buku b ON b.id=p.buku_id
        ORDER BY p.id
    """)
    return render(request, 'perpustakaan/peminjaman_list.html', {'rows': rows, 'page': 'peminjaman'})

def peminjaman_create(request):
    siswa = query("SELECT * FROM siswa WHERE is_active=TRUE ORDER BY nama")
    buku = query("SELECT * FROM buku WHERE stok>0 ORDER BY judul")
    if request.method == 'POST':
        d = {
            'siswa_id': request.POST.get('siswa_id'),
            'buku_id': request.POST.get('buku_id'),
            'tanggal_pinjam': request.POST.get('tanggal_pinjam'),
            'jatuh_tempo': request.POST.get('jatuh_tempo'),
            'keperluan': request.POST.get('keperluan', '').strip(),
            'petugas': request.POST.get('petugas', 'Budi Siregar').strip(),
        }
        errs = []
        for k in ('siswa_id', 'buku_id', 'tanggal_pinjam', 'jatuh_tempo'):
            if not d[k]: errs.append(f'{k} wajib diisi')
        if not errs:
            execute("""INSERT INTO peminjaman(siswa_id,buku_id,tanggal_pinjam,jatuh_tempo,keperluan,petugas,status)
                       VALUES(%s,%s,%s,%s,%s,%s,'Dipinjam')""",
                    [d['siswa_id'], d['buku_id'], d['tanggal_pinjam'], d['jatuh_tempo'], d['keperluan'], d['petugas']])
            execute("UPDATE buku SET stok=stok-1 WHERE id=%s AND stok>0", [d['buku_id']])
            return redirect('peminjaman_list')
        return render(request, 'perpustakaan/peminjaman_form.html',
                      {'siswa': siswa, 'buku': buku, 'data': d, 'errs': errs, 'page': 'peminjaman'})
    return render(request, 'perpustakaan/peminjaman_form.html',
                  {'siswa': siswa, 'buku': buku, 'data': {}, 'errs': [], 'page': 'peminjaman'})

def peminjaman_return(request, pk):
    row = query("SELECT * FROM peminjaman WHERE id=%s", [pk], one=True)
    if not row: raise Http404
    if row['status'] == 'Dipinjam':
        execute("UPDATE peminjaman SET status='Dikembalikan' WHERE id=%s", [pk])
        execute("UPDATE buku SET stok=stok+1 WHERE id=%s", [row['buku_id']])
    return redirect('peminjaman_list')
