// config25.js
const DAFTAR_PERIODE_TAGIHAN = {
    "LIDAH_WETAN": [
        { value: "lidah_Januari_26", label: "Januari 2026 (Lidah Wetan)" },
        { value: "lidah_Februari_26", label: "Februari 2026 (Lidah Wetan)" },
        { value: "lidah_Maret_26", label: "Maret 2026 (Lidah Wetan)" },
        { value: "lidah_April_26", label: "April 2026 (Lidah Wetan)" },
        { value: "lidah_Mei_26", label: "Mei 2026 (Lidah Wetan)" },
        { value: "lidah_Juni_26", label: "Juni 2026 (Lidah Wetan)" }
        // Bulan depan cukup tambah di sini, contoh:
        // { value: "lidah_juli_26", label: "Juli 2026 (Lidah Wetan)" }
    ],
    "KETINTANG": [
        { value: "ktt_Januari_26", label: "Januari 2026 (Ketintang)" },
        { value: "ktt_Februari_26", label: "Februari 2026 (Ketintang)" },
        { value: "ktt_Maret_26", label: "Maret 2026 (Ketintang)" },
        { value: "ktt_April_26", label: "April 2026 (Ketintang)" },
        { value: "ktt_Mei_26", label: "Mei 2026 (Ketintang)" },
        { value: "ktt_Juni_26", label: "Juni 2026 (Ketintang)" }
    ],
    "MUSTOPO": [
        { value: "mus_Januari_26", label: "Januari 2026 (Mustopo)" },
        { value: "mus_Februari_26", label: "Februari 2026 (Mustopo)" },
        { value: "mus_Maret_26", label: "Maret 2026 (Mustopo)" },
        { value: "mus_April_26", label: "April 2026 (Mustopo)" },
        { value: "mus_Mei_26", label: "Mei 2026 (Mustopo)" },
        { value: "mus_Juni_26", label: "Juni 2026 (Mustopo)" }
    ],
    "GABUNGAN":[
        // PENTING: Pisahkan dengan koma file-file yang mau digabung secara otomatis
        { value: "lidah_Januari_26,ktt_Januari_26,mus_Januari_26", label: "🌍 Total Gabungan 3 Kampus (Januari 2026)" },
        { value: "lidah_Februari_26,ktt_Februari_26,mus_Februari_26", label: "🌍 Total Gabungan 3 Kampus (Februari 2026)" },
        { value: "lidah_Maret_26,ktt_Maret_26,mus_Maret_26", label: "🌍 Total Gabungan 3 Kampus (Maret 2026)" },
        { value: "lidah_April_26,ktt_April_26,mus_April_26", label: "🌍 Total Gabungan 3 Kampus (April 2026)" },
        { value: "lidah_Mei_26,ktt_Mei_26,mus_Mei_26", label: "🌍 Total Gabungan 3 Kampus (Mei 2026)" },
        { value: "lidah_Juni_26,ktt_Juni_26,mus_Juni_26", label: "🌍 Total Gabungan 3 Kampus (Juni 2026)" },
        { value: "lidah_Januari_26,lidah_Februari_26,lidah_Maret_26,lidah_April_26,lidah_Mei_26,lidah_Juni_26,ktt_Januari_26,ktt_Februari_26,ktt_Maret_26,ktt_April_26,ktt_Mei_26,ktt_Juni_26,mus_Januari_26,mus_Februari_26,mus_Maret_26,mus_April_26,mus_Mei_26,mus_Juni_26", label: "📊 Total Rekap Tahunan 2026 (Semua Data)" }
    
    ]
};
