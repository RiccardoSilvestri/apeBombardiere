COLORS = {
    "primary": "#2563eb",
    "secondary": "#4b5563",
    "success": "#10b981",
    "error": "#ef4444",
    "warning": "#f59e0b",
    "background": "#f9fafb",
    "text": "#1f2937",
    "border": "#d1d5db",
    "highlight": "#dbeafe"
}

def configure_styles(style):
    style.theme_use('clam')
    
    style.configure("TFrame", background=COLORS["background"])
    style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1)
    
    style.configure("TLabel", background=COLORS["background"], foreground=COLORS["text"], font=("Segoe UI", 10))
    style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
    style.configure("Status.TLabel", foreground=COLORS["primary"], font=("Segoe UI", 10, "bold"))
    
    style.configure("TButton", background=COLORS["primary"], foreground="white", 
                    font=("Segoe UI", 10), relief="flat", padding=5)
    style.map("TButton", 
             background=[("active", COLORS["primary"])],
             relief=[("pressed", "sunken")])
    
    style.configure("Secondary.TButton", background=COLORS["secondary"])
    style.map("Secondary.TButton", 
             background=[("active", COLORS["secondary"])])
    
    style.configure("Success.TButton", background=COLORS["success"])
    style.map("Success.TButton", 
             background=[("active", COLORS["success"])])
    
    style.configure("TCombobox", padding=5, relief="flat")
    
    style.configure("TLabelframe", background="white", relief="solid", borderwidth=1)
    style.configure("TLabelframe.Label", background=COLORS["background"], 
                    foreground=COLORS["primary"], font=("Segoe UI", 11, "bold"))
    
    style.configure("Treeview", 
                    background="white", 
                    foreground=COLORS["text"],
                    rowheight=25,
                    fieldbackground="white")
    style.map("Treeview", 
             background=[("selected", COLORS["highlight"])],
             foreground=[("selected", COLORS["primary"])])
    

    style.configure("Error.TButton", background=COLORS["error"])
    style.map("Error.TButton", background=[("active", COLORS["error"])])
