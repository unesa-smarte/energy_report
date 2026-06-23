import os
import json
import re
import pdfplumber


def clean_to_number(text_value, is_float=False):
    """Fungsi pembantu untuk mengubah teks angka berformat (koma/titik) menjadi int atau float murni."""
    if not text_value:
        return 0 if not is_float else 0.0
    # Hilangkan lambang Rp, spasi, dan karakter non-angka kecuali titik/koma
    clean = re.sub(r"[^\d\.,]", "", text_value)

    if is_float:
        # Jika float (seperti tarif 1444.70 atau 900.00)
        # Menangani jika ada koma sebagai ribuan, kita hapus dulu
        if "," in clean and "." in clean:
            clean = clean.replace(",", "")
        elif "," in clean and "." not in clean:
            # Jika koma digunakan sebagai desimal (khas Indonesia)
            clean = clean.replace(",", ".")
        try:
            return float(clean)
        except ValueError:
            return 0.0
    else:
        # Jika integer (seperti total tagihan atau daya VA)
        # Hapus semua titik dan koma pemisah ribuan
        clean = clean.replace(".", "").replace(",", "")
        try:
            return int(clean)
        except ValueError:
            return 0


def extract_pln_data(pdf_path):
    """Mengekstrak data tagihan PLN dengan perbaikan sintaksis (if_wbp) dan proteksi error."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "".join([page.extract_text() for page in pdf.pages if page.extract_text()])

        if not text:
            print(f"Peringatan: File {os.path.basename(pdf_path)} kosong atau berupa gambar scan.")
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

        # Menyusun data (Bagian Tarif WBP sudah diperbaiki ke tarif_wbp_match)
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
    """Menelusuri folder, mengekstrak semua PDF, dan menyimpannya ke [nama_folder].json."""
    if not os.path.exists(folder_path):
        print("Folder tidak ditemukan. Sila periksa kembali jalurnya.")
        return

    all_data = []
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, file_name)
            print(f"Memproses: {file_name}...")

            extracted_data = extract_pln_data(pdf_path)
            if extracted_data:
                all_data.append(extracted_data)

    folder_name = os.path.basename(os.path.abspath(folder_path))
    output_filename = f"{folder_name}.json"
    output_path = os.path.join(folder_path, output_filename)

    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(all_data, json_file, indent=4, ensure_ascii=False)

    print("\n--- Selesai ---")
    print(f"Berhasil mengekstrak {len(all_data)} file.")
    print(f"Data disimpan di: {output_path}")


if __name__ == "__main__":
    target_folder = r"G:\IOT\unesa\capture\tagihan\lidah_Juni_26"

    process_folder_to_json(target_folder)