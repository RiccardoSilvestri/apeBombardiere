import tkinter as tk
from tkinter import ttk, scrolledtext

def create_url_section(self):
    url_frame = ttk.Frame(self.request_frame)
    url_frame.pack(fill=tk.X, padx=10, pady=5)
    
    ttk.Label(url_frame, text="URL:").pack(side=tk.LEFT, padx=(0, 5))
    
    self.url_entry = ttk.Entry(url_frame, width=60, font=("Segoe UI", 10))
    self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    self.method_menu = ttk.Combobox(url_frame, textvariable=self.method_var, 
                                  values=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"], 
                                  width=8, font=("Segoe UI", 10))
    self.method_menu.pack(side=tk.LEFT, padx=(5, 0))
    
    self.method_menu.bind("<<ComboboxSelected>>", lambda event: self.update_body_visibility())

def create_headers_section(self):
    self.headers_frame = ttk.LabelFrame(self.request_frame, text="Headers")
    self.headers_frame.pack(fill=tk.X, padx=10, pady=5)
    
    header_button_frame = ttk.Frame(self.headers_frame)
    header_button_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Button(header_button_frame, text="Aggiungi Header", 
              command=self.add_header_field).pack(side=tk.LEFT)

def create_body_section(self):
    self.body_frame = ttk.LabelFrame(self.request_frame, text="Body")
    
    body_type_frame = ttk.Frame(self.body_frame)
    body_type_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Label(body_type_frame, text="Tipo:").pack(side=tk.LEFT, padx=(0, 5))
    
    self.body_type_menu = ttk.Combobox(body_type_frame, textvariable=self.body_type_var,  
                                     values=["JSON", "x-www-form-urlencoded", "Raw"], 
                                     width=20, font=("Segoe UI", 10))
    self.body_type_menu.pack(side=tk.LEFT)
    
    self.body_text = scrolledtext.ScrolledText(self.body_frame, font=("Consolas", 10))
    self.body_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    self.body_text.bind("<KeyRelease>", self.on_body_text_change)

def create_buttons_section(self):
    button_frame = ttk.Frame(self.request_frame)
    button_frame.pack(fill=tk.X, padx=10, pady=10)
    
    ttk.Checkbutton(button_frame, text="Verifica SSL", 
                   variable=self.verify_ssl).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(button_frame, text="Formatta JSON", 
              command=self.format_json, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
    
    ttk.Button(button_frame, text="Invia Richiesta", 
              command=self.send_request, style="Success.TButton").pack(side=tk.LEFT, padx=5)
    
    ttk.Button(button_frame, text="Salva Configurazione", 
              command=self.save_config).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(button_frame, text="Carica Configurazione", 
              command=self.load_config).pack(side=tk.LEFT, padx=5)

def create_json_view(self):
    json_view_frame = ttk.LabelFrame(self.response_frame, text="Visualizzazione JSON")
    json_view_frame.pack(fill=tk.X, padx=10, pady=5, ipady=5)
    
    json_view_container = ttk.Frame(json_view_frame)
    json_view_container.pack(fill=tk.X, padx=5, pady=5)
    
    self.json_treeview = ttk.Treeview(json_view_container, columns=["Value"], show="tree", height=6)
    self.json_treeview.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    scrollbar = ttk.Scrollbar(json_view_container, orient="vertical", command=self.json_treeview.yview)
    self.json_treeview.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)