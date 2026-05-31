# TUGAS

Tugas Besar Mata Kuliah Jaringan Komputer tentang Socket Programming.

Kerjakan proyek ini dari awal sampai selesai secara bertahap, profesional, dan production-ready.

JANGAN langsung menghasilkan semua kode sekaligus.

Setiap tahap harus:

1. Menjelaskan tujuan tahap.
2. Menjelaskan konsep jaringan yang digunakan.
3. Menjelaskan struktur folder.
4. Menjelaskan alur komunikasi client-server.
5. Menghasilkan source code lengkap.
6. Menjelaskan cara menjalankan.
7. Menjelaskan cara testing.
8. Menjelaskan kemungkinan error dan solusinya.
9. Menunggu konfirmasi sebelum lanjut ke tahap berikutnya.

---

# SPESIFIKASI TUGAS BESAR

Kelompok terdiri dari 3 orang.

Buat aplikasi Socket Programming yang memenuhi seluruh requirement berikut.

## 1. UNICAST (A → B)

### SINGLE THREAD

Harus dapat mengirim:

* 1 sampai 5 kata
* 1 kalimat panjang
* 1 paragraf
* file TXT
* file DOCX
* file PDF
* gambar JPG
* gambar PNG
* audio MP3
* video MP4

### MULTITHREAD

Harus dapat mengirim:

* 1 sampai 5 kata
* 1 kalimat panjang
* 1 paragraf
* file TXT
* file DOCX
* file PDF
* gambar JPG
* gambar PNG
* audio MP3
* video MP4

Server harus mampu melayani banyak client secara bersamaan menggunakan threading.

---

## 2. MULTICAST (A → B,C)

Harus dapat mengirim:

* 1 sampai 5 kata
* 1 kalimat panjang
* 1 paragraf
* file TXT
* file DOCX
* file PDF
* gambar JPG
* gambar PNG
* audio MP3
* video MP4

Gunakan UDP Multicast.

---

## 3. BROADCAST (A → SEMUA)

Harus dapat mengirim:

* 1 sampai 5 kata
* 1 kalimat panjang
* 1 paragraf
* file TXT
* file DOCX
* file PDF
* gambar JPG
* gambar PNG
* audio MP3
* video MP4

Gunakan UDP Broadcast.

---

# BAHASA PEMROGRAMAN

Python 3.13+

---

# LIBRARY YANG BOLEH DIGUNAKAN

* socket
* threading
* queue
* os
* pathlib
* struct
* time
* json
* tkinter
* logging
* hashlib

Hindari library yang tidak diperlukan.

---

# TARGET HASIL AKHIR

Project harus memiliki struktur folder yang rapi.

Contoh:

SocketProgramming/
│
├── unicast/
│   ├── server.py
│   ├── client.py
│   ├── send_files/
│   └── received_files/
│
├── multicast/
│   ├── sender.py
│   ├── receiver.py
│   ├── send_files/
│   └── received_files/
│
├── broadcast/
│   ├── sender.py
│   ├── receiver.py
│   ├── send_files/
│   └── received_files/
│
├── common/
│   ├── file_transfer.py
│   ├── logger.py
│   ├── config.py
│   └── utils.py
│
├── docs/
│   ├── screenshots/
│   └── laporan/
│
└── README.md

---

# FITUR WAJIB

## Text Messaging

Support:

* kata
* kalimat
* paragraf

---

## File Transfer

Support:

* TXT
* DOCX
* PDF
* JPG
* PNG
* MP3
* MP4

Gunakan transfer berbasis byte stream.

Jangan membuat kode berbeda untuk setiap jenis file.

Buat satu mekanisme universal.

---

## Progress Transfer

Saat file dikirim tampilkan:

10%
20%
30%
...
100%

---

## Logging

Simpan aktivitas ke file log.

Contoh:

[12:30:00] Client connected
[12:30:10] Message sent
[12:31:00] File transferred

---

## Error Handling

Tangani:

* file tidak ditemukan
* koneksi terputus
* timeout
* client disconnect
* port digunakan aplikasi lain

---

# GUI (NILAI TAMBAHAN)

Setelah seluruh fitur terminal selesai, buat GUI menggunakan Tkinter.

GUI minimal memiliki:

* area chat
* tombol kirim
* tombol pilih file
* daftar client aktif
* status koneksi

GUI dibuat pada tahap terakhir.

---

# DOKUMENTASI

Setelah semua kode selesai:

1. Buat README lengkap.
2. Buat penjelasan arsitektur sistem.
3. Buat diagram komunikasi.
4. Buat flowchart.
5. Buat panduan instalasi.
6. Buat panduan demo presentasi.
7. Buat daftar pertanyaan dosen dan jawabannya.

---

# PRESENTASI

Siapkan materi untuk menjelaskan:

1. Apa itu Socket Programming.
2. Apa itu TCP.
3. Apa itu UDP.
4. Perbedaan Unicast, Multicast, Broadcast.
5. Perbedaan Single Thread dan Multithread.
6. Alur transfer file.
7. Alur komunikasi client-server.
8. Demo sistem.

---

# METODE KERJA

Kerjakan dengan urutan berikut:

Tahap 1:
UNIXCAST TCP Single Thread Text Chat

Tahap 2:
UNIXCAST TCP File Transfer

Tahap 3:
UNIXCAST TCP Multithread

Tahap 4:
UDP Multicast Text

Tahap 5:
UDP Multicast File Transfer

Tahap 6:
UDP Broadcast Text

Tahap 7:
UDP Broadcast File Transfer

Tahap 8:
Refactoring dan Common Module

Tahap 9:
GUI Tkinter

Tahap 10:
Dokumentasi dan Presentasi

---

# ATURAN PENTING

* Jangan melompat ke tahap berikutnya sebelum tahap saat ini selesai.
* Selalu tampilkan source code lengkap, bukan potongan kode.
* Jelaskan setiap file yang dibuat.
* Gunakan best practice Python.
* Berikan kode yang siap dijalankan.
* Jika ada bug, lakukan debugging dan revisi sampai selesai.
* Bertindak sebagai mentor sampai seluruh proyek selesai.
