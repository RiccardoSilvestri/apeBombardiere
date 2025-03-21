import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import os
from tkinter import Label
from PIL import Image, ImageTk

from styles import COLORS, configure_styles
from ui_components import (
    create_url_section, 
    create_headers_section, 
    create_body_section, 
    create_buttons_section, 
    create_json_view
)

class APIClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Ape bombardiere")
        self.root.geometry("1200x750")
        self.root.configure(bg=COLORS["background"])
        
        self.configure_styles()
        self.logo_image = Image.open("logo.png") 
        self.logo_image = self.logo_image.resize((70, 70)) 
        self.logo_tk = ImageTk.PhotoImage(self.logo_image)
        self.headers_entries = []
        self.method_var = tk.StringVar(value="GET")
        self.body_type_var = tk.StringVar(value="JSON")
        self.response_status = tk.StringVar(value="Status: Nessuna richiesta inviata")
        self.verify_ssl = tk.BooleanVar(value=True)
        
        self.create_ui()
        
        self.update_body_visibility()

    def configure_styles(self):
        style = ttk.Style()
        configure_styles(style)

    def create_ui(self):
        main_container = ttk.Frame(self.root, style="TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)


        title_frame = ttk.Frame(main_container, style="TFrame")
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(title_frame, text="Ape Bombardiere", 
                               font=("Segoe UI", 16, "bold"), foreground=COLORS["primary"],
                               style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        panel_frame = ttk.Frame(main_container, style="TFrame")
        panel_frame.pack(fill=tk.BOTH, expand=True)
        
        self.request_frame = ttk.Frame(panel_frame, style="Card.TFrame")
        self.request_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        request_header = ttk.Frame(self.request_frame, style="TFrame")
        request_header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(request_header, text="Richiesta", style="Header.TLabel").pack(side=tk.LEFT)
        logo_label = ttk.Label(title_frame, image=self.logo_tk, background=COLORS["background"])
        logo_label.pack(side=tk.LEFT, padx=(0, 10)) 
        create_url_section(self)
        create_headers_section(self)
        create_body_section(self)
        create_buttons_section(self)
        
        self.response_frame = ttk.Frame(panel_frame, style="Card.TFrame")
        self.response_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        response_header = ttk.Frame(self.response_frame, style="TFrame")
        response_header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(response_header, text="Risposta", style="Header.TLabel").pack(side=tk.LEFT)
        
        status_frame = ttk.Frame(self.response_frame)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(status_frame, textvariable=self.response_status, style="Status.TLabel").pack(anchor=tk.W)
        
        create_json_view(self)
        
        response_headers_frame = ttk.LabelFrame(self.response_frame, text="Headers")
        response_headers_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.response_headers_text = scrolledtext.ScrolledText(response_headers_frame, height=4, 
                                                             font=("Consolas", 10))
        self.response_headers_text.pack(fill=tk.X, padx=5, pady=5)
        
        response_body_frame = ttk.LabelFrame(self.response_frame, text="Body")
        response_body_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.response_body_text = scrolledtext.ScrolledText(response_body_frame, 
                                                          font=("Consolas", 10))
        self.response_body_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def update_body_visibility(self):
        method = self.method_var.get()
        if method in ["GET", "DELETE", "HEAD"]:
            self.body_frame.pack_forget()
        else:
            self.body_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def update_json_view(self):
        for item in self.json_treeview.get_children():
            self.json_treeview.delete(item)
        try:
            json_data = json.loads(self.body_text.get("1.0", tk.END).strip())
            
            def insert_json_data(parent, data):
                if isinstance(data, dict):
                    for key, value in data.items():
                        parent_id = self.json_treeview.insert(parent, "end", text=key)
                        insert_json_data(parent_id, value)
                elif isinstance(data, list):
                    for i, item in enumerate(data):
                        parent_id = self.json_treeview.insert(parent, "end", text=f"Item {i}")
                        insert_json_data(parent_id, item)
                else:
                    self.json_treeview.insert(parent, "end", text=str(data))
            
            insert_json_data("", json_data)
        except json.JSONDecodeError:
            self.json_treeview.insert("", "end", text="JSON non valido")

    def save_config(self):
        config = {
            "url": self.url_entry.get(),
            "method": self.method_var.get(),
            "headers": {key_entry.get(): value_entry.get() for key_entry, value_entry in self.headers_entries if key_entry.get() and value_entry.get()},
            "body_type": self.body_type_var.get(),
            "body": self.body_text.get("1.0", tk.END).strip()
        }
        try:
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("Salvataggio", "Configurazione salvata con successo!")
            self.update_json_view()  
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante il salvataggio:\n{str(e)}")

    def load_config(self):
        try:
            if not os.path.exists("config.json"):
                messagebox.showinfo("Informazione", "Nessun file di configurazione trovato.")
                return
                
            with open("config.json", "r") as f:
                config = json.load(f)
            
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, config.get("url", ""))
            
            self.method_var.set(config.get("method", "GET"))
            
            for header_row in self.headers_frame.winfo_children():
                if isinstance(header_row, ttk.Frame) and header_row != self.headers_frame.winfo_children()[0]:
                    header_row.destroy()
            self.headers_entries.clear()
            
            headers = config.get("headers", {})
            for key, value in headers.items():
                self.add_header_field() 
                self.headers_entries[-1][0].insert(0, key) 
                self.headers_entries[-1][1].insert(0, value) 
            
            self.body_type_var.set(config.get("body_type", "JSON"))
            
            self.body_text.delete("1.0", tk.END)
            self.body_text.insert(tk.END, config.get("body", ""))
            
            messagebox.showinfo("Caricamento", "Configurazione caricata con successo!")
            self.update_json_view()
            self.update_body_visibility()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante il caricamento:\n{str(e)}")

    def send_request(self):
        try:
            url = self.url_entry.get()
            if not url:
                messagebox.showwarning("Attenzione", "Inserisci un URL valido.")
                return
                
            method = self.method_var.get()
            headers = {key_entry.get(): value_entry.get() 
                      for key_entry, value_entry in self.headers_entries 
                      if key_entry.get() and value_entry.get()}

            body_type = self.body_type_var.get()
            data = None
            json_data = None
            
            if method not in ["GET", "DELETE", "HEAD"]:
                if body_type == "JSON":
                    try:
                        body_content = self.body_text.get("1.0", tk.END).strip()
                        if body_content:
                            json_data = json.loads(body_content)
                            headers.setdefault("Content-Type", "application/json")
                    except json.JSONDecodeError as e:
                        messagebox.showerror("Errore JSON", f"JSON non valido: {e}")
                        return
                elif body_type == "x-www-form-urlencoded":
                    data = {}
                    body_content = self.body_text.get("1.0", tk.END).strip()
                    if body_content:
                        for pair in body_content.split('&'):
                            if '=' in pair:
                                key, val = pair.split('=', 1)
                                data[key.strip()] = val.strip()
                    headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
                else:
                    data = self.body_text.get("1.0", tk.END).strip()
                    headers.setdefault("Content-Type", "text/plain")

            self.response_status.set("Status: Invio richiesta in corso...")
            self.root.update_idletasks()
            
            response = requests.request(
                method, 
                url,
                headers=headers,
                json=json_data,
                data=data,
                verify=self.verify_ssl.get()
            )

            status_text = f"Status: {response.status_code} {response.reason}"
            self.response_status.set(status_text)
            
            self.response_headers_text.delete("1.0", tk.END)
            self.response_headers_text.insert(tk.END, "\n".join(
                [f"{k}: {v}" for k, v in response.headers.items()]
            ))
            
            self.response_body_text.delete("1.0", tk.END)
            try:
                json_data = response.json()
                formatted_json = json.dumps(json_data, indent=2)
                self.response_body_text.insert(tk.END, formatted_json)
                
                for item in self.json_treeview.get_children():
                    self.json_treeview.delete(item)
                    
                def insert_json_data(parent, data):
                    if isinstance(data, dict):
                        for key, value in data.items():
                            parent_id = self.json_treeview.insert(parent, "end", text=key)
                            insert_json_data(parent_id, value)
                    elif isinstance(data, list):
                        for i, item in enumerate(data):
                            parent_id = self.json_treeview.insert(parent, "end", text=f"Item {i}")
                            insert_json_data(parent_id, item)
                    else:
                        self.json_treeview.insert(parent, "end", text=str(data))
                
                insert_json_data("", json_data)
            except json.JSONDecodeError:
                self.response_body_text.insert(tk.END, response.text)

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante la richiesta:\n{str(e)}")
            self.response_status.set("Status: Errore durante la richiesta")

    def add_header_field(self):
        header_row = ttk.Frame(self.headers_frame)
        header_row.pack(fill=tk.X, pady=2, padx=5)

        key_entry = ttk.Entry(header_row, width=30, font=("Segoe UI", 10))
        key_entry.pack(side=tk.LEFT, padx=5)
        key_entry.insert(0, "")

        value_entry = ttk.Entry(header_row, width=30, font=("Segoe UI", 10))
        value_entry.pack(side=tk.LEFT, padx=5)
        value_entry.insert(0, "")

        remove_btn = ttk.Button(header_row, text="✕", width=3, 
                               command=lambda: self.remove_header_field(header_row))
        remove_btn.pack(side=tk.LEFT, padx=5)

        self.headers_entries.append((key_entry, value_entry))
        
        return key_entry, value_entry

    def remove_header_field(self, header_row):
        for i, (key_entry, value_entry) in enumerate(self.headers_entries):
            if key_entry.master == header_row:
                self.headers_entries.pop(i)
                break
        
        header_row.destroy()

    def format_json(self):
        try:
            body_content = self.body_text.get("1.0", tk.END).strip()
            if not body_content:
                return
                
            data = json.loads(body_content)
            self.body_text.delete("1.0", tk.END)
            self.body_text.insert(tk.END, json.dumps(data, indent=2))
            self.update_json_view()
        except json.JSONDecodeError as e:
            messagebox.showerror("Errore JSON", f"JSON non valido: {e}")

    def on_body_text_change(self, event=None):
        if self.body_type_var.get() == "JSON":
            self.update_json_view()