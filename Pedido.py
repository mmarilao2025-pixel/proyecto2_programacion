import crud.menu_crud as menu_crud
import crud.pedido_crud as pedido_crud
from models import ClienteBD, PedidoBD #Models ORM
from functools import reduce
from typing import Dict, List, Dict, Optional


class Pedido:
    def __init__(self):
        self.menus: List[CrearMenu] = []
        self.gestor_stock = stock()

    def agregar_menu(self, menu: CrearMenu):
        """Agrega un menú al pedido o incrementa la cantidad si ya existe."""
        encontrado= next((item for item in self.menus if item.nombre == menu.nombre), None)
        if encontrado:
            encontrado.cantidad += 1
            return
        
        nuevo_menu = CrearMenu(
            nombre=menu.nombre,
            ingredientes=menu.ingredientes.copy(),
            precio=menu.precio,
            icono_path=menu.icono_path,
            cantidad=1
        )
        self.menus.append(nuevo_menu)

    def calcular_total(self) -> float:
        #calcula el subtotal por menu y luego suma todos.
        return sum(map(
            lambda menu: menu.precio * menu.cantidad,
            self.menus
        ))
   
    def _calcular_requerimientos(self) -> Dict[str, float]:
       # obtener la receta de un menú específico
        def obtener_receta_base(menu: CrearMenu) -> Dict[str, float]:
            return menu.ingredientes
       # map: Crea una lista de diccionarios de requerimientos por menú
        lista_requerimientos: List[Dict[str, float]] = list(map(
            lambda menu: {
                ing: cant * menu.cantidad
                for ing, cant in obtener_receta_base(menu).items()
            },
            self.menus
        ))            

        def combinar_requerimientos(acumulado: Dict[str, float], actual: Dict[str, float]) -> Dict[str, float]:
        
            for ingrediente, cantidad in actual.items():
                acumulado[ingrediente] = acumulado.get(ingrediente, 0) + cantidad
            return acumulado
        return reduce(combinar_requerimientos, lista_requerimientos, {})


    def procesar_compra(self, id_cliente: int) -> Optional[PedidoBD]:
        #Procesa la compra: valida stock, descuenta, guarda el pedido y limpia el carrito
        if not self.menus:
            print("Error: Debe agregar productos al pedido antes de generar la boleta.")
            return None
        
        # Validación de Cliente 
        cliente: Optional[ClienteBD] = pedido_crud.obtener_cliente_por_id(id_cliente)
        if not cliente:
            print(f"Error: Cliente con ID {id_cliente} no encontrado o inválido.")
            return None

        requerimientos_totales = self._calcular_requerimientos()
        
        if not requerimientos_totales:
            print("Error: No se pudo calcular los ingredientes necesarios (receta vacía).")
            return None
        # Verificación y Descuento de Stock
        if not self.gestor_stock.descontar_stock(requerimientos_totales):
            print("Error: Pedido cancelado: Stock insuficiente o error de transacción.")
            return None
        
        #Preparar y Guardar el Pedido en la DB
        try:
            total = self.calcular_total()
            
            # filtrando menús con cantidad > 0
            detalles_pedido = list(filter(
                lambda m: m.cantidad > 0,
                self.menus
            ))

            # Llama a la función CRUD para guardar el pedido
            pedido_final: PedidoBD = pedido_crud.crear_pedido(
                cliente=cliente, 
                total=total, 
                detalles_menus=detalles_pedido
            )
            
            # Limpiar carrito tras éxito
            self.limpiar_pedido()
            print(f"Pedido N°{pedido_final.id} para el cliente '{cliente.nombre}' generado y guardado. Total: ${total:.2f}")
            return pedido_final
            
        except Exception as e:
            print(f"Error Crítico al guardar el pedido en la DB: {e}")
            return None


    def limpiar_pedido(self):
        """Limpia todo el pedido."""
        self.menus.clear()

