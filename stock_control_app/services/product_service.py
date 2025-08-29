from data.repositories import ProductRepository


class ProductService:
    @staticmethod
    def get_all_products():
        return ProductRepository.get_all()

    @staticmethod
    def get_product(product_id):
        return ProductRepository.get_by_id(product_id)

    @staticmethod
    def create_product(product_data):
        # Validar que el código no exista
        existing = ProductRepository.get_by_code(product_data["code"])
        if existing:
            return False, "Ya existe un producto con este código"
        
        product_id = ProductRepository.create(product_data)
        return True, f"Producto creado con ID: {product_id}"

    @staticmethod
    def update_product(product_id, product_data):
        # Validar que el código no exista en otro producto
        existing = ProductRepository.get_by_code(product_data["code"])
        if existing and existing["id"] != product_id:
            return False, "Ya existe otro producto con este código"
        
        ProductRepository.update(product_id, product_data)
        return True, "Producto actualizado correctamente"

    @staticmethod
    def delete_product(product_id):
        ProductRepository.delete(product_id)
        return True, "Producto eliminado correctamente"

    @staticmethod
    def search_products(search_term):
        return ProductRepository.search(search_term)

    @staticmethod
    def update_product_stock(product_id, quantity_change):
        product = ProductRepository.get_by_id(product_id)
        if not product:
            return False, "Producto no encontrado"
        
        new_stock = product["current_stock"] + quantity_change
        if new_stock < 0:
            return False, "Stock no puede ser negativo"
        
        ProductRepository.update_stock(product_id, new_stock)
        return True, "Stock actualizado correctamente"