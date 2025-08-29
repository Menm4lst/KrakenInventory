from data.repositories import MovementRepository, ProductRepository


class MovementService:
    @staticmethod
    def get_all_movements():
        return MovementRepository.get_all()

    @staticmethod
    def create_movement(movement_data):
        # Verificar que el producto existe
        product = ProductRepository.get_by_id(movement_data["product_id"])
        if not product:
            return False, "Producto no encontrado"
        
        # Calcular cambio de stock
        quantity_change = movement_data["quantity"]
        if movement_data["type"] == "out":
            quantity_change = -quantity_change
        
        # Verificar que el stock no sea negativo
        if product["current_stock"] + quantity_change < 0:
            return False, "Stock insuficiente para este movimiento"
        
        # Crear movimiento
        MovementRepository.create(movement_data)
        
        # Actualizar stock del producto
        new_stock = product["current_stock"] + quantity_change
        ProductRepository.update_stock(movement_data["product_id"], new_stock)
        
        return True, "Movimiento registrado correctamente"

    @staticmethod
    def get_movements_by_product(product_id):
        return MovementRepository.get_by_product_id(product_id)

    @staticmethod
    def get_movements_by_date_range(start_date, end_date):
        return MovementRepository.get_by_date_range(start_date, end_date)