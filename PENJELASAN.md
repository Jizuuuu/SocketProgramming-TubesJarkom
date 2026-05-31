# Penjelasan Lengkap Kode & Tahapan Proyek (Socket Programming)

Dokumen ini memuat penjelasan mendetail (*code breakdown*) dari seluruh folder dan file kode (*source code*) yang telah dibuat secara bertahap dari Tahap 1 hingga Tahap 10.

---

## 1. Folder `unicast/` (Tahap 1, 2, dan 3)
Berisi implementasi dasar protokol TCP Unicast (1-ke-1) menggunakan arsitektur Client-Server.

### `unicast/server.py`
Ini adalah *Main Server* yang mendengarkan (*listen*) di port `8080`.
* **Arsitektur Jaringan:** Menggunakan koneksi TCP (`socket.SOCK_STREAM`) yang menjamin paket sampai secara utuh dan berurutan (*reliable*).
* **Fitur Multithread (Tahap 3):** Kode tidak memblokir saat melayani satu *client*. Melainkan, pada fungsi `start_server()`, setiap kali fungsi `server_socket.accept()` mendapatkan *client* baru, server akan melahirkan *Thread* baru (`threading.Thread(target=handle_client)`) untuk menangani pengiriman dan penerimaan dari *client* tersebut.
* **Fitur File Transfer (Tahap 2):** Kode menggunakan struktur pesan dengan *Custom JSON Header*. Sebelum mengirim data, *client* mengirim paket berisi ukuran panjang *header* (4 bytes), diikuti string *JSON header* (`{"type": "file", "filename": "x.jpg", "size": 1000}`). Server membaca ukuran ini dan melakukan iterasi iterasi `f.write(chunk)` ke dalam folder `received_files/` secara aman dari RAM.
* **Penanganan Bentrok Nama:** Nama file yang diterima akan ditempelkan nomor Port pengirim (contoh: `12345_gambar.jpg`) untuk mencegah *Race Condition* saat dua klien mengirim nama file yang sama berbarengan.

### `unicast/client.py`
* Merupakan program berbasis Terminal/CLI (Command Line Interface).
* Di saat mulai, program akan meminta *input* `IP Server`. Jika kosong, akan beralih ke *localhost* (`127.0.0.1`).
* Saat `1` (Teks) dipilih: *Client* membungkus pesan sebagai byte dan menambahkan JSON Header bertipe `"text"`.
* Saat `2` (File) dipilih: *Client* meminta nama file yang wajib ada di dalam folder `send_files/`. File lalu dibaca per-potongan (*chunk*) seukuran 4096 byte dan dikirim menggunakan `sendall(chunk)`. Sistem akan mengeksekusi rumus persentase `(sent / total) * 100` untuk mencetak indikator *progress bar* 10% s.d. 100%.

---

## 2. Folder `multicast/` (Tahap 4 dan 5)
Berisi implementasi datagram UDP Multicast (Satu-ke-banyak grup).

### `multicast/sender.py`
* **Konsep Jaringan:** Mengirim ke IP Multicast Grup `224.1.1.1` di port `10000` menggunakan protokol UDP (`socket.SOCK_DGRAM`).
* **Time-to-Live (TTL):** Paket UDP Multicast di-set nilai `IP_MULTICAST_TTL = 2`, yang menentukan sejauh apa (jumlah *hop* router) paket ini bisa menyeberang di jaringan.
* **Mekanisme UDP File Chunking:** Karena UDP menolak paket berukuran besar (melebihi MTU), file yang besar (misal MP4) harus dipotong menjadi *chunk* kecil seukuran 1024 byte.
* Setiap paket potongan UDP ditambahkan **4 byte Index Header** di depannya. Tujuannya adalah agar *Receiver* tahu urutan ke-berapa potongan (paket) ini berada.

### `multicast/receiver.py`
* Menjalankan fungsi `bind` ke *port* 10000 secara *any interface* (`0.0.0.0`), lalu melakukan **IP_ADD_MEMBERSHIP** untuk menyuruh kartu jaringan (*network card*) secara resmi mendaftarkan dirinya ke grup Multicast `224.1.1.1`.
* **Mekanisme Re-Assembly:** Menggunakan *File Pre-Allocation* dengan cara `f.truncate(size)` untuk membuat file kosong sesuai ukuran penuhnya di *disk*.
* Karena urutan sampainya datagram UDP sering kali acak (*out of order delivery*), *Receiver* membaca indeks *chunk* pada datagram yang datang, lalu langsung melompat (*f.seek(offset)*) ke posisi byte yang semestinya pada file.

