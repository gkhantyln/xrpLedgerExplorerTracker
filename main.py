import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
from ttkthemes import ThemedStyle
import requests
from plyer import notification
from datetime import datetime

class XRPScanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XRP Ledger Explorer | Wallet Tracking Application")
        self.root.geometry("835x525")

        self.icon_image = tk.PhotoImage(file="xrp.png")
        root.tk.call('wm', 'iconphoto', root._w, self.icon_image)
        
        self.root.attributes('-topmost', True)
        self.root.resizable(False, False)
        
        # Adres ve Butonlar Çerçeveleri
        self.address_frame = ttk.Frame(root)
        self.address_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.transfer_frame = ttk.Frame(root)
        self.transfer_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # XRP Adresi Etiketi ve Giriş Alanı
        self.address_label = ttk.Label(self.address_frame, text="XRP Address:")
        self.address_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        
        self.address_entry = ttk.Entry(self.address_frame, width=50)
        self.address_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Başlat ve Durdur Butonları
        self.start_button = ttk.Button(self.address_frame, text="Start", command=self.start_request)
        self.start_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.stop_button = ttk.Button(self.address_frame, text="Stop", command=self.stop_request, state="disabled")
        self.stop_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Gelen Transferler ve Hata Logları Alanları
        self.transfer_label = ttk.Label(self.transfer_frame, text="Received XRP Transfers:")
        self.transfer_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.transfer_text = tk.Text(self.transfer_frame, width=100, height=15, font=("Courier", 10))
        self.transfer_text.grid(row=1, column=0, padx=5, pady=5)
        
        self.log_label = ttk.Label(self.transfer_frame, text="Error Logs / Reports:")
        self.log_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        self.log_text = tk.Text(self.transfer_frame, width=100, height=5, font=("Courier", 10))
        self.log_text.grid(row=3, column=0, padx=5, pady=5)
        
        # Butonlar
        self.clear_logs_button = ttk.Button(self.transfer_frame, text="Clear Error Logs / Reports", command=self.clear_logs)
        self.clear_logs_button.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        
        self.clear_transfers_button = ttk.Button(self.transfer_frame, text="Clear Incoming XRP Transfers", command=self.clear_transfers)
        self.clear_transfers_button.grid(row=4, column=0, padx=5, pady=5, sticky="e")

        self.style = ThemedStyle(self.root)
        self.style.theme_use('clearlooks')  # Modern bir görünüm için varsayılan tema
        
        self.last_transaction_hash = ""
        self.running = False
        self.interval = 5
        
    def start_request(self):
        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.log_text.insert(tk.END, "Request thread initiated.\n")
        self.root.after(0, self.check_transfers)
    
    def stop_request(self):
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
    def check_transfers(self):
        if not self.running:
            return
        
        address = self.address_entry.get()
        try:
            response = requests.get(f"https://api.xrpscan.com/api/v1/account/{address}/transactions")
            if response.status_code == 200:
                data = response.json()
                transactions = data.get("transactions", [])
                if transactions:
                    latest_transaction = transactions[0]
                    transaction_hash = latest_transaction.get("hash")
                    if transaction_hash != self.last_transaction_hash:
                        self.process_transaction_data(latest_transaction)
                        self.last_transaction_hash = transaction_hash
                    else:
                        self.log_text.insert(tk.END, "No new data found.\n")
            else:
                self.log_text.insert(tk.END, f"Error: Request failed. Status code: {response.status_code}\n")
        except Exception as e:
            self.log_text.insert(tk.END, f"Error: {str(e)}\n")
        
        self.root.after(self.interval * 1000, self.check_transfers)
    
    def process_transaction_data(self, data):
        amount = data.get("Amount", {}).get("value")
        currency = data.get("Amount", {}).get("currency")
        destination = data.get("Destination")
        sender = data.get("Account")
        transaction_hash = data.get("hash")
        timestamp = data.get("date")
        
        # Tarih ve saat bilgisini istenen formatta gösterme
        formatted_timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%m/%d/%Y %H:%M")
        
        formatted_transfer = f"{formatted_timestamp} | {amount} {currency} | {destination} > {sender} | {transaction_hash}\n"
        self.transfer_text.insert(tk.END, formatted_transfer)
        
        title = "New Transfer"
        message = f"A new transfer has arrived: {amount} {currency} ({transaction_hash})"
        notification.notify(title=title, message=message, app_name="XRP Ledger Explorer | Wallet Tracking Application", timeout=10)
    
    def clear_transfers(self):
        self.transfer_text.delete("1.0", tk.END)
        
    def clear_logs(self):
        self.log_text.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = XRPScanApp(root)
    root.mainloop()
