from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import IngredienteBD

class IngredienteCRUD:
    @staticmethod
    def crear_ingrediente(db: Session, nombre: str, unidad: str, cantidad: int):
        
        pass
    @staticmethod
    def leer_ingrediente():
        pass
    @staticmethod
    def actualizar_ingrediente():
        pass
    @staticmethod
    def eliminar_ingrediente():
        pass