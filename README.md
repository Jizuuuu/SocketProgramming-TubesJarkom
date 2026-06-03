# Tugas Besar Socket Programming

Aplikasi Socket Programming komprehensif yang diimplementasikan menggunakan Python. Dibuat untuk memenuhi Tugas Besar Jaringan Komputer. Sistem ini mencakup pengiriman teks dan file menggunakan TCP Unicast, UDP Multicast, UDP Broadcast, dilengkapi dengan modul GUI Tkinter.

## 1. Penjelasan Arsitektur Sistem
Sistem ini memadukan 3 arsitektur besar:
* **TCP Unicast (Multithread):** Bersifat *Connection-Oriented*. Menggunakan arsitektur *Client-Server*. Server diatur menjadi *Multithread* (Daemon Threads) sehingga mampu menangani banyak Client serentak tanpa *blocking*.
* **UDP Multicast:** Bersifat *Connection-Less* (satu-ke-banyak selektif). Paket dialamatkan ke IP khusus Multicast Group (`224.1.1.1`).
* **UDP Broadcast:** Bersifat *Connection-Less* (satu-ke-semua massal). Paket dibuang ke alamat *Broadcast* (`255.255.255.255` / `<broadcast>`) untuk membanjiri jaringan LAN.

Karena menggunakan *byte stream* universal, kita merancang sebuah **Custom JSON Header** agar mesin dapat membedakan mana pesan Teks dan mana pesan File, beserta ekstensi dan ukurannya.

## 2. Diagram Komunikasi TCP & UDP

```mermaid
graph TD
    subgraph TCP Unicast
    Client1[Client 1] -->|Kirim Teks/File| Server((Server TCP\nMultithread))
    Client2[Client 2] -->|Kirim Teks/File| Server
    Server -.->|Reply ACK| Client1
    Server -.->|Reply ACK| Client2
    end
    
    subgraph UDP Multicast/Broadcast
    UDPSender[UDP Sender] -->|Kirim Datagram| Jaringan((IP Group/Broadcast))
    Jaringan --> Receiver1[Receiver 1]
    Jaringan --> Receiver2[Receiver 2]
    end
```

## 3. Flowchart Transfer File UDP (Mekanisme Chunking)

```mermaid
flowchart TD
    A([Start Sender]) --> B[Baca Ukuran File]
    B --> C[Hitung Jumlah Chunk]
    C --> D[Kirim JSON Header]
    D --> E[Baca File 1024 Byte]
    E --> F[Kirim Chunk Index + Data]
    F --> G{File Habis?}
    G -- Belum --> E
    G -- Sudah --> H([Selesai])
```

## 4. Panduan Instalasi
1. Pastikan Anda telah menginstal **Python 3.13+**.
2. *Clone* atau esktrak *source code* ini ke dalam satu *folder*.
3. Sistem murni menggunakan pustaka standar Python bawaan (*Standard Libraries*) seperti `socket`, `threading`, `json`, `struct`, dan `tkinter`. **Tidak perlu** menginstal pustaka pihak ketiga melalui `pip`.

## 5. Panduan Demo Presentasi
Kami merekomendasikan skenario berikut saat presentasi (bisa antar Laptop jika terhubung dalam 1 jaringan Wi-Fi/LAN):
1. **Demo Unicast TCP Multithread:**
   * **Laptop 1:** Eksekusi `python unicast/server_multi.py` (Atau `server_single.py` untuk menguji perbedaan Single-Thread).
   * **Laptop 2 & 3 (Atau Terminal Berbeda):** Eksekusi `python unicast/client.py` dan masukkan IP dari Laptop 1.
   * Tunjukkan pengiriman sebuah Teks dan sebuah File (`.jpg`) secara hampir bersamaan. Perlihatkan *progress bar* yang berjalan paralel karena *multithreading*.
2. **Demo UDP Multicast (Satu-ke-Banyak Grup):**
   * **Laptop 2 & 3:** Jalankan `python multicast/receiver.py` (keduanya kini tergabung dalam grup `224.1.1.1`).
   * **Laptop 1:** Jalankan `python multicast/sender.py` lalu kirim file video `.mp4`. Tunjukkan bahwa cukup 1x aksi kirim, file akan terdistribusi secara serentak ke Laptop 2 dan 3 sekaligus menggunakan algoritma pemotongan (*chunking*) & penyusunan (*pre-allocation*).
3. **Demo UDP Broadcast (Satu-ke-Semua):**
   * Mirip dengan Multicast, jalankan `python broadcast/receiver.py` di beberapa laptop (keduanya akan *stand-by* mendengarkan jaringan).
   * **Laptop 1:** Jalankan `python broadcast/sender.py`. Kiriman ini bersifat menyiarkan ke satu subnet secara paksa (*flooding*), dan otomatis dibaca oleh receiver tanpa perlu mendaftar grup khusus.
4. **Demo GUI (Nilai Tambahan):**
   * Buka `python gui/server_gui.py` klik Start. Buka `python gui/client_gui.py` klik Connect.
   * Tunjukkan UI interaktif untuk *chatting* dan kemampuan memilih file melalui *file picker* OS bawaan.

## 6. Daftar Pertanyaan Dosen & Kunci Jawaban
1. **Mengapa UDP perlu dipecah (*chunking*) saat mengirim file, sedangkan TCP tidak?**
   * *Jawaban:* UDP bersifat *datagram-based* dan dikirim mentah-mentah. Sebuah paket dibatasi oleh ukuran MTU (sekitar 1500 byte) router. Jika dikirim langsung 10MB, paket akan ditolak (*dropped*). Sedangkan TCP bersifat *Stream*, OS otomatis mengatur segmentasi paket dan merakit ulang (*reassembly*) di bawah kap.
2. **Apa yang terjadi jika jaringan lemot atau paket UDP hilang di jalan?**
   * *Jawaban:* UDP tidak punya fitur *Retransmission* bawaan. Dalam implementasi dasar kami, *receiver* akan mendeteksi dari indikator *Progress Receive* yang tidak mencapai 100% atau kena *Timeout* (gagal). Untuk menjadikannya *Reliable UDP*, kita perlu memprogram logika *Ack/Nack* tambahan (seperti protokol TFTP).
3. **Apa gunanya perintah `sock.setsockopt(..., SO_REUSEADDR, 1)`?**
   * *Jawaban:* Agar jika server *crash* atau dimatikan mendadak, kita bisa langsung menjalankan program lagi tanpa perlu menunggu sistem operasi merilis proteksi *port* tersebut dari status `TIME_WAIT`.
