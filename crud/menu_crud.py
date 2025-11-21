from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import MenuBD, IngredienteBD, MenuIngredienteBD

class MenuCRUD:
    @staticmethod
    def crear_menu(db: Session, nombre: str, precio: float, categoria: str = "General"):
        """Crea nuevo menú validando nombre único"""
        existente = db.query(MenuBD).filter_by(nombre=nombre).first()
        if existente:
            raise ValueError(f"Menú '{nombre}' ya existe.")  
        if precio <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
            
        menu = MenuBD(nombre=nombre, precio=precio, categoria=categoria)
        db.add(menu)
        try:
            db.commit()
            db.refresh(menu)
            return menu
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al crear menú: {e}")
#_______________________________________________________________________
    @staticmethod
    def leer_menus(db: Session):
        """Obtiene todos los menús"""
        return db.query(MenuBD).all()

    @staticmethod
    def leer_menu_por_nombre(db: Session, nombre: str):
        """Busca menú por nombre"""
        return db.query(MenuBD).filter_by(nombre=nombre).first()

    @staticmethod
    def leer_menus_por_categoria(db: Session, categoria: str):
        """Filtra menús por categoría usando filter"""
        menus = db.query(MenuBD).all()
        return list(filter(lambda m: m.categoria == categoria, menus))
#__________________________________________________________________________
    @staticmethod
    def actualizar_menu(db: Session, nombre: str, nuevo_precio: float = None, 
                       nueva_categoria: str = None):
        """Actualiza precio o categoría de menú"""
        menu = db.query(MenuBD).filter_by(nombre=nombre).first()
        if not menu:
            raise ValueError(f"Menú '{nombre}' no encontrado.")
        
        if nuevo_precio is not None:
            if nuevo_precio <= 0:
                raise ValueError("El precio debe ser mayor a 0.")
            menu.precio = nuevo_precio
            
        if nueva_categoria:
            menu.categoria = nueva_categoria
            
        try:
            db.commit()
            db.refresh(menu)
            return menu
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al actualizar menú: {e}")
#________________________________________________________________
    @staticmethod
    def eliminar_menu(db: Session, nombre: str):
        """Elimina menú por nombre"""
        menu = db.query(MenuBD).filter_by(nombre=nombre).first()
        if not menu:
            raise ValueError(f"Menú '{nombre}' no encontrado.")
            
        db.delete(menu)
        try:
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al eliminar menú: {e}")
#____________________________________________________________________________
    @staticmethod
    def agregar_ingrediente_a_menu(db: Session, menu_nombre: str, ingrediente_nombre: str, cantidad: int = 1):
        """Agrega un ingrediente a un menú con la cantidad necesaria"""
        menu = db.query(MenuBD).filter_by(nombre=menu_nombre).first()
        ingrediente = db.query(IngredienteBD).filter_by(nombre=ingrediente_nombre).first()
        
        if not menu:
            raise ValueError(f"Menú '{menu_nombre}' no encontrado.")
        if not ingrediente:
            raise ValueError(f"Ingrediente '{ingrediente_nombre}' no encontrado.")
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0.")
        
        # Verificar si ya existe la relación
        existente = db.query(MenuIngredienteBD).filter_by(
            menu_id=menu.id, 
            ingrediente_id=ingrediente.id
        ).first()
        
        if existente:
            raise ValueError(f"El ingrediente '{ingrediente_nombre}' ya está en el menú '{menu_nombre}'.")
        
        # Crear nueva relación
        nueva_relacion = MenuIngredienteBD(
            menu_id=menu.id,
            ingrediente_id=ingrediente.id,
            cantidad_necesaria=cantidad
        )
        
        db.add(nueva_relacion)
        try:
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al agregar ingrediente al menú: {e}")
#______________________________________________________________________________________
    @staticmethod
    def eliminar_ingrediente_de_menu(db: Session, menu_nombre: str, ingrediente_nombre: str):
        """Elimina un ingrediente de un menú"""
        menu = db.query(MenuBD).filter_by(nombre=menu_nombre).first()
        ingrediente = db.query(IngredienteBD).filter_by(nombre=ingrediente_nombre).first()
        
        if not menu:
            raise ValueError(f"Menú '{menu_nombre}' no encontrado.")
        if not ingrediente:
            raise ValueError(f"Ingrediente '{ingrediente_nombre}' no encontrado.")
        
        # Buscar y eliminar la relación
        relacion = db.query(MenuIngredienteBD).filter_by(
            menu_id=menu.id, 
            ingrediente_id=ingrediente.id
        ).first()
        
        if relacion:
            db.delete(relacion)
            try:
                db.commit()
                return True
            except SQLAlchemyError as e:
                db.rollback()
                raise Exception(f"Error al eliminar ingrediente del menú: {e}")
        return False
#______________________________________________________________________________
    @staticmethod
    def obtener_ingredientes_de_menu(db: Session, menu_nombre: str):
        """Obtiene todos los ingredientes de un menú específico con sus cantidades"""
        menu = db.query(MenuBD).filter_by(nombre=menu_nombre).first()
        if not menu:
            raise ValueError(f"Menú '{menu_nombre}' no encontrado.")
        
        resultados = db.query(MenuIngredienteBD).filter_by(menu_id=menu.id).all()
        return [{"ingrediente": rel.ingrediente, "cantidad_necesaria": rel.cantidad_necesaria} 
                for rel in resultados]
#____________________________________________________________________________________
    @staticmethod
    def actualizar_cantidad_ingrediente(db: Session, menu_nombre: str, ingrediente_nombre: str, nueva_cantidad: int):
        """Actualiza la cantidad necesaria de un ingrediente en un menú"""
        menu = db.query(MenuBD).filter_by(nombre=menu_nombre).first()
        ingrediente = db.query(IngredienteBD).filter_by(nombre=ingrediente_nombre).first()
        
        if not menu:
            raise ValueError(f"Menú '{menu_nombre}' no encontrado.")
        if not ingrediente:
            raise ValueError(f"Ingrediente '{ingrediente_nombre}' no encontrado.")
        if nueva_cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0.")
        
        relacion = db.query(MenuIngredienteBD).filter_by(
            menu_id=menu.id, 
            ingrediente_id=ingrediente.id
        ).first()
        
        if not relacion:
            raise ValueError(f"El ingrediente '{ingrediente_nombre}' no está en el menú '{menu_nombre}'.")
        
        relacion.cantidad_necesaria = nueva_cantidad
        try:
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al actualizar cantidad: {e}")