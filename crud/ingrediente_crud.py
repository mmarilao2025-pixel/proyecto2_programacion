from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import IngredienteBD

class IngredienteCRUD:
    @staticmethod
    def crear_ingrediente(db: Session, nombre: str, unidad: str, cantidad: int):
        """Crea nuevo ingrediente validando nombre único"""
        existente = db.query(IngredienteBD).filter_by(nombre=nombre).first()
        if existente:
            raise ValueError(f"Ingrediente '{nombre}' ya existe.")
        
        if cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa.")
            
        ingrediente = IngredienteBD(nombre=nombre, unidad=unidad, cantidad=cantidad)
        db.add(ingrediente)
        try:
            db.commit()
            db.refresh(ingrediente)
            return ingrediente
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al crear ingrediente: {e}")
#_________________________________________________________________________________
    @staticmethod
    def leer_ingredientes(db: Session):
        """Obtiene todos los ingredientes"""
        return db.query(IngredienteBD).all()

    @staticmethod
    def leer_ingrediente_por_nombre(db: Session, nombre: str):
        """Busca ingrediente por nombre"""
        return db.query(IngredienteBD).filter_by(nombre=nombre).first()
#____________________________________________________________________________
    @staticmethod
    def actualizar_ingrediente(db: Session, nombre: str, nueva_cantidad: int = None, 
                              nueva_unidad: str = None):
        """Actualiza cantidad o unidad de ingrediente"""
        ingrediente = db.query(IngredienteBD).filter_by(nombre=nombre).first()
        if not ingrediente:
            raise ValueError(f"Ingrediente '{nombre}' no encontrado.")
        
        if nueva_cantidad is not None:
            if nueva_cantidad < 0:
                raise ValueError("La cantidad no puede ser negativa.")
            ingrediente.cantidad = nueva_cantidad
            
        if nueva_unidad:
            ingrediente.unidad = nueva_unidad
            
        try:
            db.commit()
            db.refresh(ingrediente)
            return ingrediente
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al actualizar ingrediente: {e}")
#_______________________________________________________________________________
    @staticmethod
    def eliminar_ingrediente(db: Session, nombre: str):
        """Elimina ingrediente por nombre"""
        ingrediente = db.query(IngredienteBD).filter_by(nombre=nombre).first()
        if not ingrediente:
            raise ValueError(f"Ingrediente '{nombre}' no encontrado.")
            
        db.delete(ingrediente)
        try:
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al eliminar ingrediente: {e}")