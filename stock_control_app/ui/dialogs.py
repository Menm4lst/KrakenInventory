import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import Dialog


class ProductDialog(Dialog):
    def __init__(self, parent, title, product=None):
        self.product = product
        self.result = None
        super().__init__(parent, title=title)
    
    def body(self, master):
        ttk.Label(master, text="Código:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.code_var = tk.StringVar()
        self.code_entry = ttk.Entry(master, textvariable=self.code_var, width=30)
        self.code_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(master, text="Nombre:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(master, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(master, text="Descripción:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(master, textvariable=self.desc_var, width=30)
        self.desc_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(master, text="Categoría:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_entry = ttk.Entry(master, textvariable=self.category_var, width=30)
        self.category_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(master, text="Stock actual:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.stock_var = tk.StringVar()
        self.stock_entry = ttk.Entry(master, textvariable=self.stock_var, width=30)
        self.stock_entry.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(master, text="Stock mínimo:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.min_stock_var = tk.StringVar()
        self.min_stock_entry = ttk.Entry(master, textvariable=self.min_stock_var, width=30)
        self.min_stock_entry.grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(master, text="Stock máximo:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_stock_var = tk.StringVar()
        self.max_stock_entry = ttk.Entry(master, textvariable=self.max_stock_var, width=30)
        self.max_stock_entry.grid(row=6, column=1, padx=5, pady=5)
        
        ttk.Label(master, text="Costo:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
        self.cost_var = tk.StringVar()
        self.cost_entry = ttk.Entry(master, textvariable=self.cost_var, width=30)
        self.cost_entry.grid(row=7, column=1, padx=5, pady=5)
        
        ttk.Label(master, text="Precio:").grid(row=8, column=0, sticky=tk.W, padx=5, pady=5)
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(master, textvariable=self.price_var, width=30)
        self.price_entry.grid(row=8, column=1, padx=5, pady=5)
        
        # Si estamos editando, llenar los campos
        if self.product:
            self.code_var.set(self.product["code"])
            self.name_var.set(self.product["name"])
            self.desc_var.set(self.product["description"] or "")
            self.category_var.set(self.product["category"] or "")
            self.stock_var.set(str(self.product["current_stock"]))
            self.min_stock_var.set(str(self.product["min_stock"]))
            self.max_stock_var.set(str(self.product["max_stock"]))
            self.cost_var.set(str(self.product["cost"]))
            self.price_var.set(str(self.product["price"]))
        
        return self.code_entry  # Initial focus
    
    def validate(self):
        # Validaciones básicas
        if not self.code_var.get().strip():
            tk.messagebox.showerror("Error", "El código es obligatorio")
            return False
        
        if not self.name_var.get().strip():
            tk.messagebox.showerror("Error", "El nombre es obligatorio")
            return False
        
        try:
            stock = int(self.stock_var.get())
            min_stock = int(self.min_stock_var.get())
            max_stock = int(self.max_stock_var.get())
            cost = float(self.cost_var.get())
            price = float(self.price_var.get())
            
            if min_stock < 0 or max_stock < 0 or stock < 0 or cost < 0 or price < 0:
                tk.messagebox.showerror("Error", "Los valores numéricos deben ser positivos")
                return False
            
            if max_stock > 0 and min_stock > max_stock:
                tk.messagebox.showerror("Error", "El stock mínimo no puede ser mayor al máximo")
                return False
            
        except ValueError:
            tk.messagebox.showerror("Error", "Los valores numéricos deben ser válidos")
            return False
        
        return True
    
    def apply(self):
        self.result = {
            "code": self.code_var.get().strip(),
            "name": self.name_var.get().strip(),
            "description": self.desc_var.get().strip(),
            "category": self.category_var.get().strip(),
            "current_stock": int(self.stock_var.get()),
            "min_stock": int(self.min_stock_var.get()),
            "max_stock": int(self.max_stock_var.get()),
            "cost": float(self.cost_var.get()),
            "price": float(self.price_var.get())
        }