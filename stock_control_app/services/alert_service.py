from data.repositories import ProductRepository


class AlertService:
    @staticmethod
    def get_low_stock_products():
        products = ProductRepository.get_all()
        low_stock = []
        
        for product in products:
            if product["current_stock"] <= product["min_stock"]:
                low_stock.append(product)
        
        return low_stock

    @staticmethod
    def get_overstock_products():
        products = ProductRepository.get_all()
        overstock = []
        
        for product in products:
            if product["max_stock"] > 0 and product["current_stock"] > product["max_stock"]:
                overstock.append(product)
        
        return overstock