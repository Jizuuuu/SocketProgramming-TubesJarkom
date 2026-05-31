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

PORT = 8080
BUFFER_SIZE = 4096
SEND_DIR = 'send_files'

def start_client():
    server_ip = input("Masukkan IP Server (tekan Enter untuk 127.0.0.1/localhost): ").strip()
    host = server_ip if server_ip else '127.0.0.1'
    
    os.makedirs(SEND_DIR, exist_ok=True)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((host, PORT))
            logging.info(f"Berhasil terhubung ke server {host}:{PORT}")
        except ConnectionRefusedError:
            logging.error("Koneksi ditolak. Pastikan server sudah berjalan.")
            return
        except Exception as e:
            logging.error(f"Gagal terhubung: {e}")
            return

        while True:
            try:
                print("\n" + "="*50)
                print("Pilih aksi:")
                print("1. Kirim Teks")
                print("2. Kirim File")
                print("3. Exit")
                pilihan = input("> ")
                
                if pilihan == '3' or pilihan.lower() == 'exit':
                    logging.info("Menutup koneksi...")
                    break
                    
                if pilihan == '1':
                    print("Masukkan pesan yang ingin dikirim:")
                    pesan = input("> ")
                    if not pesan:
                        continue
                    
                    payload = pesan.encode('utf-8')
                    header = json.dumps({'type': 'text', 'size': len(payload)}).encode('utf-8')
                    header_len = struct.pack('>I', len(header))
                    
                    client_socket.sendall(header_len + header + payload)
                    logging.info("Message sent")
                    
                    # Terima balasan
                    terima_balasan(client_socket)

                elif pilihan == '2':
                    print(f"Pastikan file berada di direktori '{SEND_DIR}/'")
                    print("Masukkan nama file beserta ekstensinya (contoh: gambar.jpg, dokumen.pdf):")
                    filename = input("> ")
                    filepath = os.path.join(SEND_DIR, filename)
                    
                    if not os.path.isfile(filepath):
                        logging.error(f"File tidak ditemukan: {filepath}")
                        continue
                        
                    filesize = os.path.getsize(filepath)
                    header = json.dumps({
                        'type': 'file', 
                        'filename': filename, 
                        'size': filesize
                    }).encode('utf-8')
                    header_len = struct.pack('>I', len(header))
                    
                    # Kirim Header
                    client_socket.sendall(header_len + header)
                    
                    # Kirim File dalam potongan (chunk)
                    logging.info(f"Mulai mengirim file: {filename} ({filesize} bytes)")
                    sent_bytes = 0
                    last_percent = 0
                    
                    with open(filepath, 'rb') as f:
                        while sent_bytes < filesize:
                            chunk = f.read(BUFFER_SIZE)
                            if not chunk:
                                break
                            client_socket.sendall(chunk)
                            sent_bytes += len(chunk)
                            
                            # Hitung persentase progres
                            percent = (sent_bytes / filesize) * 100
                            if percent >= last_percent + 10:
                                print(f"Progress Send: {int(last_percent + 10)}%")
                                last_percent += 10
                                
                    logging.info("File transferred")
                    
                    # Terima balasan
                    terima_balasan(client_socket)
                    
                else:
                    print("Pilihan tidak valid.")
                
            except ConnectionResetError:
                logging.error("Koneksi terputus dari server.")
                break
            except Exception as e:
                logging.error(f"Terjadi error: {e}")
                break

def terima_balasan(sock):
    """Menerima konfirmasi balasan dari server."""
    raw_header_len = recv_all(sock, 4)
    if not raw_header_len:
        logging.warning("Koneksi ditutup oleh server saat menunggu balasan.")
        return
        
    header_len = struct.unpack('>I', raw_header_len)[0]
    header_bytes = recv_all(sock, header_len)
    if not header_bytes:
        return
        
    header = json.loads(header_bytes.decode('utf-8'))
    size = header.get('size')
    
    payload = recv_all(sock, size)
    if payload:
        logging.info(f"Balasan dari server: {payload.decode('utf-8')}")

def recv_all(sock, n):
    """Fungsi helper untuk menerima persis n bytes data."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

if __name__ == "__main__":
    start_client()
