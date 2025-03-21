import json
from tkinter import messagebox

def format_json_text(text_widget):
    try:
        body_content = text_widget.get("1.0", "end").strip()
        if not body_content:
            return False
            
        data = json.loads(body_content)
        text_widget.delete("1.0", "end")
        text_widget.insert("end", json.dumps(data, indent=2))
        return True
    except json.JSONDecodeError as e:
        messagebox.showerror("Errore JSON", f"JSON non valido: {e}")
        return False

def insert_json_to_treeview(treeview, data, parent=""):
    if isinstance(data, dict):
        for key, value in data.items():
            parent_id = treeview.insert(parent, "end", text=key)
            insert_json_to_treeview(treeview, value, parent_id)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            parent_id = treeview.insert(parent, "end", text=f"Item {i}")
            insert_json_to_treeview(treeview, item, parent_id)
    else:
        treeview.insert(parent, "end", text=str(data))