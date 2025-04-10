import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import os
from PIL import Image, ImageTk

from styles import COLORS, configure_styles
from ui_components import (
    create_url_section, 
    create_headers_section, 
    create_body_section, 
    create_buttons_section, 
    create_json_view
)

CONFIG_FILE = "config.json"

class APIClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Ape bombardiere")
        self.root.geometry("1400x750")
        self.root.configure(bg=COLORS["background"])

        self.configure_styles()
        self.logo_image = Image.open("logo.png").resize((70, 70))
        self.logo_tk = ImageTk.PhotoImage(self.logo_image)

        self.headers_entries = []
        self.method_var = tk.StringVar(value="GET")
        self.body_type_var = tk.StringVar(value="JSON")
        self.response_status = tk.StringVar(value="Status: Nessuna richiesta inviata")
        self.verify_ssl = tk.BooleanVar(value=True)
        self.selected_config = tk.StringVar()
        self.configs = {}

        self.create_ui()
        self.update_body_visibility()
        self.load_all_configs()

    def configure_styles(self):
        style = ttk.Style()
        configure_styles(style)

    def create_ui(self):
        main_container = ttk.Frame(self.root, style="TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        title_frame = ttk.Frame(main_container, style="TFrame")
        title_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(title_frame, text="Ape Bombardiere", font=("Segoe UI", 16, "bold"),
                  foreground=COLORS["primary"], style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Label(title_frame, image=self.logo_tk, background=COLORS["background"]).pack(side=tk.LEFT, padx=(10, 0))

        panel_frame = ttk.Frame(main_container, style="TFrame")
        panel_frame.pack(fill=tk.BOTH, expand=True)

        self.request_frame = ttk.Frame(panel_frame, style="Card.TFrame")
        self.request_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        request_header = ttk.Frame(self.request_frame, style="TFrame")
        request_header.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(request_header, text="Richiesta", style="Header.TLabel").pack(side=tk.LEFT)

        create_url_section(self)
        create_headers_section(self)
        create_body_section(self)
        self.create_buttons_section_custom()

        self.response_frame = ttk.Frame(panel_frame, style="Card.TFrame")
        self.response_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        response_header = ttk.Frame(self.response_frame, style="TFrame")
        response_header.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(response_header, text="Risposta", style="Header.TLabel").pack(side=tk.LEFT)

        status_frame = ttk.Frame(self.response_frame)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(status_frame, textvariable=self.response_status, style="Status.TLabel").pack(anchor=tk.W)

        create_json_view(self)

        response_headers_frame = ttk.LabelFrame(self.response_frame, text="Headers")
        response_headers_frame.pack(fill=tk.X, padx=10, pady=5)
        self.response_headers_text = scrolledtext.ScrolledText(response_headers_frame, height=4, font=("Consolas", 10))
        self.response_headers_text.pack(fill=tk.X, padx=5, pady=5)

        response_body_frame = ttk.LabelFrame(self.response_frame, text="Body")
        response_body_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.response_body_text = scrolledtext.ScrolledText(response_body_frame, font=("Consolas", 10))
        self.response_body_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.create_config_panel(panel_frame)

    def create_buttons_section_custom(self):
        button_frame = ttk.Frame(self.request_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Checkbutton(button_frame, text="Verifica SSL", variable=self.verify_ssl).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Formatta JSON", command=self.format_json, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Invia Richiesta", command=self.send_request, style="Success.TButton").pack(side=tk.LEFT, padx=5)

        # Tasto Bombarda
        ttk.Button(button_frame, text="Bombarda", command=self.bombarda_config, style="Error.TButton").pack(side=tk.LEFT, padx=5)

    def create_config_panel(self, parent):
        config_panel = ttk.Frame(parent, style="Card.TFrame")
        config_panel.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(config_panel, text="Configurazioni", style="Header.TLabel").pack(padx=10, pady=(10, 0))

        self.config_listbox = tk.Listbox(config_panel, height=15)
        self.config_listbox.pack(padx=10, pady=5, fill=tk.Y, expand=True)
        self.config_listbox.bind("<<ListboxSelect>>", self.on_config_select)

        ttk.Entry(config_panel, textvariable=self.selected_config).pack(padx=10, pady=(5, 0), fill=tk.X)

        ttk.Button(config_panel, text="Salva", command=self.save_config).pack(padx=10, pady=(5, 0), fill=tk.X)
        ttk.Button(config_panel, text="Carica", command=self.load_selected_config).pack(padx=10, pady=5, fill=tk.X)
        ttk.Button(config_panel, text="Elimina", command=self.delete_config).pack(padx=10, pady=5, fill=tk.X)

    def save_config(self):
        name = self.selected_config.get().strip()
        if not name:
            messagebox.showwarning("Attenzione", "Inserisci un nome per la configurazione.")
            return

        config = {
            "url": self.url_entry.get().strip(),
            "method": self.method_var.get(),
            "headers": {k.get(): v.get() for k, v in self.headers_entries if k.get() and v.get()},
            "body_type": self.body_type_var.get(),
            "body": self.body_text.get("1.0", tk.END).strip()
        }

        self.configs[name] = config
        self.write_configs()
        self.load_all_configs()
        messagebox.showinfo("Salvataggio", f"Configurazione '{name}' salvata.")

    def load_selected_config(self):
        selected = self.config_listbox.curselection()
        if not selected:
            return
        name = self.config_listbox.get(selected[0])
        self.selected_config.set(name)
        self.load_config(name)

    def load_config(self, name):
        if name not in self.configs:
            return
        config = self.configs[name]
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, config.get("url", "").strip())

        self.method_var.set(config.get("method", "GET"))

        for header_row in self.headers_frame.winfo_children()[1:]:
            header_row.destroy()
        self.headers_entries.clear()

        for key, value in config.get("headers", {}).items():
            self.add_header_field()
            self.headers_entries[-1][0].insert(0, key)
            self.headers_entries[-1][1].insert(0, value)

        self.body_type_var.set(config.get("body_type", "JSON"))
        self.body_text.delete("1.0", tk.END)
        self.body_text.insert(tk.END, config.get("body", ""))

        self.update_body_visibility()
        self.update_json_view()

    def delete_config(self):
        selected = self.config_listbox.curselection()
        if not selected:
            return
        name = self.config_listbox.get(selected[0])
        if messagebox.askyesno("Conferma", f"Eliminare la configurazione '{name}'?"):
            self.configs.pop(name, None)
            self.write_configs()
            self.load_all_configs()

    def load_all_configs(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.configs = json.load(f)
            except Exception:
                self.configs = {}
        else:
            self.configs = {}

        self.config_listbox.delete(0, tk.END)
        for name in self.configs:
            self.config_listbox.insert(tk.END, name)

    def write_configs(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.configs, f, indent=4)

    def on_config_select(self, event):
        selection = self.config_listbox.curselection()
        if selection:
            name = self.config_listbox.get(selection[0])
            self.selected_config.set(name)

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
            self.insert_json_data("", json_data)
        except json.JSONDecodeError:
            self.json_treeview.insert("", "end", text="JSON non valido")

    def insert_json_data(self, parent, data):
        if isinstance(data, dict):
            for key, value in data.items():
                parent_id = self.json_treeview.insert(parent, "end", text=key)
                self.insert_json_data(parent_id, value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                parent_id = self.json_treeview.insert(parent, "end", text=f"Item {i}")
                self.insert_json_data(parent_id, item)
        else:
            self.json_treeview.insert(parent, "end", text=str(data))

    def send_request(self):
        try:
            url = self.url_entry.get().strip()
            if not url:
                messagebox.showwarning("Attenzione", "Inserisci un URL valido.")
                return

            method = self.method_var.get()
            headers = {k.get(): v.get() for k, v in self.headers_entries if k.get() and v.get()}
            body_type = self.body_type_var.get()
            data = None
            json_data = None

            if method not in ["GET", "DELETE", "HEAD"]:
                body_content = self.body_text.get("1.0", tk.END).strip()
                if body_type == "JSON":
                    if body_content:
                        json_data = json.loads(body_content)
                        headers.setdefault("Content-Type", "application/json")
                elif body_type == "x-www-form-urlencoded":
                    data = {}
                    if body_content:
                        for pair in body_content.split('&'):
                            if '=' in pair:
                                k, v = pair.split('=', 1)
                                data[k.strip()] = v.strip()
                    headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
                else:
                    data = body_content
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

            self.response_status.set(f"Status: {response.status_code} {response.reason}")

            self.response_headers_text.delete("1.0", tk.END)
            self.response_headers_text.insert(tk.END, "\n".join(f"{k}: {v}" for k, v in response.headers.items()))

            self.response_body_text.delete("1.0", tk.END)
            try:
                response_json = response.json()
                formatted_json = json.dumps(response_json, indent=2)
                self.response_body_text.insert(tk.END, formatted_json)
                self.update_json_view_with_data(response_json)
            except Exception:
                self.response_body_text.insert(tk.END, response.text)

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante la richiesta:\n{str(e)}")
            self.response_status.set("Status: Errore durante la richiesta")

    def update_json_view_with_data(self, data):
        for item in self.json_treeview.get_children():
            self.json_treeview.delete(item)
        self.insert_json_data("", data)

    def add_header_field(self):
        header_row = ttk.Frame(self.headers_frame)
        header_row.pack(fill=tk.X, pady=2, padx=5)

        key_entry = ttk.Entry(header_row, width=30, font=("Segoe UI", 10))
        key_entry.pack(side=tk.LEFT, padx=5)
        value_entry = ttk.Entry(header_row, width=30, font=("Segoe UI", 10))
        value_entry.pack(side=tk.LEFT, padx=5)

        remove_btn = ttk.Button(header_row, text="✕", width=3, command=lambda: self.remove_header_field(header_row))
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
            content = self.body_text.get("1.0", tk.END).strip()
            if not content:
                return
            data = json.loads(content)
            self.body_text.delete("1.0", tk.END)
            self.body_text.insert(tk.END, json.dumps(data, indent=2))
            self.update_json_view()
        except json.JSONDecodeError as e:
            messagebox.showerror("Errore JSON", f"JSON non valido: {e}")

    def on_body_text_change(self, event=None):
        if self.body_type_var.get() == "JSON":
            self.update_json_view()

    def bombarda_config(self):
        errori = []
        finestra_errori = tk.Toplevel(self.root)
        finestra_errori.title("Errori Bombarda")
        finestra_errori.geometry("600x400")

        text_area = scrolledtext.ScrolledText(finestra_errori, font=("Consolas", 10))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for nome, config in self.configs.items():
            try:
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, config.get("url", ""))

                self.method_var.set(config.get("method", "GET"))

                for header_row in self.headers_frame.winfo_children()[1:]:
                    header_row.destroy()
                self.headers_entries.clear()
                for key, value in config.get("headers", {}).items():
                    k, v = self.add_header_field()
                    k.insert(0, key)
                    v.insert(0, value)

                self.body_type_var.set(config.get("body_type", "JSON"))
                self.body_text.delete("1.0", tk.END)
                self.body_text.insert("1.0", config.get("body", ""))

                self.update_body_visibility()
                self.root.update_idletasks()

                self.send_request()
            except Exception as e:
                text_area.insert(tk.END, f"[{nome}] ➜ Errore: {str(e)}\n\n")
                errori.append((nome, str(e)))

        if not errori:
            text_area.insert(tk.END, "✅ Tutte le richieste inviate con successo!\n")
