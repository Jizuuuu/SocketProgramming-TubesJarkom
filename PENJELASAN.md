# Penjelasan Lengkap Kode & Tahapan Proyek (Socket Programming)

Dokumen ini memuat penjelasan mendetail (*code breakdown*) dari seluruh struktur folder, fungsi masing-masing folder, dan file kode (*source code*) yang telah dibuat secara bertahap dari Tahap 1 hingga Tahap 10.

---

## Struktur Folder Proyek
Berikut adalah fungsi dari masing-masing folder di dalam proyek ini:
* **`unicast/`** : Folder ini berisi file implementasi protokol TCP Unicast (Satu-ke-satu). Terdapat file server (single-thread & multi-thread) dan file client berbasis terminal (CLI). Folder ini menampung pengerjaan Tahap 1, Tahap 2, dan Tahap 3.
* **`multicast/`** : Folder ini memuat implementasi protokol UDP Multicast (Satu-ke-banyak grup). Terdapat program sender dan receiver untuk mendemonstrasikan pengiriman file/teks serentak ke banyak komputer yang tergabung di grup IP `224.1.1.1`. Menampung pengerjaan Tahap 4 dan Tahap 5.
* **`broadcast/`** : Folder ini memuat implementasi protokol UDP Broadcast (Satu-ke-semua massal). Program sender di sini akan membanjiri jaringan (IP `255.255.255.255`) dan semua komputer di jaringan (receiver) akan menerimanya. Menampung pengerjaan Tahap 6 dan Tahap 7.
* **`common/`** : Folder ini berfungsi sebagai "Shared Library" atau modul utilitas bersama. File di sini berisi konfigurasi (*config*) dan fungsi pencatatan (*logger*) yang dipanggil (di-*import*) oleh semua file di folder lain agar kode lebih rapi (*Refactoring* - Tahap 8).
* **`gui/`** : Folder ini dikhususkan untuk tampilan visual atau antarmuka grafis (Graphical User Interface) menggunakan pustaka `tkinter`. Aplikasi ini membungkus logika koneksi TCP ke dalam bentuk visual yang ramah pengguna (Tahap 9).
* **`received_files/`** : Folder tempat file-file hasil unduhan (*download*)/penerimaan dari klien atau server disimpan.
* **`send_files/`** : Folder khusus (*sandbox*) untuk menaruh file-file yang akan diuji coba untuk dikirim melalui CLI.

---

## 1. Folder `unicast/` (Tahap 1, 2, dan 3)
Berisi implementasi dasar protokol TCP Unicast (1-ke-1) menggunakan arsitektur Client-Server.

### ├── unicast/
│   ├── server_single.py
│   ├── server_multi.py
│   └── client.py

Kedua file server ini adalah *Main Server* TCP yang mendengarkan (*listen*) di port `8080`. Sengaja dipisah agar Anda mudah mendemonstrasikan versi **Single Thread** (Tahap 1 & 2) dan **Multithread** (Tahap 3) ke Dosen.
* **Arsitektur Jaringan:** Menggunakan koneksi TCP (`socket.SOCK_STREAM`) yang menjamin paket sampai secara utuh dan berurutan (*reliable*).
* **Fitur Multithread (Tahap 3):** Kode tidak memblokir saat melayani satu *client*. Melainkan, pada fungsi `start_server()`, setiap kali fungsi `server_socket.accept()` mendapatkan *client* baru, server akan melahirkan *Thread* baru (`threading.Thread(target=handle_client)`) untuk menangani pengiriman dan penerimaan dari *client* tersebut.
* **Fitur File Transfer (Tahap 2):** Menggunakan struktur pesan dengan *Custom JSON Header*. Sebelum mengirim data, *client* mengirim paket berisi ukuran panjang *header* (4 bytes), diikuti string *JSON header* (`{"type": "file", "filename": "x.jpg", "size": 1000}`). Server membaca ukuran ini dan melakukan iterasi iterasi `f.write(chunk)` ke dalam folder `received_files/` secara aman dari RAM.

---

## 2. Folder `multicast/` (Tahap 4 dan 5)
Berisi implementasi datagram UDP Multicast (Satu-ke-banyak grup).

### Konsep Dasar & Skenario Uji Coba Lintas Laptop
Konsepnya adalah satu laptop bertindak sebagai pengirim (*Sender*), dan laptop lainnya bertindak sebagai penerima (*Receiver*). Saat diuji coba: Anda dapat menjalankan `receiver.py` di 2-3 laptop berbeda. Saat satu laptop menjalankan `sender.py` menembakkan file, maka semua laptop receiver tersebut akan menerima file secara *serentak bersamaan* hanya dengan satu klik kirim. (Syarat: satu jaringan Wi-Fi/LAN yang sama dan Windows Firewall diizinkan).

