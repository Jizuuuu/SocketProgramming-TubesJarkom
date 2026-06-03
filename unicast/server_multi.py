import socket
import logging
import struct
import json
import os
import threading

# Konfigurasi Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(threadName)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)

HOST = '0.0.0.0' # Ubah menjadi 0.0.0.0 agar bisa diakses laptop lain
PORT = 8080
BUFFER_SIZE = 4096
RECV_DIR = 'received_files'

def handle_client(client_socket, client_address):
    """Fungsi yang akan dijalankan oleh setiap thread untuk melayani satu client."""
    # Set timeout ke client agar thread tidak gantung (hang) selamanya jika terputus
    client_socket.settimeout(60.0)
    
    with client_socket:
        try:
            while True:
                # 1. Terima panjang header (4 bytes)
                raw_header_len = recv_all(client_socket, 4)
                if not raw_header_len:
                    logging.info(f"Client {client_address} disconnect")
                    break
                    
                header_len = struct.unpack('>I', raw_header_len)[0]
                
                # 2. Terima header JSON
                header_bytes = recv_all(client_socket, header_len)
                if not header_bytes:
                    logging.error(f"Koneksi dari {client_address} terputus saat menerima header.")
                    break
                    
                header = json.loads(header_bytes.decode('utf-8'))
                msg_type = header.get('type')
                size = header.get('size')
                
                # 3. Tangani sesuai tipe payload
                if msg_type == 'text':
                    payload = recv_all(client_socket, size)
                    if not payload:
                        break
                    message = payload.decode('utf-8')
                    logging.info(f"Pesan teks dari {client_address}: {message}")
                    
                    # Balasan Text
                    reply = "Pesan teks berhasil diterima."
                    send_reply(client_socket, reply)
                    
                elif msg_type == 'file':
                    filename = header.get('filename')
                    # Ubah nama file dengan menempelkan port address agar tidak bentrok jika banyak client kirim file bernama sama
                    safe_filename = f"{client_address[1]}_{filename}"
                    filepath = os.path.join(RECV_DIR, safe_filename)
                    
                    logging.info(f"Mulai menerima file: {safe_filename} ({size} bytes) dari {client_address}")
                    
                    received_bytes = 0
                    last_percent = 0
                    
                    with open(filepath, 'wb') as f:
                        while received_bytes < size:
                            chunk_size = min(BUFFER_SIZE, size - received_bytes)
                            chunk = client_socket.recv(chunk_size)
                            if not chunk:
                                raise ConnectionResetError("Koneksi terputus saat transfer file.")
                            f.write(chunk)
                            received_bytes += len(chunk)
                            
                            # Hitung persentase
                            percent = (received_bytes / size) * 100
                            if percent >= last_percent + 10:
                                print(f"[{client_address}] Progress Receive: {int(last_percent + 10)}%")
                                last_percent += 10
                                
                    logging.info(f"File {safe_filename} berhasil diterima dari {client_address}")
                    
                    # Balasan File
                    reply = f"File {filename} berhasil diterima oleh server."
                    send_reply(client_socket, reply)
                else:
                    logging.warning(f"Tipe pesan tidak dikenal dari {client_address}")
                    
        except ConnectionResetError:
            logging.warning(f"Koneksi terputus dari {client_address} secara tiba-tiba.")
        except socket.timeout:
            logging.warning(f"Timeout saat menunggu data dari {client_address}.")
        except Exception as e:
            logging.error(f"Terjadi error pada {client_address}: {e}")
        finally:
            logging.info(f"Mengakhiri sesi untuk {client_address}.")

def start_server():
    os.makedirs(RECV_DIR, exist_ok=True)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((HOST, PORT))
        except OSError as e:
            logging.error(f"Port {PORT} digunakan aplikasi lain. Error: {e}")
            return
            
        # Ubah backlog (antrean) menjadi angka lebih besar, misalnya 5
        server_socket.listen(5)
        
        # Deteksi IP lokal Windows untuk mempermudah Client
        local_ip = socket.gethostbyname(socket.gethostname())
        logging.info(f"Server Multithread berjalan di IP: {local_ip} (Port {PORT})")
        logging.info("Menunggu koneksi dari banyak client...")

        while True:
            try:
                client_socket, client_address = server_socket.accept()
                logging.info(f"Koneksi baru masuk dari {client_address}")
                
                # Membuat thread baru untuk menangani client tersebut
                client_thread = threading.Thread(
                    target=handle_client,
                    args=(client_socket, client_address),
                    name=f"Thread-{client_address[1]}",
                    daemon=True # Daemon thread otomatis tertutup bila main program berhenti
                )
                client_thread.start()
                
                # Active count dikurangi 1 karena tidak menghitung main_thread
                logging.info(f"Jumlah client terhubung: {threading.active_count() - 1}")
                
            except KeyboardInterrupt:
                logging.info("Server dihentikan manual.")
                break
            except Exception as e:
                logging.error(f"Error saat menerima koneksi: {e}")

def recv_all(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def send_reply(sock, message):
    reply_bytes = message.encode('utf-8')
    header = json.dumps({'type': 'reply', 'size': len(reply_bytes)}).encode('utf-8')
    header_len = struct.pack('>I', len(header))
    
    sock.sendall(header_len + header + reply_bytes)

if __name__ == "__main__":
    start_server()
