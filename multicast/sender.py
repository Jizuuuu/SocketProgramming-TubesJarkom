import socket
import logging
import json
import struct
import os
import time
import math

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 10000
SEND_DIR = 'send_files'
CHUNK_SIZE = 1024  # Ukuran payload per paket UDP

def start_sender():
    os.makedirs(SEND_DIR, exist_ok=True)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    
    while True:
        print("\n" + "="*50)
        print("Pilih aksi UDP Multicast:")
        print("1. Kirim Teks")
        print("2. Kirim File")
        print("3. Exit")
        pilihan = input("> ")
        
        if pilihan == '3' or pilihan.lower() == 'exit':
            break
            
        if pilihan == '1':
            pesan = input("Masukkan pesan: ")
            if not pesan: continue
            
            payload = pesan.encode('utf-8')
            header = json.dumps({'type': 'text', 'size': len(payload)}).encode('utf-8')
            
            # Format paket: 4 byte len(header) + header + payload
            packet = struct.pack('>I', len(header)) + header + payload
            sock.sendto(packet, (MCAST_GRP, MCAST_PORT))
            logging.info("Pesan teks Multicast terkirim.")
            
        elif pilihan == '2':
            filename = input("Masukkan nama file: ")
            filepath = os.path.join(SEND_DIR, filename)
            
            if not os.path.isfile(filepath):
                logging.error(f"File tidak ditemukan: {filepath}")
                continue
                
            filesize = os.path.getsize(filepath)
            total_chunks = math.ceil(filesize / CHUNK_SIZE)
            
            header = json.dumps({
                'type': 'file',
                'filename': filename,
                'size': filesize,
                'chunks': total_chunks
            }).encode('utf-8')
            
            # Kirim Header File
            header_packet = struct.pack('>I', len(header)) + header
            sock.sendto(header_packet, (MCAST_GRP, MCAST_PORT))
            time.sleep(0.5) # Beri waktu semua receiver memproses header
            
            logging.info(f"Mulai mengirim file multicast {filename} ({total_chunks} chunks)")
            last_percent = 0
            
            with open(filepath, 'rb') as f:
                for i in range(total_chunks):
                    chunk_data = f.read(CHUNK_SIZE)
                    # Paket chunk: index (4 bytes) + chunk_data
                    chunk_packet = struct.pack('>I', i) + chunk_data
                    sock.sendto(chunk_packet, (MCAST_GRP, MCAST_PORT))
                    time.sleep(0.005) # Jeda kecil mencegah packet drop berlebihan
                    
                    percent = ((i+1) / total_chunks) * 100
                    if percent >= last_percent + 10:
                        print(f"Progress Send: {int(last_percent + 10)}%")
                        last_percent += 10
                        
            logging.info("Selesai mengirim file ke Multicast Group.")

if __name__ == "__main__":
    start_sender()