### `multicast/sender.py` (Sisi Pengirim)
* **Konsep Jaringan:** Mengirim ke IP Multicast Grup `224.1.1.1` di port `10000` menggunakan protokol UDP (`socket.SOCK_DGRAM`).
* **Time-to-Live (TTL):** Paket UDP Multicast di-set nilai `IP_MULTICAST_TTL = 2`. Ini menentukan seberapa jauh paket multicast boleh menyebar melewati *router*.
* **Mekanisme UDP File Chunking:** UDP tidak menjamin file besar sampai dengan utuh (dibatasi MTU jaringan). Oleh karena itu, file besar dipotong-potong menjadi ukuran kecil (1024 byte). Setiap paket ditambahkan **4 byte Index Header** di depannya. Tujuannya adalah agar *Receiver* tahu urutan ke-berapa potongan (paket) ini berada (misal: chunk ke-0, chunk ke-1).

### `multicast/receiver.py` (Sisi Penerima)
* Menjalankan fungsi `bind` ke *port* 10000 secara *any interface* (`0.0.0.0`).
* **Bergabung ke Grup (IP_ADD_MEMBERSHIP):** Kartu jaringan (NIC) komputer secara resmi mendaftarkan dirinya ke IP grup `224.1.1.1` dengan perintah `setsockopt`. Tanpa ini, OS akan mengabaikan paket multicast yang masuk.
* **Penyusunan Ulang yang Tangguh (File Pre-Allocation & Seeking):** Karena UDP tidak menjamin urutan (*out-of-order*) dan ada kemungkinan paket datang acak, receiver tidak menulis file secara berurutan biasa.
  1. Receiver membuat file kosong dengan ukuran penuh di *disk* menggunakan perintah `f.truncate(size)`.
  2. Saat chunk UDP masuk, receiver membaca indeksnya dari header 4-byte.
  3. Menghitung posisi tepat byte tersebut (`offset = indeks_chunk * 1024`).
  4. Melakukan pencarian posisi menggunakan `f.seek(offset)` dan menulis datanya di posisi yang tepat.

---

## 3. Folder `broadcast/` (Tahap 6 dan 7)
Berisi implementasi UDP Broadcast (Satu-ke-semua massal). Pengiriman ke seluruh perangkat yang ada di dalam satu segmen jaringan (subnet) lokal yang sama secara paksa, mirip berteriak menggunakan pengeras suara (megafon) di ruangan kelas.

### `broadcast/sender.py` (Sisi Pengirim)
* **Izin Broadcast (SO_BROADCAST):** Secara bawaan, OS melarang aplikasi mengirim paket broadcast karena bisa membanjiri jaringan. Di dalam kode, pengirim harus mengaktifkan opsi khusus `client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)` agar OS mengizinkannya.
* Paket ditembakkan ke alamat siar (*broadcast address*), yakni `255.255.255.255`.
* Mekanisme pemotongan file (chunking) dan header 4-byte sama dengan multicast.

### `broadcast/receiver.py` (Sisi Penerima)
* **Tanpa Perlu Gabung Grup:** Berbeda dengan Multicast, penerima broadcast **tidak memerlukan** kode pendaftaran ke grup (`IP_ADD_MEMBERSHIP`). Cukup *stand-by* mendengarkan pada port Broadcast `10001` dengan IP `0.0.0.0`. Selama terhubung di jaringan, OS otomatis meloloskan paket tersebut.
* Algoritma perakitan file (*file re-assembly*) menggunakan cara `f.truncate` dan `f.seek` persis seperti modul Multicast.

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
* Sebuah aplikasi berjendela yang memanfaatkan `tkinter`. Menggabungkan kode inti dari *TCP Multithread* dengan elemen grafis.
* Terdapat elemen **ScrolledText** untuk memonitor log secara riil (*real-time*).
* Menampilkan antrean **Listbox** yang menampilkan IP secara *live* dari setiap *Client* yang baru masuk dan akan hilang secara otomatis sesaat setelah *Client* melakukan *disconnect*.
* Menggunakan teknik pemrograman *Asynchronous / Threading* untuk GUI (`daemon=True`) agar tampilan jendela (*window*) tidak *freeze* atau membeku (Not Responding) pada saat ada proses penerimaan file besar.

### `gui/client_gui.py`
* Memiliki bidang isian (`Entry`) dinamis tempat pengguna bisa mengetikkan nomor IP Server pada jaringan lokal.
* Menggunakan fitur `filedialog.askopenfilename()` untuk memanggil menu penjelajah *file* (File Explorer) milik OS bawaan agar Anda bisa dengan bebas mengeklik dan memilih file JPG / MP4 dari direktori manapun di dalam PC, tanpa repot meng-copy filenya ke dalam folder khusus `send_files`.

---

## 6. Tahap 10 (Dokumentasi Akhir)
Seluruh pengerjaan bermuara pada file `README.md` dan `PENJELASAN.md` ini sebagai dokumentasi level tinggi, siap untuk mempermudah saat pengerjaan laporan akhir PDF.
> [!NOTE]
> Semua bagian kode dibangun di atas kapabilitas *pure standard library* Python untuk menjamin *portability* di sembarang *platform* (Windows/Linux/Mac) tanpa instalasi *dependency* yang menyusahkan.