---

## 3. Folder `broadcast/` (Tahap 6 dan 7)
Berisi implementasi UDP Broadcast (Satu-ke-semua massal).

### `broadcast/sender.py`
* Mirip seperti Multicast, namun dengan pengaktifan level *socket option*: `SO_BROADCAST = 1`.
* Paket ditembakkan ke IP alamat siar (*broadcast address*), yakni `<broadcast>` atau `255.255.255.255`. Hal ini akan membuat paket membanjiri *switch* atau *router* ke seluruh perangkat yang terhubung dalam satu jaringan Wi-Fi/LAN lokal.

### `broadcast/receiver.py`
* Cukup mendengarkan pada port Broadcast `10001` tanpa harus mendaftarkan kehamilan atau grup apa pun. Algoritma perakitan file (file re-assembly) yang digunakan sama persis dengan modul *Multicast* (`offset = index * 1024`).

---

## 4. Folder `common/` (Tahap 8 - Refactoring)
Folder utilitas lintas sistem (Common Module) yang membungkus komponen berulang agar arsitektur menjadi modular dan mudah dipelihara (*maintainable*).

### `common/config.py`
* Berisi variabel-variabel kunci statis pendukung (*environment variables*) layaknya `TCP_HOST`, `MCAST_GRP`, dan `CHUNK_SIZE`. Dengan mengisolasi konfigurasi ke sini, saat kita kelak ingin memindahkan server ke port 9090, kita cukup mengubah 1 baris kode saja (tanpa perlu membongkar seluruh *file server, client, maupun GUI*).

### `common/logger.py`
* Bertugas menstandarkan sistem *output log console*. Semua program kita menggunakan modul *logging* bawaan Python daripada perintah `print()`. Di sinilah format waktunya didefinisikan secara baku layaknya `[14:30:00] INFO: Pesan masuk`.

---

## 5. Folder `gui/` (Tahap 9 - Tkinter GUI)
Memberikan nilai tambah dalam bentuk antarmuka visual/grafis (Graphical User Interface).

### `gui/server_gui.py`
* Sebuah aplikasi berjendela yang memanfaatkan `tkinter`.
* Menggabungkan kode inti dari *TCP Multithread* dengan elemen grafis.
* Terdapat elemen **ScrolledText** untuk memonitor log secara riil (*real-time*).
* Menampilkan antrean **Listbox** yang menampilkan IP secara *live* dari setiap *Client* yang baru masuk dan akan hilang secara otomatis sesaat setelah *Client* melakukan *disconnect*.
* Menggunakan teknik pemrograman *Asynchronous / Threading* untuk GUI (`daemon=True`) agar tampilan jendela (*window*) tidak *freeze* atau membeku (Not Responding) pada saat ada proses penerimaan file besar.

### `gui/client_gui.py`
* Sebagai pengganti dari *client* terminal CLI.
* Memiliki bidang isian (`Entry`) dinamis tempat pengguna bisa mengetikkan nomor IP Server pada jaringan lokal.
* Menggunakan fitur `filedialog.askopenfilename()` untuk memanggil menu penjelajah *file* (File Explorer) milik OS bawaan agar Anda bisa dengan bebas mengeklik dan memilih file JPG / MP4 dari direktori manapun di dalam PC, tanpa repot meng-copy filenya ke dalam folder khusus `send_files`.

---

## 6. Tahap 10 (Dokumentasi Akhir)
Seluruh pengerjaan bermuara pada file:
1. `README.md` : Dokumentasi level tinggi yang menjelaskan ke dosen ihwal topologi jaringan (via gambar diagram Mermaid), cara eksekusi, serta menangkis pertanyaan *interview*.
2. `walkthrough.md` : Dokumentasi internal historis.

> [!NOTE]
> Semua bagian kode dibangun di atas kapabilitas *pure standard library* Python untuk menjamin *portability* di sembarang *platform* (Windows/Linux/Mac) tanpa instalasi *dependency* yang menyusahkan.
