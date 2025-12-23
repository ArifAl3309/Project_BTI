import json
import os
import textwrap  # untuk membungkus teks panjang (wrap) agar turun ke baris bawah

FILE = "tugas.json"  # nama file penyimpanan (persisten)

# ================== KONFIGURASI TAMPILAN (LEBAR KOLOM) ==================
# Atur lebar kolom agar tabel rapi. Ubah angka jika butuh.
COL_MAPEL = 18
COL_DESKRIPSI = 32  # lebar kolom deskripsi; teks lebih panjang akan di-wrap
COL_DEADLINE = 18

# Perkiraan total lebar baris, dipakai untuk menggambar garis pembatas yang panjang
TOTAL_WIDTH = 6 + COL_MAPEL + 1 + COL_DESKRIPSI + 1 + COL_DEADLINE + 7

# ================== UTILITAS TAMPILAN ==================
#Mempercantik Tampilan Output pada terminal
def garis():
    """Cetak garis pembatas sepanjang lebar tampilan (min 80)."""
    print("=" * max(80, TOTAL_WIDTH))

def icon(done: bool) -> str:
    """Ubah status boolean menjadi ikon (✅ selesai / ⏳ belum)."""
    return "✅" if done else "⏳"

def header_judul(teks: str):
    """Header seksi (judul besar di tengah + garis atas/bawah)."""
    garis()
    print(f"{teks:^{max(80, TOTAL_WIDTH)}}")
    garis()

# ================== FILE PERSISTENSI ==================
def _normalize_item(t: dict) -> dict: #Menyamakan Format Input Data
    """
    Normalisasi item tugas agar schema selalu konsisten.
    - Kompatibilitas data lama: jika ada 'judul', dianggap sebagai 'mapel'.
    - Pastikan semua kunci ada: mapel, deskripsi, deadline, done.
    """
    mapel = t.get("mapel", t.get("judul", "-"))
    deskripsi = t.get("deskripsi", "-")
    deadline = t.get("deadline", "-")
    done = bool(t.get("done", False))
    return {"mapel": mapel, "deskripsi": deskripsi, "deadline": deadline, "done": done}

