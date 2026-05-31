import socket
import logging
import struct
import json
import os

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

BCAST_PORT = 10001
RECV_DIR = 'received_files'
CHUNK_SIZE = 1024

def start_receiver():
    os.makedirs(RECV_DIR, exist_ok=True)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    sock.bind(('', BCAST_PORT))
    
    logging.info(f"Receiver Broadcast berjalan dan mendengarkan port {BCAST_PORT}")
    
    while True:
        try:
            data, addr = sock.recvfrom(65535)
            
            if len(data) >= 4:
                try:
                    header_len = struct.unpack('>I', data[:4])[0]
                    if 0 < header_len < 2048:
                        header_bytes = data[4:4+header_len]
                        header = json.loads(header_bytes.decode('utf-8'))
                        
                        if header.get('type') == 'text':
                            payload = data[4+header_len:]
                            logging.info(f"Pesan Broadcast dari {addr}: {payload.decode('utf-8')}")
                            
                        elif header.get('type') == 'file':
                            filename = header.get('filename')
                            total_chunks = header.get('chunks')
                            size = header.get('size')
                            logging.info(f"Pengumuman file Broadcast: {filename} ({size} bytes)")
                            terima_file(sock, filename, total_chunks, size, addr)
                except:
                    pass
                    
        except Exception as e:
            logging.error(f"Error: {e}")

def terima_file(sock, filename, total_chunks, size, sender_addr):
    filepath = os.path.join(RECV_DIR, filename)
    received_chunks = set()
    last_percent = 0
    
    sock.settimeout(5.0) 
    
    with open(filepath, 'wb') as f:
        f.truncate(size)
        
        while len(received_chunks) < total_chunks:
            try:
                data, addr = sock.recvfrom(65535)
                if addr != sender_addr: continue
                
                chunk_index = struct.unpack('>I', data[:4])[0]
                chunk_data = data[4:]
                
                if chunk_index not in received_chunks:
                    offset = chunk_index * CHUNK_SIZE
                    f.seek(offset)
                    f.write(chunk_data)
                    received_chunks.add(chunk_index)
                
                percent = (len(received_chunks) / total_chunks) * 100
                if percent >= last_percent + 10:
                    print(f"Progress Receive: {int(last_percent + 10)}%")
                    last_percent += 10
                    
            except socket.timeout:
                logging.warning(f"Timeout! Menerima {len(received_chunks)}/{total_chunks} chunks.")
                break
                
    sock.settimeout(None)
    if len(received_chunks) == total_chunks:
        logging.info(f"File {filename} berhasil diterima secara utuh dari Broadcast.")

if __name__ == "__main__":
    start_receiver()
