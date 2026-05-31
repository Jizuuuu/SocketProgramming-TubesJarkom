import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import socket
import threading
import sys
import os
import struct
import json

# Tambahkan parent directory ke sys.path agar bisa import common module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.config import TCP_HOST, TCP_PORT, BUFFER_SIZE

class ClientGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Client TCP Chat & File Transfer")
        self.master.geometry("500x550")
        
        self.sock = None
        self.connected = False
        
        # UI Elements
        self.status_lbl = tk.Label(master, text="Status Koneksi: Disconnected", fg="red", font=("Arial", 10, "bold"))
        self.status_lbl.pack(pady=5)
        
        frame_conn = tk.Frame(master)
        frame_conn.pack(pady=5)
        tk.Label(frame_conn, text="IP Server:").grid(row=0, column=0, padx=5)
        self.ip_entry = tk.Entry(frame_conn, width=15)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.grid(row=0, column=1, padx=5)
        
        self.connect_btn = tk.Button(frame_conn, text="Connect", command=self.connect_server)
        self.connect_btn.grid(row=0, column=2, padx=5)
        
        self.chat_area = scrolledtext.ScrolledText(master, state='disabled', width=55, height=18, font=("Arial", 10))
        self.chat_area.pack(pady=10)
        
        frame_input = tk.Frame(master)
        frame_input.pack(pady=5)
        
        self.msg_entry = tk.Entry(frame_input, width=40, font=("Arial", 10))
        self.msg_entry.grid(row=0, column=0, padx=5)
        self.msg_entry.bind("<Return>", lambda e: self.send_text())
        
        self.send_btn = tk.Button(frame_input, text="Kirim Teks", command=self.send_text)
        self.send_btn.grid(row=0, column=1)
        
        self.file_btn = tk.Button(master, text="Pilih & Kirim File", command=self.send_file)
        self.file_btn.pack(pady=10)
        
    def append_log(self, msg):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, msg + "\n")
        self.chat_area.see(tk.END)
        self.chat_area.config(state='disabled')
        
    def connect_server(self):
        if self.connected:
            return
            
        host = self.ip_entry.get().strip()
        if not host:
            host = "127.0.0.1"
            
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, TCP_PORT))
            self.connected = True
            self.status_lbl.config(text=f"Status Koneksi: Connected ke {host}:{TCP_PORT}", fg="green")
            self.connect_btn.config(state=tk.DISABLED)
            self.ip_entry.config(state=tk.DISABLED)
            self.append_log(f"[INFO] Berhasil terhubung ke server {host}.")
            
            # Start listener thread
            threading.Thread(target=self.listen_server, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Gagal terhubung: {e}")
            
    def listen_server(self):
        while self.connected:
            try:
                raw_len = self.sock.recv(4)
                if not raw_len: break
                header_len = struct.unpack('>I', raw_len)[0]
                
                # Helper untuk GUI recv_all bisa disederhanakan
                header_bytes = self.sock.recv(header_len)
                header = json.loads(header_bytes.decode('utf-8'))
                
                if header.get('type') == 'reply':
                    payload = self.sock.recv(header.get('size'))
                    self.append_log(f"[SERVER]: {payload.decode('utf-8')}")
            except Exception:
                break
        
        self.connected = False
        self.status_lbl.config(text="Status Koneksi: Disconnected", fg="red")
        self.connect_btn.config(state=tk.NORMAL)
        self.ip_entry.config(state=tk.NORMAL)
        self.append_log("[INFO] Koneksi terputus dari server.")
        
    def send_text(self):
        if not self.connected:
            messagebox.showwarning("Warning", "Silakan connect terlebih dahulu!")
            return
            
        msg = self.msg_entry.get()
        if not msg: return
        
        try:
            payload = msg.encode('utf-8')
            header = json.dumps({'type': 'text', 'size': len(payload)}).encode('utf-8')
            header_len = struct.pack('>I', len(header))
            self.sock.sendall(header_len + header + payload)
            
            self.append_log(f"[SAYA]: {msg}")
            self.msg_entry.delete(0, tk.END)
        except Exception as e:
            self.append_log(f"[ERROR] Gagal kirim teks: {e}")
            
    def send_file(self):
        if not self.connected:
            messagebox.showwarning("Warning", "Silakan connect terlebih dahulu!")
            return
            
        filepath = filedialog.askopenfilename(title="Pilih file untuk dikirim")
        if not filepath: return
        
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        
        try:
            header = json.dumps({'type': 'file', 'filename': filename, 'size': filesize}).encode('utf-8')
            header_len = struct.pack('>I', len(header))
            self.sock.sendall(header_len + header)
            
            self.append_log(f"[INFO] Mulai mengirim file {filename} ({filesize} bytes)...")
            
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(BUFFER_SIZE)
                    if not chunk: break
                    self.sock.sendall(chunk)
                    
            self.append_log(f"[INFO] File {filename} berhasil dikirim.")
        except Exception as e:
            self.append_log(f"[ERROR] Gagal kirim file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()
