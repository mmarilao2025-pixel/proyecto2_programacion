from Ingrediente import Ingrediente
from typing import List
class Stock:
    def __init__(self):
        self.lista_ingredientes = []

    def agregar_ingrediente(self, ingrediente):
        for item in self.lista_ingredientes:
            if item.nombre.lower() == ingrediente.nombre.lower():
                item.cantidad += ingrediente.cantidad
                print(f" Stock de '{ingrediente.nombre}' actualizado a {item.cantidad}.")
                return
        self.lista_ingredientes.append(ingrediente)
        print(f" Nuevo ingrediente '{ingrediente.nombre}' agregado con cantidad {ingrediente.cantidad}.")

    def buscar_ingrediente(self, nombre_ingrediente: str):
        """Busca un ingrediente por nombre (case insensitive)"""
        for item in self.lista_ingredientes:
            if item.nombre.lower() == nombre_ingrediente.lower():
                return item
        return None
    
    def eliminar_ingrediente(self, nombre_ingrediente):
        for item in self.lista_ingredientes:
            if item.nombre.lower() == nombre_ingrediente.lower():
                self.lista_ingredientes.remove(item)
                print(f" Ingrediente '{nombre_ingrediente}' eliminado del stock.")
                return
        print(f" Ingrediente '{nombre_ingrediente}' no encontrado en el stock.") 

    def verificar_stock(self):
        for item in self.lista_ingredientes:
            print(f" Ingrediente: {item.nombre}, Cantidad: {item.cantidad}")

    def actualizar_stock(self, nombre_ingrediente: str, nueva_cantidad: float):
        """Actualiza la cantidad de un ingrediente específico."""
        ingrediente = self.buscar_ingrediente(nombre_ingrediente)
        if ingrediente:
            ingrediente_anterior = ingrediente.cantidad
            ingrediente.cantidad = float(nueva_cantidad)
            print(f"Stock de '{nombre_ingrediente}' actualizado: {ingrediente_anterior} → {nueva_cantidad}")
        else:
            print(f"Ingrediente '{nombre_ingrediente}' no encontrado.")

    def obtener_elementos_menu(self) -> List[Ingrediente]:
        return self.lista_ingredientes.copy()

