from Ingrediente import Ingrediente
from typing import List, Optional, Dict
import crud.ingrediente_crud as ingrediente_crud


class Stock:
    def __init__(self): #porque se guarda en la base de datos 
        pass

    def agregar_o_actualizar_ingrediente (self, nombre:str,cantidad: float)-> Optional[ingredienteBD]:
        #valida que el nombre no este vacio y la cantidad sea positiva
        if not nombre.strip():
            print(" El nombre del ingrediente no puede estar vacío.")
            return None
        #validacion: la cantidad debe ser positiva y mayor que cero 
        if cantidad <= 0:
            print(" La cantidad debe ser un número positivo.")
            return None
        
        try:

            ingrediente_db=ingrediente_crud.crear_o_actualizar_ingrediente(nombre,cantidad)
            if ingrediente_db:
                print(f"Stock de '{nombre}' agregado/actualizado a {ingrediente_db.cantidad}.")
            return ingrediente_db
        except Exception as e:
            print(f" Error al agregar/actualizar el ingrediente: {e}")
            return None
        

    def obtener_ingrediente(self, nombre_ingrediente:str)-> Optional[ingredienteBD]:
       #busca un ingrediente por su nombre en la base de datos
        return ingrediente_crud.obtener_ingrediente_por_nombre(nombre_ingrediente)
    

    def eliminar_ingrediente(self, nombre_ingrediente:str):
        #elimina un ingrediente por nombre usando el ORM
        try:
            if ingrediente_crud.eliminar_ingrediente_db(nombre_ingrediente):
                print(f"Ingrediente '{nombre_ingrediente}' eliminado del stock.")
            else:
                print(f"Ingrediente '{nombre_ingrediente}' no encontrado.")
        except Exception as e:
            print(f" Error al eliminar el ingrediente: {e}")

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