def muat() -> list: #Fungsi saat Program dijalankan
    """
    Muat data dari FILE jika ada.
    - Mengembalikan list tugas.
    - Menormalkan setiap item agar tidak ada KeyError saat ditampilkan.
    """
    if os.path.exists(FILE):
        try:
            with open(FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return [_normalize_item(x) for x in data if isinstance(x, dict)]
        except Exception:
            # Kalau ada error saat membaca file, anggap data kosong (fail-safe).
            pass
    return []

def simpan(tugas: list): #Perubahan Data
    """Simpan list tugas ke FILE dalam format JSON (indented agar mudah dibaca)."""
    try:
        with open(FILE, "w", encoding="utf-8") as f:
            json.dump(tugas, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[!] Gagal menyimpan data: {e}")

# ================== INPUT & VALIDASI ==================
def input_non_kosong(prompt: str) -> str: #INPUT NON KOSONG
    """
    Meminta input user hingga tidak kosong (biar data wajib terisi).
    Dipakai untuk Mapel, Deskripsi, dan Deadline.
    """
    while True:
        v = input(prompt).strip()
        if v:
            return v
        print("[!] Field ini wajib diisi.")

def baca_indeks(tugas: list, label: str) -> int: #Memilih nomor tugas yang valid
    """
    Meminta nomor indeks tugas yang valid dari user.
    - Mengembalikan indeks berbasis 0
    - Jika invalid, mengembalikan -1 (caller memutuskan lanjut atau tidak)
    """
    if not tugas:
        print("[!] Tidak ada tugas.")
        return -1
    try:
        idx = int(input(f"Masukkan nomor tugas yang ingin {label}: ").strip())
        if 1 <= idx <= len(tugas):
            return idx - 1  # konversi nomor (1..N) menjadi indeks (0..N-1)
        print(f"[!] Nomor harus antara 1 dan {len(tugas)}")
        return -1
    except ValueError:
        print("[!] Masukkan angka yang valid.")
        return -1

# ================== FITUR INTI ==================
def tampilkan_menu():
    """Tampilkan menu utama yang selalu muncul di setiap loop."""
    garis()
    print("📘  MENU UTAMA TO-DO LIST")
    garis()
    print("1) Tambah Tugas Baru")
    print("2) Lihat Semua Tugas")
    print("3) Tandai Selesai")
    print("4) Hapus Tugas")
    print("5) Lihat Tugas Selesai")
    print("6) Lihat Tugas Belum Selesai")
    print("7) Keluar")
    garis()

def tambah_tugas(tugas: list):
    """
    Tambahkan entry tugas baru:
    - Mapel, Deskripsi, Deadline (semua wajib diisi)
    - Status awal: done=False (belum selesai)
    """
    header_judul("Tambah Tugas Baru")
    mapel = input_non_kosong("Mata Pelajaran : ")
    deskripsi = input_non_kosong("Deskripsi Singkat tugas : ")
    deadline = input_non_kosong("Deadline (DD-MM-YYYY) : ")
    tugas.append({
        "mapel": mapel,
        "deskripsi": deskripsi,
        "deadline": deadline,
        "done": False
    })
    simpan(tugas)
    print("\n[OK] Tugas berhasil ditambahkan!\n")

def _wrap(text: str, width: int) -> list[str]:
    """
    Membungkus teks panjang menjadi beberapa baris dengan lebar 'width'.
    - break_long_words=True agar kata sangat panjang tetap terpotong rapi
    - replace_whitespace=False agar spasi asli tetap dipertahankan
    """
    lines = textwrap.wrap(text or "-", width=width, break_long_words=True, replace_whitespace=False)
    return lines or ["-"]

def lihat_tugas(tugas: list, hanya_done: bool | None = None):
    """
    Menampilkan daftar tugas dalam format tabel:
    - Auto-wrap kolom Deskripsi (dan Mapel jika kepanjangan).
    - Filter:
        hanya_done = True  -> tampilkan hanya yang selesai
        hanya_done = False -> tampilkan hanya yang belum selesai
        None               -> tampilkan semua
    """
    header_judul("Daftar Tugas")
    if not tugas:
        print("(Belum ada tugas yang tersimpan.)\n")
        return

    # Header tabel dengan lebar kolom yang telah dikonfigurasi
    print(
        f"{'No':<4} {'St':<2}  "
        f"{'Mata Pelajaran':<{COL_MAPEL}}  "
        f"{'Deskripsi':<{COL_DESKRIPSI}}  "
        f"{'Deadline':<{COL_DEADLINE}}"
    )
    print("-" * max(80, TOTAL_WIDTH))

    ada = False
    for i, t in enumerate(tugas, start=1):
        done = t.get("done", False)
        # Terapkan filter berdasarkan status selesai / belum
        if (hanya_done is True and not done) or (hanya_done is False and done):
            continue

        mapel = t.get("mapel", "-")
        deskripsi = t.get("deskripsi", "-")
        deadline = t.get("deadline", "-")

        # Bungkus teks agar tidak menabrak kolom lain
        desc_lines = _wrap(deskripsi, COL_DESKRIPSI)
        mapel_lines = _wrap(mapel, COL_MAPEL)

        # Tentukan berapa baris yang perlu dicetak untuk item ini
        rows = max(len(desc_lines), len(mapel_lines))

        # Cetak baris pertama + baris lanjutan (jika ada)
        for r in range(rows):
            # Kolom 'No' dan 'St' hanya muncul di baris pertama
            no_str = f"{i:<4}" if r == 0 else " " * 4
            st_str = f"{icon(done):<2}" if r == 0 else " " * 2

            # Ambil potongan baris sesuai indeks r (jika tidak ada, pakai string kosong)
            mapel_str = mapel_lines[r] if r < len(mapel_lines) else ""
            desc_str = desc_lines[r] if r < len(desc_lines) else ""
            # Kolom deadline hanya ditampilkan di baris pertama untuk menghemat ruang
            dead_str = deadline if r == 0 else ""

            print(
                f"{no_str} {st_str}  "
                f"{mapel_str:<{COL_MAPEL}}  "
                f"{desc_str:<{COL_DESKRIPSI}}  "
                f"{dead_str:<{COL_DEADLINE}}"
            )

        ada = True

    if not ada:
        # Pesan jika filter menghasilkan daftar kosong
        if hanya_done is True:
            print("(Belum ada tugas yang selesai.)")
        elif hanya_done is False:
            print("(Semua tugas sudah selesai!)")
    garis()
    print()

def tandai_selesai(tugas: list):
    """Ubah status 'done' menjadi True untuk item yang dipilih user."""
    header_judul("Tandai Tugas Selesai")
    lihat_tugas(tugas, hanya_done=False)  # tampilkan yang belum selesai saja
    idx = baca_indeks(tugas, "ditandai selesai")
    if idx == -1:
        return
    if tugas[idx]["done"]:
        print("[i] Tugas ini sudah selesai.\n")
        return
    tugas[idx]["done"] = True
    simpan(tugas)
    print(f"[OK] Tugas '{tugas[idx]['deskripsi']}' ditandai selesai ✅\n")

def hapus_tugas(tugas: list):
    """Hapus item tugas berdasarkan nomor yang dipilih user (dengan konfirmasi)."""
    header_judul("Hapus Tugas")
    lihat_tugas(tugas)
    idx = baca_indeks(tugas, "dihapus")
    if idx == -1:
        return
    judul = tugas[idx]["deskripsi"]
    konfirmasi = input(f"Yakin ingin menghapus '{judul}'? (y/n): ").strip().lower()
    if konfirmasi == "y":
        tugas.pop(idx)
        simpan(tugas)
        print("[OK] Tugas berhasil dihapus.\n")
    else:
        print("[i] Dibatalkan.\n")

# ================== MAIN LOOP ==================
def main():
    """Loop utama: tampilkan menu, baca pilihan, jalankan fitur sampai user keluar."""
    tugas = muat()  # load data dari file JSON (kalau ada)
    print("👋 Selamat datang di To-Do List Console!\n")
    while True:
        tampilkan_menu()
        pilih = input("Pilih menu (1-7): ").strip()
        print()  # spasi supaya output tidak dempet
        if pilih == "1":
            tambah_tugas(tugas)
        elif pilih == "2":  
            lihat_tugas(tugas)
        elif pilih == "3":
            tandai_selesai(tugas)
        elif pilih == "4":
            hapus_tugas(tugas)
        elif pilih == "5":
            lihat_tugas(tugas, hanya_done=True)
        elif pilih == "6":
            lihat_tugas(tugas, hanya_done=False)
        elif pilih == "7":
            print("Terima kasih telah menggunakan To-Do List Console! 👋")
            break
        else:
            print("[!] Pilihan tidak dikenal. Masukkan angka 1-7.\n")

if __name__ == "__main__": #Entry Point
    main()