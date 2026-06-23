import socket
import cv2
import os
import sys
import time
from datetime import datetime

# Konfigurasi Server & Folder
TCP_IP = '0.0.0.0'
TCP_PORT = 5005
BUFFER_SIZE = 1024
SAVE_FOLDER = "G:\\IOT\\unesa\\capture"
RTSP_URL = "rtsp://admin:1234567890@192.168.1.130:8554/Streaming/Channels/101"

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
s.settimeout(1.0)

print(f"Server Python Aktif di Port {TCP_PORT}.")
print("Tekan Ctrl + C untuk keluar secara aman.\n")

try:
    while True:
        try:
            conn, addr = s.accept()
        except socket.timeout:
            continue

        print(f"\nMendapat koneksi dari Wemos IP: {addr[0]}")
        conn.settimeout(30.0)  # Ditambah jadi 10 detik agar aman

        try:
            data = conn.recv(BUFFER_SIZE).decode('utf-8').strip()

            if data == "CAPTURE_NOW":
                print("Wemos meminta capture. Membuka stream RTSP CCTV...")

                sukses_capture = False
                cap = cv2.VideoCapture(RTSP_URL)

                if cap.isOpened():
                    # --- OPTIMASI 1: PERLAMBAT PROSES (WARM-UP) ---
                    print("Kamera terhubung. Memberi jeda stabilitas sensor (5 detik)...")
                    time.sleep(5)

                    # Buang 20 frame pertama untuk menguras cache video lama/blur
                    print("Membuang frame awal yang kosong...")
                    for _ in range(20):
                        cap.read()

                    # Ambil frame yang murni dan stabil
                    ret, frame = cap.read()

                    if ret:
                        # Simpan Gambar ke Hardisk
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"snapshot_{timestamp}.jpg"
                        filepath = os.path.join(SAVE_FOLDER, filename)
                        cv2.imwrite(filepath, frame)
                        print(f"✓ Gambar BERHASIL disimpan: {filepath}")
                        sukses_capture = True

                        # --- OPTIMASI 2: TAMPILKAN DI LAYAR SEBENTAR ---
                        print("Menampilkan hasil capture di layar...")
                        # Buat jendela tampilan yang bisa diatur ukurannya
                        cv2.namedWindow("Hasil Capture Dahua", cv2.WINDOW_NORMAL)
                        cv2.resizeWindow("Hasil Capture Dahua", 640, 480)
                        cv2.imshow("Hasil Capture Dahua", frame)

                        # Tampilkan selama 3 detik (3000 milidetik), lalu tutup otomatis
                        cv2.waitKey(3000)
                        cv2.destroyAllWindows()
                        print("Jendela tampilan ditutup.")

                cap.release()

                # Kirim sinyal balik ke Wemos
                if sukses_capture:
                    print("Mengirim perintah SHUTDOWN_RELAY...")
                    conn.sendall("SHUTDOWN_RELAY\n".encode('utf-8'))
                else:
                    print("X Gagal mendapatkan frame matang dari RTSP.")
                    conn.sendall("FAILED_CAPTURE\n".encode('utf-8'))

                conn.shutdown(socket.SHUT_WR)

        except socket.timeout:
            print("X Koneksi timeout saat membaca data dari Wemos.")
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
            cv2.destroyAllWindows()  # Antisipasi jika hang saat jendela terbuka
        finally:
            conn.close()

except KeyboardInterrupt:
    print("\n[INFO] Server dimatikan via Ctrl+C.")
finally:
    s.close()
    cv2.destroyAllWindows()
    sys.exit(0)