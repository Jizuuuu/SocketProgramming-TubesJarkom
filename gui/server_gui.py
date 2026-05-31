import tkinter as tk
from tkinter import scrolledtext
import socket
import threading
import sys
import os
import struct
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.config import TCP_HOST, TCP_PORT, BUFFER_SIZE

class ServerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Server TCP Chat & File Transfer")
        self.master.geometry("500x550")
        
        self.server_sock = None
        self.active_clients = []
        self.is_running = False
        
        self.status_lbl = tk.Label(master, text="Server Offline", fg="red", font=("Arial", 10, "bold"))
        self.status_lbl.pack(pady=5)
        
        self.start_btn = tk.Button(master, text="Start Server", command=self.start_server)
        self.start_btn.pack(pady=5)
        
        tk.Label(master, text="Daftar Client Aktif:").pack()
        self.client_listbox = tk.Listbox(master, height=5, width=50)
        self.client_listbox.pack(pady=5)
        
        tk.Label(master, text="Log Aktivitas:").pack()
        self.log_area = scrolledtext.ScrolledText(master, state='disabled', width=55, height=15, font=("Arial", 10))
        self.log_area.pack(pady=5)
        
    def append_log(self, msg):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')
        
    def update_client_list(self):
        self.client_listbox.delete(0, tk.END)
        for c in self.active_clients:
            self.client_listbox.insert(tk.END, str(c))
            
    def start_server(self):
        if self.is_running: return
        
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind(('0.0.0.0', TCP_PORT)) # 0.0.0.0 agar bisa diakses LAN
        self.server_sock.listen(5)
        
        self.is_running = True
        local_ip = socket.gethostbyname(socket.gethostname())
        self.status_lbl.config(text=f"Server Online (IP: {local_ip}:{TCP_PORT})", fg="green")
        self.start_btn.config(state=tk.DISABLED)
        self.append_log("[INFO] Server dihidupkan. Menunggu client...")
        
        os.makedirs("gui_received_files", exist_ok=True)
        threading.Thread(target=self.accept_clients, daemon=True).start()
        
    def accept_clients(self):
        while self.is_running:
            try:
                client_sock, client_addr = self.server_sock.accept()
                self.active_clients.append(client_addr)
                self.update_client_list()
                self.append_log(f"[INFO] Client masuk: {client_addr}")
                
                threading.Thread(target=self.handle_client, args=(client_sock, client_addr), daemon=True).start()
            except Exception:
                break
                
    def handle_client(self, client_sock, client_addr):
        with client_sock:
            try:
                while True:
                    raw_len = client_sock.recv(4)
                    if not raw_len: break
                    header_len = struct.unpack('>I', raw_len)[0]
                    
                    header_bytes = client_sock.recv(header_len)
                    header = json.loads(header_bytes.decode('utf-8'))
                    msg_type = header.get('type')
                    size = header.get('size')
                    
                    if msg_type == 'text':
                        payload = client_sock.recv(size)
                        msg = payload.decode('utf-8')
                        self.append_log(f"[{client_addr} - TEKS]: {msg}")
                        
                        reply = "Pesan teks diterima server."
                        self.send_reply(client_sock, reply)
                        
                    elif msg_type == 'file':
                        filename = f"{client_addr[1]}_{header.get('filename')}"
                        filepath = os.path.join("gui_received_files", filename)
                        self.append_log(f"[{client_addr} - FILE]: Menerima {filename} ({size} bytes)...")
                        
                        received = 0
                        with open(filepath, 'wb') as f:
                            while received < size:
                                chunk = client_sock.recv(min(BUFFER_SIZE, size - received))
                                if not chunk: break
                                f.write(chunk)
                                received += len(chunk)
                        
                        self.append_log(f"[INFO] File {filename} berhasil disimpan.")
                        reply = "File berhasil diterima server."
                        self.send_reply(client_sock, reply)
                        
            except Exception as e:
                self.append_log(f"[ERROR] {client_addr}: {e}")
            finally:
                if client_addr in self.active_clients:
                    self.active_clients.remove(client_addr)
                    self.update_client_list()
                self.append_log(f"[INFO] Client {client_addr} terputus.")
                
    def send_reply(self, sock, msg):
        try:
            payload = msg.encode('utf-8')
            header = json.dumps({'type': 'reply', 'size': len(payload)}).encode('utf-8')
            sock.sendall(struct.pack('>I', len(header)) + header + payload)
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
