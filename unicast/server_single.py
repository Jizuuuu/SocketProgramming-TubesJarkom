import socket
import logging
import struct
import json
import os

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)

HOST = '0.0.0.0' # 0.0.0.0 agar bisa diakses laptop lain
PORT = 8080
BUFFER_SIZE = 4096
RECV_DIR = 'received_files'

def start_server():
    os.makedirs(RECV_DIR, exist_ok=True)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((HOST, PORT))
        except OSError as e:
            logging.error(f"Port {PORT} digunakan aplikasi lain. Error: {e}")
            return
            
        # Single Thread: Antrean dibatasi 1 (menolak koneksi ganda bersamaan)
        server_socket.listen(1)
        
        local_ip = socket.gethostbyname(socket.gethostname())
        logging.info(f"Server SINGLE THREAD berjalan di IP: {local_ip} (Port {PORT})")
        logging.info("Menunggu koneksi dari SATU client (Client lain akan antre/ditolak)...")

        while True:
            try:
                # Blokir eksekusi program (Terkunci melayani client ini saja)
                client_socket, client_address = server_socket.accept()
                logging.info(f"Client connected dari {client_address}")
            except KeyboardInterrupt:
                logging.info("Server dihentikan manual.")
                break
                
            client_socket.settimeout(60.0) 
            
            with client_socket:
                try:
                    while True:
                        raw_header_len = recv_all(client_socket, 4)
                        if not raw_header_len:
                            logging.info(f"Client {client_address} disconnect")
                            break
                            
                        header_len = struct.unpack('>I', raw_header_len)[0]
                        header_bytes = recv_all(client_socket, header_len)
                        if not header_bytes: break
                            
                        header = json.loads(header_bytes.decode('utf-8'))
                        msg_type = header.get('type')
                        size = header.get('size')
                        
                        if msg_type == 'text':
                            payload = recv_all(client_socket, size)
                            if not payload: break
                            logging.info(f"Pesan teks dari {client_address}: {payload.decode('utf-8')}")
                            send_reply(client_socket, "Pesan teks berhasil diterima.")
                            
                        elif msg_type == 'file':
                            filename = header.get('filename')
                            filepath = os.path.join(RECV_DIR, filename)
                            logging.info(f"Mulai menerima file: {filename} ({size} bytes) dari {client_address}")
                            
                            received_bytes = 0
                            last_percent = 0
                            with open(filepath, 'wb') as f:
                                while received_bytes < size:
                                    chunk_size = min(BUFFER_SIZE, size - received_bytes)
                                    chunk = client_socket.recv(chunk_size)
                                    if not chunk: raise ConnectionResetError("Terputus saat transfer file.")
                                    f.write(chunk)
                                    received_bytes += len(chunk)
                                    
                                    percent = (received_bytes / size) * 100
                                    if percent >= last_percent + 10:
                                        print(f"[{client_address}] Progress Receive: {int(last_percent + 10)}%")
                                        last_percent += 10
                            logging.info(f"File {filename} berhasil diterima.")
                            send_reply(client_socket, f"File {filename} berhasil diterima oleh server.")
                            
                except Exception as e:
                    logging.error(f"Terjadi error: {e}")
                finally:
                    logging.info(f"Mengakhiri sesi untuk {client_address}. Siap melayani client antrean selanjutnya.")

def recv_all(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet: return None
        data.extend(packet)
    return data

def send_reply(sock, message):
    reply_bytes = message.encode('utf-8')
    header = json.dumps({'type': 'reply', 'size': len(reply_bytes)}).encode('utf-8')
    sock.sendall(struct.pack('>I', len(header)) + header + reply_bytes)

if __name__ == "__main__":
    start_server()
