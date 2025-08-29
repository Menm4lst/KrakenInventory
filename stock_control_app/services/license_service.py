import json
import os
from datetime import datetime


def check_license():
    default_response = {
        "valid": False,
        "message": "Licencia no válida",
        "read_only": True
    }
    
    try:
        license_path = os.path.join(os.path.dirname(__file__), "..", "license.json")
        with open(license_path, "r") as f:
            license_data = json.load(f)
        
        # Verificar fecha de expiración
        expiry_date = datetime.strptime(license_data["expiry_date"], "%Y-%m-%d")
        if datetime.now() > expiry_date:
            return {
                "valid": False,
                "message": "Licencia expirada",
                "read_only": True
            }
        
        # Aquí se pueden agregar más validaciones
        
        return {
            "valid": True,
            "message": "Licencia válida",
            "read_only": False
        }
    
    except FileNotFoundError:
        default_response["message"] = "Archivo de licencia no encontrado"
        return default_response
    except Exception as e:
        default_response["message"] = f"Error validando licencia: {str(e)}"
        return default_response