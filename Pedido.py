from ElementoMenu import CrearMenu 
from typing import List

class Pedido:
    def __init__(self):
        self.menus: List[CrearMenu] = []  

    def agregar_menu(self, menu: CrearMenu):
        """Agrega un menú al pedido o incrementa la cantidad si ya existe."""
        for item in self.menus:
            if item.nombre == menu.nombre:
                item.cantidad += 1
                return
        # Crear una copia del menú con cantidad 1
        nuevo_menu = CrearMenu(
            nombre=menu.nombre,
            ingredientes=menu.ingredientes.copy(),
            precio=menu.precio,
            icono_path=menu.icono_path,
            cantidad=1
        )
        self.menus.append(nuevo_menu)

    def eliminar_menu(self, nombre_menu: str):
        # Disminuye la cantidad de un menú o lo elimina si llega a 0
        for menu in self.menus:
            if menu.nombre == nombre_menu:
                menu.cantidad -= 1
                if menu.cantidad <= 0:
                    self.menus.remove(menu)
                break


    def mostrar_pedido(self):
        """Muestra el contenido del pedido."""
        if not self.menus:
            print("El pedido está vacío.")
            return
        
        print("Pedido actual:")
        for menu in self.menus:
            print(f"  - {menu.nombre}: {menu.cantidad} x ${menu.precio:.2f} = ${menu.cantidad * menu.precio:.2f}")
        
        total = self.calcular_total()
        print(f"Total: ${total:.2f}") #llama al metodo de abajo

    def calcular_total(self) -> float:
        """Calcula el total del pedido."""
        return sum(menu.precio * menu.cantidad for menu in self.menus)

    def limpiar_pedido(self):
        """Limpia todo el pedido."""
        self.menus.clear()

