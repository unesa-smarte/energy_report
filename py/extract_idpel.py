import os
import csv
import re
import sys
import time
import pdfplumber

def extract_pln_metadata(pdf_path):
    """Mengekstrak metadata inti dari invoice PLN dengan regex alamat yang diperbaiki."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "".join([page.extract_text() for page in pdf.pages if page.extract_text()])

        if not text:
            return None

        clean_text = " ".join(text.split())

        # 1. ID Pelanggan (12 Digit)
        id_pel = None
        id_pel_match = re.search(r"ID Pelanggan\s*:?\s*(\d+)", clean_text)
        if id_pel_match:
            id_pel = id_pel_match.group(1).strip()
        else:
            fallback_id = re.search(r"\b\d{12}\b", clean_text)
            if fallback_id:
                id_pel = fallback_id.group(0).strip()

        if not id_pel:
            return None

        # 2. Nama Pelanggan
        nama_pel = "KOSONG/GAGAL REGEX"
        nama_match = re.search(
            r"Nama Pelanggan\s*:?\s*(.*?)(?=\s*Alamat Pelanggan|\s*NPWP|\s*Jatuh Tempo|$)", 
            clean_text, re.IGNORECASE
        )
        if nama_match:
            nama_pel = nama_match.group(1).strip().replace(":", "").strip()

        # 3. Alamat Pelanggan (PERBAIKAN: Berhenti tepat sebelum kata Total, Subsidi, Jatuh Tempo, dll)
        alamat_pel = "KOSONG/GAGAL REGEX"
        alamat_match = re.search(
            r"Alamat Pelanggan\s*:?\s*(.*?)(?=\s*Total|\s*Subsidi|\s*Jatuh|\s*NPWP|\s*Tanggal|\s*Golongan|\s*Tarif|$)", 
            clean_text, re.IGNORECASE
        )
        if alamat_match:
            alamat_pel = alamat_match.group(1).strip().replace(":", "").strip()

        # 4. Golongan Tarif
        gol_tarif = "KOSONG/GAGAL REGEX"
        gol_match = re.search(
            r"Golongan Tarif\s*:?\s*([A-Z0-9\s/\.,]+?VA|[A-Z0-9/\.]+)", 
            clean_text, re.IGNORECASE
        )
        if gol_match:
            gol_tarif = gol_match.group(1).strip().replace(":", "").strip()

        return {
            "ID Pelanggan": id_pel,
            "Nama Pelanggan": nama_pel,
            "Alamat Pelanggan": alamat_pel,
            "Golongan Tarif": gol_tarif
        }

    except Exception as e:
        return None

def process_all_folders(master_folder_path, output_csv_path):
    database_pelanggan = {}
    total_scanned = 0
    
    print(f"Memulai pemindaian folder induk: {master_folder_path}")
    print("-" * 65)

    # Karakter animasi spinner
    spinner = ['|', '/', '-', '\\']
    spinner_idx = 0

    # Ambil list semua file PDF terlebih dahulu untuk pelacakan
    pdf_files = []
    for root, dirs, files in os.walk(master_folder_path):
        for file_name in files:
            if file_name.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file_name))

    total_files = len(pdf_files)
    if total_files == 0:
        print("Tidak ada file PDF yang ditemukan di folder tersebut.")
        return

    # Proses file dengan menampilkan animasi teks berjalan di terminal
    for pdf_path in pdf_files:
        total_scanned += 1
        
        # --- Bagian Animasi Spinner & Progress Teks ---
        current_file_name = os.path.basename(pdf_path)
        # Batasi panjang string nama file agar tampilan terminal tetap rapi
        if len(current_file_name) > 30:
            display_name = current_file_name[:27] + "..."
        else:
            display_name = current_file_name.ljust(30)
            
        # Cetak status berputar (\r membuat teks mencetak ulang di baris yang sama)
        sys.stdout.write(f"\r [{spinner[spinner_idx]}] ({total_scanned}/{total_files}) Memproses: {display_name}")
        sys.stdout.flush()
        
        # Update index animasi
        spinner_idx = (spinner_idx + 1) % len(spinner)
        # ----------------------------------------------

        meta = extract_pln_metadata(pdf_path)
        if meta:
            id_pel = meta["ID Pelanggan"]
            if id_pel in database_pelanggan:
                database_pelanggan[id_pel]["kemunculan"] += 1
            else:
                database_pelanggan[id_pel] = {
                    "Nama Pelanggan": meta["Nama Pelanggan"],
                    "Alamat Pelanggan": meta["Alamat Pelanggan"],
                    "Golongan Tarif": meta["Golongan Tarif"],
                    "kemunculan": 1
                }

    # Hapus baris loading terakhir setelah selesai
    sys.stdout.write("\r" + " " * 75 + "\r")
    sys.stdout.flush()

    # Tulis hasil akhir ke CSV
    fieldnames = ["ID Pelanggan", "Nama Pelanggan", "Alamat Pelanggan", "Golongan Tarif", "kemunculan"]
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for id_pel, data in database_pelanggan.items():
            writer.writerow({
                "ID Pelanggan": id_pel,
                "Nama Pelanggan": data["Nama Pelanggan"],
                "Alamat Pelanggan": data["Alamat Pelanggan"],
                "Golongan Tarif": data["Golongan Tarif"],
                "kemunculan": data["kemunculan"]
            })

    print("-" * 65)
    print(f"✨ PROSES SELESAI SUKSES!")
    print(f" 📂 Total PDF Sukses Di-scan : {total_scanned} file")
    print(f" 👥 Total ID Unik Ditemukan : {len(database_pelanggan)} pelanggan")
    print(f" 📄 Hasil CSV Disimpan Ke   : {output_csv_path}")
    print("-" * 65)

if __name__ == "__main__":
    FOLDER_INDUK = r"E:\nyo\py_lora\tagihan2"
    CSV_OUTPUT = r"E:\nyo\py_lora\tagihan2\rekap_data_pelanggan.csv"
    
    process_all_folders(FOLDER_INDUK, CSV_OUTPUT)