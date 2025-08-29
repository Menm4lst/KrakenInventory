import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.simpledialog import Dialog

from services.product_service import ProductService
from ui.dialogs import ProductDialog


class ProductUI:
    def __init__(self, parent, read_only=False):
        self.parent = parent
        self.read_only = read_only
        self.frame = ttk.Frame(parent)
        
        self.setup_ui()
        self.load_products()
        
    def setup_ui(self):
        # Barra de herramientas
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Nuevo", command=self.new_product, state="normal" if not self.read_only else "disabled").pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Editar", command=self.edit_product, state="normal" if not self.read_only else "disabled").pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Eliminar", command=self.delete_product, state="normal" if not self.read_only else "disabled").pack(side=tk.LEFT, padx=2)

        # Filtros avanzados
        filter_frame = ttk.LabelFrame(self.frame, text="Filtros avanzados")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_frame, text="Categoría:").grid(row=0, column=0, padx=5, pady=2)
        self.category_var = tk.StringVar()
        self.category_entry = ttk.Entry(filter_frame, textvariable=self.category_var, width=15)
        self.category_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(filter_frame, text="Stock mínimo:").grid(row=0, column=2, padx=5, pady=2)
        self.min_stock_var = tk.StringVar()
        self.min_stock_entry = ttk.Entry(filter_frame, textvariable=self.min_stock_var, width=8)
        self.min_stock_entry.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(filter_frame, text="Stock máximo:").grid(row=0, column=4, padx=5, pady=2)
        self.max_stock_var = tk.StringVar()
        self.max_stock_entry = ttk.Entry(filter_frame, textvariable=self.max_stock_var, width=8)
        self.max_stock_entry.grid(row=0, column=5, padx=5, pady=2)

        ttk.Label(filter_frame, text="Precio máximo:").grid(row=0, column=6, padx=5, pady=2)
        self.max_price_var = tk.StringVar()
        self.max_price_entry = ttk.Entry(filter_frame, textvariable=self.max_price_var, width=10)
        self.max_price_entry.grid(row=0, column=7, padx=5, pady=2)

        ttk.Button(filter_frame, text="Aplicar filtros", command=self.apply_filters).grid(row=0, column=8, padx=10, pady=2)

        # Barra de búsqueda
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=tk.RIGHT)

        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # Treeview para productos
        self.tree = ttk.Treeview(self.frame, columns=("code", "name", "category", "stock", "price"), show="headings")

        # Configurar columnas
        self.tree.heading("code", text="Código", command=lambda: self.sort_column("code", False))
        self.tree.heading("name", text="Nombre", command=lambda: self.sort_column("name", False))
        self.tree.heading("category", text="Categoría", command=lambda: self.sort_column("category", False))
        self.tree.heading("stock", text="Stock", command=lambda: self.sort_column("stock", False))
        self.tree.heading("price", text="Precio", command=lambda: self.sort_column("price", False))

        self.tree.column("code", width=100)
        self.tree.column("name", width=200)
        self.tree.column("category", width=150)
        self.tree.column("stock", width=80)
        self.tree.column("price", width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Bind double click to edit
        self.tree.bind("<Double-1>", self.on_double_click)

    def apply_filters(self):
        # Obtener valores de los filtros
        category = self.category_var.get().strip()
        min_stock = self.min_stock_var.get().strip()
        max_stock = self.max_stock_var.get().strip()
        max_price = self.max_price_var.get().strip()

        # Obtener todos los productos
        products = ProductService.get_all_products()
        filtered = []
        for product in products:
            if category and category.lower() not in product["category"].lower():
                continue
            if min_stock:
                try:
                    if product["current_stock"] < int(min_stock):
                        continue
                except:
                    continue
            if max_stock:
                try:
                    if product["current_stock"] > int(max_stock):
                        continue
                except:
                    continue
            if max_price:
                try:
                    if product["price"] > float(max_price):
                        continue
                except:
                    continue
            filtered.append(product)

        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        for product in filtered:
            self.tree.insert("", tk.END, values=(
                product["code"],
                product["name"],
                product["category"],
                product["current_stock"],
                f"${product['price']:.2f}"
            ), iid=product["id"])
        
    def load_products(self):
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cargar productos
        products = ProductService.get_all_products()
        for product in products:
            self.tree.insert("", tk.END, values=(
                product["code"],
                product["name"],
                product["category"],
                product["current_stock"],
                f"${product['price']:.2f}"
            ), iid=product["id"])
    
    def sort_column(self, col, reverse):
        # Get all values from the column
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        
        # Try to convert to numbers if possible
        try:
            data.sort(key=lambda x: float(x[0]) if x[0].replace('.', '').isdigit() else x[0], reverse=reverse)
        except:
            data.sort(reverse=reverse)
        
        # Rearrange items
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
        
        # Reverse sort next time
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))
    
    def on_search(self, event=None):
        search_term = self.search_var.get()
        if not search_term:
            self.load_products()
            return
        
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Buscar productos
        products = ProductService.search_products(search_term)
        for product in products:
            self.tree.insert("", tk.END, values=(
                product["code"],
                product["name"],
                product["category"],
                product["current_stock"],
                f"${product['price']:.2f}"
            ), iid=product["id"])
    
    def new_product(self):
        dialog = ProductDialog(self.frame, title="Nuevo Producto")
        if dialog.result:
            success, message = ProductService.create_product(dialog.result)
            if success:
                messagebox.showinfo("Éxito", message)
                self.load_products()
            else:
                messagebox.showerror("Error", message)
    
    def edit_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
            return
        
        product_id = int(selected[0])
        product = ProductService.get_product(product_id)
        
        dialog = ProductDialog(self.frame, title="Editar Producto", product=product)
        if dialog.result:
            success, message = ProductService.update_product(product_id, dialog.result)
            if success:
                messagebox.showinfo("Éxito", message)
                self.load_products()
            else:
                messagebox.showerror("Error", message)
    
    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este producto?"):
            product_id = int(selected[0])
            success, message = ProductService.delete_product(product_id)
            if success:
                messagebox.showinfo("Éxito", message)
                self.load_products()
            else:
                messagebox.showerror("Error", message)
    
    def on_double_click(self, event):
        if not self.read_only:
            self.edit_product()