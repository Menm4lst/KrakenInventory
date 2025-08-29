import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

from data.database import init_db
from services.license_service import check_license
from ui.main_window import MainWindow


def main():
    # Verificar licencia
    license_status = check_license()
    if not license_status["valid"]:
        messagebox.showerror("Error de Licencia", license_status["message"])
        return

    # Inicializar base de datos
    init_db()
    
    # Cargar configuración
    config = {}
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
        except:
            config = {}
    
    # Crear aplicación
    root = tk.Tk()
    root.title("Sistema de Control de Stock")
    root.geometry("1200x700")
    
    # Crear ventana principal
    app = MainWindow(root, config, license_status["read_only"])
    
    # Configurar hotkeys globales
    root.bind("<Control-n>", lambda e: app.on_new_item())
    root.bind("<Control-e>", lambda e: app.on_edit_item())
    root.bind("<Delete>", lambda e: app.on_delete_item())
    root.bind("<Control-f>", lambda e: app.on_search())
    
    root.mainloop()


if __name__ == "__main__":
    main()