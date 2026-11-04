🎵 Pygame Music Player - Typography ShowcaseAplikasi pemutar musik berbasis Pygame dengan tampilan User Interface (UI) bernuansa Dark Mode modern. Proyek ini memamerkan penggunaan hirarki tipografi secara estetis menggunakan 4 variasi bobot font Poppins.📸 Preview Tampilanalign="center">
✨ Fitur UtamaTipografi Terstruktur: Menerapkan 4 variasi font (Bold, Medium, Regular, Italic) untuk menciptakan hirarki visual yang jelas.Efek Text Shadow: Rendisi teks dilengkapi bayangan (offset) halus untuk efek timbul dan keterbacaan yang tinggi.Smart Font Fallback: Sistem deteksi font otomatis—jika file font kustom tidak ditemukan, aplikasi akan berpindah ke font bawaan sistem tanpa memicu crash.UI Responsive & Modern: Menggunakan palet warna konsisten dengan sudut card border-radius yang lembut.📂 Struktur Proyek├── assets/
│   ├── fonts/
│   │   ├── Poppins-Bold.ttf
│   │   ├── Poppins-Medium.ttf
│   │   ├── Poppins-Regular.ttf
│   │   └── Poppins-Italic.ttf
│   └── preview.png          # Foto pratinjau tampilan aplikasi
├── main.py                  # Script utama Pygame
└── README.md                # Dokumentasi proyek
🎨 Penggunaan FontJenis FontFile AssetPeruntukan UIBoldPoppins-Bold.ttfJudul lagu utama (Now Playing)MediumPoppins-Medium.ttfJudul seksi & header playlistRegularPoppins-Regular.ttfNama lagu pada daftar playlist & durasiItalicPoppins-Italic.ttfSub-teks nama artis & genre musik🚀 Cara Menjalankan1. PrasyaratPastikan Anda sudah menginstal Python versi 3.8 ke atas di komputer Anda.2. Instalasi DependensiInstal pustaka Pygame menggunakan pip:pip install pygame
3. Jalankan AplikasiJalankan file main.py melalui terminal atau prompt perintah:python main.py
📝 LisensiProyek ini berada di bawah lisensi MIT License. Bebas digunakan dan dikembangkan kembali.
