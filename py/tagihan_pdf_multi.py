import os
import json
import re
import pdfplumber


def clean_to_number(text_value, is_float=False):
    """Mengubah teks angka berformat (koma/titik) menjadi int atau float murni."""
    if not text_value:
        return 0 if not is_float else 0.0
    clean = re.sub(r"[^\d\.,]", "", text_value)

    if is_float:
        if "," in clean and "." in clean:
            clean = clean.replace(",", "")
        elif "," in clean and "." not in clean:
            clean = clean.replace(",", ".")
        try:
            return float(clean)
        except ValueError:
            return 0.0
    else:
        clean = clean.replace(".", "").replace(",", "")
        try:
            return int(clean)
        except ValueError:
            return 0


def extract_pln_data(pdf_path):
    """Mengekstrak data tagihan PLN menggunakan pdfplumber."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "".join([page.extract_text() for page in pdf.pages if page.extract_text()])

        if not text:
            return None

        clean_text = " ".join(text.split())

        # 1. ID Pelanggan
        id_pel = None
        id_pel_match = re.search(r"ID Pelanggan\s*:?\s*(\d+)", clean_text)
        if id_pel_match:
            id_pel = id_pel_match.group(1).strip()
        else:
            id_pel_match = re.search(r"\b\d{12}\b", clean_text)
            if id_pel_match:
                id_pel = id_pel_match.group(0).strip()

        # 2. Nama Pelanggan
        nama_pel = None
        nama_match = re.search(
            r"Nama Pelanggan\s*:?\s*(.*?)(?=\s*Alamat Pelanggan|\s*\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember|Jan|Feb|Mar|Apr|Mei|Jun|Jul|Agt|Sep|Okt|Nov|Des)|\s*Jatuh Tempo|\s*Total|$)",
            clean_text, re.IGNORECASE)
        if nama_match:
            nama_pel = nama_match.group(1).strip().replace(":", "").strip()

        # 3. Ekstraksi Golongan & Tarif
        gol_clean = None
        tarif_clean = None
        gol_tarif_match = re.search(r"Golongan Tarif\s*:?\s*([A-Z0-9\s/\.,]+?VA|[A-Z0-9/\.]+)", clean_text,
                                    re.IGNORECASE)

        gol_raw = None
        if gol_tarif_match:
            gol_raw = gol_tarif_match.group(1).strip()
        else:
            fallback_gol = re.search(r"\b([S|R|B|I|P|M][0-9xX]?\s*/\s*[\d\.,]+\s*VA)\b", clean_text, re.IGNORECASE)
            if fallback_gol:
                gol_raw = fallback_gol.group(0).strip()

        if gol_raw and "/" in gol_raw:
            parts = gol_raw.split("/")
            gol_clean = parts[0].strip()
            digits = re.sub(r"[^\d]", "", parts[1])
            if digits:
                tarif_clean = f"{digits}VA"
        elif gol_raw:
            gol_clean = gol_raw

        # 4. Ambil teks mentah untuk data nominal angka
        total_match = re.search(r"Total Tagihan\s*(?:\*\*|\*)?\s*Rp\s*([\d\.,]+)", clean_text)
        kwh_lwbp_match = re.search(r"kWh LWBP\s*:\s*([\d,]+)", clean_text)
        tarif_lwbp_match = re.search(r"Tarif LWBP\s*:\s*Rp\s*([\d,]+\.?\d*)", clean_text)
        kwh_wbp_match = re.search(r"kWh WBP\s*:\s*([\d,]+)", clean_text)
        tarif_wbp_match = re.search(r"Tarif WBP\s*:\s*Rp\s*([\d,]+\.?\d*)", clean_text)
        kwh_kvarh_match = re.search(r"kVArh\s*:\s*([\d,]+)", clean_text)
        tarif_kvarh_match = re.search(r"Tarif kVArh\s*:\s*Rp\s*([\d,]+\.?\d*)", clean_text)

        data = {
            "File Name": os.path.basename(pdf_path),
            "ID Pelanggan": id_pel,
            "Nama Pelanggan": nama_pel,
            "Gol": gol_clean,
            "Tarif": tarif_clean,
            "Total Tagihan": clean_to_number(total_match.group(1) if total_match else None, is_float=False),
            "kWh LWBP": clean_to_number(kwh_lwbp_match.group(1) if kwh_lwbp_match else None, is_float=False),
            "Tarif LWBP": clean_to_number(tarif_lwbp_match.group(1) if tarif_lwbp_match else None, is_float=True),
            "kWh WBP": clean_to_number(kwh_wbp_match.group(1) if kwh_wbp_match else None, is_float=False),
            "Tarif WBP": clean_to_number(tarif_wbp_match.group(1) if tarif_wbp_match else None, is_float=True),
            "kVArh": clean_to_number(kwh_kvarh_match.group(1) if kwh_kvarh_match else None, is_float=False),
            "Tarif kVArh": clean_to_number(tarif_kvarh_match.group(1) if tarif_kvarh_match else None, is_float=True)
        }
        return data

    except Exception as e:
        print(f"Gagal memproses file {os.path.basename(pdf_path)}: {e}")
        return None


def process_folder_to_json(folder_path):
    """Menelusuri satu folder, mengekstrak semua PDF, dan menyimpannya ke [nama_folder].json."""
    all_data = []

    # Cari semua file pdf di dalam folder tersebut
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, file_name)
            extracted_data = extract_pln_data(pdf_path)
            if extracted_data:
                all_data.append(extracted_data)

    if all_data:
        folder_name = os.path.basename(os.path.abspath(folder_path))
        output_filename = f"{folder_name}.json"
        output_path = os.path.join(folder_path, output_filename)

        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(all_data, json_file, indent=4, ensure_ascii=False)
        print(f"   -> BERHASIL: {len(all_data)} file disimpan di {output_filename}")
    else:
        print("   -> (Tidak ada file PDF tagihan yang valid ditemukan)")


# --- PERUBAHAN UTAMA DI SINI ---
def run_multiple_jobs(master_folder_path):
    """Menelusuri folder master dan menjalankan ekstraksi untuk setiap sub-folder."""
    if not os.path.exists(master_folder_path):
        print("Folder Master tidak ditemukan!")
        return

    print(f"Memulai Scan Folder Master: {master_folder_path}\n" + "=" * 50)

    # Mengambil semua item (folder/file) yang ada di dalam folder master
    sub_items = os.listdir(master_folder_path)
    job_count = 0

    for item in sub_items:
        full_path = os.path.join(master_folder_path, item)

        # Pastikan yang diproses hanya yang berupa FOLDER (bukan file log/script)
        if os.path.isdir(full_path):
            job_count += 1
            print(f"\n[JOB {job_count}] Memproses Folder: {item}")
            process_folder_to_json(full_path)

    print("\n" + "=" * 50 + f"\nSelesai! {job_count} folder job telah diperiksa.")


if __name__ == "__main__":
    # CONTOH STRUKTUR FOLDER:
    # C:\Data_PLN_Master\
    #    ├── Job_Folder_1\ (isinya PDF)
    #    ├── Job_Folder_2\ (isinya PDF)
    #    └── Job_Folder_10\ (isinya PDF)

    # Cukup arahkan ke FOLDER INDUKNYA saja di bawah ini:
    master_folder = r"G:\IOT\unesa\capture\tagihan"

    run_multiple_jobs(master_folder)