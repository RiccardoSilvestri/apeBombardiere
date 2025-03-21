import tkinter as tk
from api_client import APIClient

if __name__ == "__main__":
    root = tk.Tk()
    app = APIClient(root)
    root.mainloop()