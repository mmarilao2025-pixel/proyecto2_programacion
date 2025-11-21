from sqlalchemy.orm import Session
from models import IngredienteBD
import crud.ingrediente_crud as ingrediente_crud
from conexion import get_session

class Stock:
    def __init__(self):
        pass

    def _get_db_session(self):
        """Obtener sesión de base de datos"""
        return next(get_session())

    def agregar_o_actualizar_ingrediente(self, nombre: str, unidad: str, cantidad: float) -> bool:
        """Agrega o actualiza ingrediente en la base de datos"""
        if not nombre.strip():
            raise ValueError("El nombre del ingrediente no puede estar vacío.")
        
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser un número positivo.")
        
        db = self._get_db_session()
        try:
            # Buscar si ya existe
            ingrediente_existente = ingrediente_crud.leer_ingrediente_por_nombre(db, nombre)
            
            if ingrediente_existente:
                # Actualizar
                ingrediente_crud.actualizar_ingrediente(
                    db, nombre, nueva_cantidad=cantidad, nueva_unidad=unidad
                )
            else:
                # Crear nuevo
                ingrediente_crud.crear_ingrediente(db, nombre, unidad, cantidad)
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def obtener_todos_los_ingredientes(self):
        """Obtiene todos los ingredientes para mostrar en treeview"""
        db = self._get_db_session()
        try:
            return ingrediente_crud.leer_ingredientes(db)
        finally:
            db.close()

    def eliminar_ingrediente(self, nombre: str) -> bool:
        """Elimina ingrediente por nombre"""
        db = self._get_db_session()
        try:
            resultado = ingrediente_crud.eliminar_ingrediente(db, nombre)
            db.commit()
            return resultado
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def descontar_stock(self, requerimientos: Dict[str, float]) -> bool:
        #verifica y descuenta el stock segun los requerimientos del menu
        ingredientes_a_validar=[(nombre, self.obtener_ingrediente(nombre))
                                 for nombre in requerimientos.keys()]
        stock_insuficiente= list(filter(
            lambda item: item[1] is None or item[1].cantidad < requerimientos.get(item[0]),
            ingredientes_a_validar
        ))

        if stock_insuficiente:
            # map y lambda: crea un mensaje de error para cada ingrediente con stock insuficiente
            mensajes_error = list(map(
                lambda item: f" Stock insuficiente para '{item[0]}'. Requerido: {requerimientos.get(item[0])}, Disponible: {item[1].cantidad if item[1] else 0}",
                stock_insuficiente  
            ))
            print("error: Stock insuficiente para los siguientes ingredientes:")
            for msg in mensajes_error:
                print(f" - {msg}")
            return False
        
        try:
                ingrediente_crud.descontar_multiples_ingredientes(requerimientos)
                print("Descuento de stock completado exitosamente.")
                return True
            
        except Exception as e:
                  print(f"Error crítico al descontar stock: {e}")
                  return False


    def verificar_stock(self):
        #Muestra todo el stock disponible 
        ingredientes: List[IngredienteBD] = ingrediente_crud.obtener_todos_los_ingredientes()
        
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

    def actualizar_stock(self, datos_csv: list[Dict[str, str]]):
        print("Actualizando stock desde CSV...")


        datos_procesados= list(filter(
            lambda item: item['nombre'].strip() and item['cantidad']>0,
            map(
                lambda row:{
                    'nombre': row.get('nombre', ''),
                    'cantidad': float(row.get('cantidad', 0)) if row.get('cantidad') and row.get('cantidad').replace('.', '', 1).isdigit() else 0

                },
                datos_csv
            )
        ))
        
        if not datos_procesados:
            print(" No se encontraron datos válidos en el CSV.")
            return
        for item in datos_procesados:
            self.agregar_o_actualizar_ingrediente(item['nombre'], item['cantidad'])
        print(" Stock actualizado desde CSV.")
