from sqlalchemy.orm import Session
from models import IngredienteBD
import crud.ingrediente_crud as ingrediente_crud
from conexion import get_session
from typing import List, Dict
from Ingrediente import Ingrediente

class Stock:
    def __init__(self):
        pass  

    def _get_db_session(self):
        """Obtener sesión de base de datos"""
        return next(get_session())

    def agregar_ingrediente(self, ingrediente: Ingrediente) -> bool:
        """Agrega o actualiza ingrediente en la base de datos"""
        if not ingrediente.nombre.strip():
            raise ValueError("El nombre del ingrediente no puede estar vacío.")
        
        if ingrediente.cantidad <= 0:
            raise ValueError("La cantidad debe ser un número positivo.")
        
        db = self._get_db_session()
        try:
            # Buscar si ya existe
            ingrediente_existente = ingrediente_crud.leer_ingrediente_por_nombre(db, ingrediente.nombre)
            
            if ingrediente_existente:
                # Actualizar cantidad sumando
                nueva_cantidad = ingrediente_existente.cantidad + int(ingrediente.cantidad)
                ingrediente_crud.actualizar_ingrediente(
                    db, ingrediente.nombre, nueva_cantidad, ingrediente.unidad
                )
                print(f"Stock de '{ingrediente.nombre}' actualizado a {nueva_cantidad}.")
            else:
                # Crear nuevo
                ingrediente_crud.crear_ingrediente(
                    db, ingrediente.nombre, ingrediente.unidad, int(ingrediente.cantidad)
                )
                print(f"Ingrediente '{ingrediente.nombre}' agregado con cantidad {ingrediente.cantidad}.")
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def eliminar_ingrediente(self, nombre: str) -> bool:
        """Elimina ingrediente por nombre"""
        db = self._get_db_session()
        try:
            resultado = ingrediente_crud.eliminar_ingrediente(db, nombre)
            db.commit()
            if resultado:
                print(f"Ingrediente '{nombre}' eliminado del stock.")
            return resultado
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def obtener_ingrediente(self, nombre_ingrediente: str) -> IngredienteBD:
        """Busca un ingrediente por su nombre en la base de datos"""
        db = self._get_db_session()
        try:
            ingrediente_db = ingrediente_crud.leer_ingrediente_por_nombre(db, nombre_ingrediente)
            if ingrediente_db:
                return Ingrediente(
                    nombre=ingrediente_db.nombre,
                    unidad=ingrediente_db.unidad,
                    cantidad=ingrediente_db.cantidad
                )
            return None
        finally:
            db.close()

    def obtener_todos_los_ingredientes(self) -> List[Ingrediente]:
        """Obtiene todos los ingredientes para mostrar en treeview"""
        db = self._get_db_session()
        try:
            ingredientes_db = ingrediente_crud.leer_ingredientes(db)
            # Convertir IngredienteBD a Ingrediente
            return [
                Ingrediente(
                    nombre=ing_db.nombre,
                    unidad=ing_db.unidad or "unid",
                    cantidad=ing_db.cantidad
                )
                for ing_db in ingredientes_db
            ]
        finally:
            db.close()

    @property
    def lista_ingredientes(self):
        """Propiedad que obtiene ingredientes desde BD (para compatibilidad con código existente)"""
        return self.obtener_todos_los_ingredientes()

    def descontar_stock(self, requerimientos: Dict[str, float]) -> bool:
        """Verifica y descuenta el stock según los requerimientos del menú"""
        db = self._get_db_session()
        try:
            # Verificar stock suficiente
            for nombre_ing, cantidad_necesaria in requerimientos.items():
                ingrediente = ingrediente_crud.leer_ingrediente_por_nombre(db, nombre_ing)
                if not ingrediente or ingrediente.cantidad < cantidad_necesaria:
                    print(f"Stock insuficiente para '{nombre_ing}'. Requerido: {cantidad_necesaria}, Disponible: {ingrediente.cantidad if ingrediente else 0}")
                    return False
            
            # Descontar stock
            for nombre_ing, cantidad_necesaria in requerimientos.items():
                ingrediente = ingrediente_crud.leer_ingrediente_por_nombre(db, nombre_ing)
                nueva_cantidad = ingrediente.cantidad - cantidad_necesaria
                ingrediente_crud.actualizar_ingrediente(db, nombre_ing, nueva_cantidad)
            
            db.commit()
            print("Descuento de stock completado exitosamente.")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error crítico al descontar stock: {e}")
            return False
        finally:
            db.close()

    def verificar_stock(self):
        """Muestra todo el stock disponible desde BD"""
        ingredientes = self.obtener_todos_los_ingredientes()
        
        datos_stock = list(map(
            lambda i: f" Ingrediente: {i.nombre}, Cantidad: {i.cantidad}", 
            ingredientes
        ))
        
        if datos_stock:
            print("\n--- Stock Actual (DB) ---")
            for linea in datos_stock:
                print(linea)
            print("-------------------------\n")
        else:
            print("No hay ingredientes registrados en el stock.")

    def actualizar_stock(self, datos_csv: List[Dict[str, str]]):
        """Actualiza stock desde CSV usando ORM"""
        print("Actualizando stock desde CSV...")

        datos_procesados = list(filter(
            lambda item: item['nombre'].strip() and item['cantidad'] > 0,
            map(
                lambda row: {
                    'nombre': row.get('nombre', '').strip(),
                    'unidad': row.get('unidad', 'unid').strip(),
                    'cantidad': float(row.get('cantidad', 0)) if str(row.get('cantidad', 0)).replace('.', '', 1).isdigit() else 0
                },
                datos_csv
            )
        ))
        
        if not datos_procesados:
            print("No se encontraron datos válidos en el CSV.")
            return
        
        for item in datos_procesados:
            ingrediente = Ingrediente(
                nombre=item['nombre'],
                unidad=item['unidad'],
                cantidad=item['cantidad']
            )
            self.agregar_ingrediente(ingrediente)
        
        print("Stock actualizado desde CSV.")

    def agregar_o_actualizar_ingrediente(self, nombre: str, unidad: str, cantidad: float) -> bool:
        """Método alternativo para compatibilidad - agrega o actualiza ingrediente"""
        ingrediente = Ingrediente(nombre=nombre, unidad=unidad, cantidad=cantidad)
        return self.agregar_ingrediente(ingrediente)
