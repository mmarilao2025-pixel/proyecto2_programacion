from models import ClienteBD, PedidoBD
from functools import reduce
from typing import Dict, List, Optional
from Stock import Stock
from ElementoMenu import CrearMenu
from conexion import get_session
from crud.pedido_crud import PedidoCRUD
from datetime import datetime

class Pedido:
    def __init__(self):
        self.menus: List[CrearMenu] = []
        self.gestor_stock = Stock() 

    def agregar_menu(self, menu: CrearMenu):
        """Agrega un menú al pedido o incrementa la cantidad si ya existe."""
        encontrado = next(
            filter(lambda item: item.nombre == menu.nombre, self.menus), 
            None
        )
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
        """Calcula el subtotal por menu y luego suma todos."""
        return sum(map(
            lambda menu: menu.precio * menu.cantidad,
            self.menus
        ))
   
    def _calcular_requerimientos(self) -> Dict[str, float]:
        """Calcula los requerimientos totales de ingredientes para el pedido"""
        def obtener_requerimientos_menu(menu: CrearMenu) -> Dict[str, float]:
            """Obtiene los requerimientos de un menú específico"""
            return {
                ing.nombre: float(ing.cantidad) * menu.cantidad
                for ing in menu.ingredientes
            }
       
        lista_requerimientos: List[Dict[str, float]] = list(map(
            obtener_requerimientos_menu,
            self.menus
        ))            

        def combinar_requerimientos(acumulado: Dict[str, float], actual: Dict[str, float]) -> Dict[str, float]:
            """Combina requerimientos usando reduce"""
            for ingrediente, cantidad in actual.items():
                acumulado[ingrediente] = acumulado.get(ingrediente, 0) + cantidad
            return acumulado
        
        # USO DE REDUCE (requisito de pauta)
        return reduce(combinar_requerimientos, lista_requerimientos, {})

    def _descontar_ingredientes_pedido(self) -> bool:
        """Descuenta los ingredientes del stock para todo el pedido"""
        try:
            requerimientos_totales = self._calcular_requerimientos()
            
            if not requerimientos_totales:
                print("Error: No se pudieron calcular los requerimientos.")
                return False
            
            # Descontar del stock usando el gestor de stock
            return self.gestor_stock.descontar_stock(requerimientos_totales)
            
        except Exception as e:
            print(f"Error al descontar ingredientes: {e}")
            return False

    def procesar_compra(self, cliente_rut: str = None) -> Optional[PedidoBD]:
        """
        Procesa la compra: valida stock, descuenta, guarda el pedido y limpia el carrito
        """
        if not self.menus:
            print("Error: Debe agregar productos al pedido antes de generar la boleta.")
            return None
        
        # Validación de Cliente (temporal - por defecto)
        if not cliente_rut:
            cliente_rut = "11111111-1"  
        
        db = next(get_session())
        try:
            # Verificar si el cliente existe
            from crud.cliente_crud import ClienteCRUD
            cliente: Optional[ClienteBD] = ClienteCRUD.leer_cliente_por_rut(db, cliente_rut)
            
            if not cliente:
                print(f"Cliente con RUT '{cliente_rut}' no encontrado. Usando cliente por defecto.")
                # Crear cliente por defecto si no existe
                try:
                    cliente = ClienteCRUD.crear_cliente(db, "Cliente General", cliente_rut, "000000000")
                    db.commit()
                except Exception:
                    # Si ya existe, obtenerlo
                    cliente = ClienteCRUD.leer_cliente_por_rut(db, cliente_rut)

            # Verificar y descontar stock
            if not self._descontar_ingredientes_pedido():
                print("Error: Stock insuficiente para procesar el pedido.")
                return None
            
            # Calcular total
            total = self.calcular_total()
        
            detalles_pedido = list(filter(
                lambda m: m.cantidad > 0,
                self.menus
            ))

            if not detalles_pedido:
                print("Error: No hay menús válidos en el pedido.")
                return None

            # Guardar el pedido en la base de datos
            pedido_final: PedidoBD = PedidoCRUD.crear_pedido(db, cliente_rut, total)
            
            # Guardar detalles del pedido (menús)
            self._guardar_detalles_pedido(db, pedido_final.id, detalles_pedido)
            
            db.commit()
            
            print(f"Pedido N°{pedido_final.id} para '{cliente.nombre}' guardado. Total: ${total:.2f}")
            return pedido_final
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error Crítico al guardar el pedido en la DB: {e}")
            return None
        finally:
            db.close()

    def _guardar_detalles_pedido(self, db: Session, pedido_id: int, detalles_menus: List[CrearMenu]):
        """Guarda los detalles del pedido en la base de datos"""
        try:
            from crud.menu_crud import MenuCRUD
            from models import MenuBD
            
            for menu in detalles_menus:
                # Verificar si el menú existe en la base de datos
                menu_db = MenuCRUD.leer_menu_por_nombre(db, menu.nombre)
                if not menu_db:
                    # Crear el menú si no existe
                    menu_db = MenuCRUD.crear_menu(db, menu.nombre, menu.precio, "General")
                
                # Aquí podrías guardar la relación pedido-menú en una tabla de detalles
                # Por ahora solo registramos el pedido principal
                print(f"  - {menu.cantidad}x {menu.nombre} (${menu.precio:.2f} c/u)")
                
        except Exception as e:
            print(f"Error al guardar detalles del pedido: {e}")
            raise

    def limpiar_pedido(self):
        """Limpia todo el pedido después de procesarlo."""
        self.menus.clear()
        print("Pedido limpiado correctamente.")

    def obtener_resumen_pedido(self) -> Dict:
        """Obtiene un resumen del pedido actual"""
        # USO DE MAP para crear resumen
        items_resumen = list(map(
            lambda menu: {
                'nombre': menu.nombre,
                'cantidad': menu.cantidad,
                'precio_unitario': menu.precio,
                'subtotal': menu.precio * menu.cantidad
            },
            self.menus
        ))
        
        total = self.calcular_total()
        
        return {
            'items': items_resumen,
            'total': total,
            'cantidad_total': sum(menu.cantidad for menu in self.menus)
        }

    def __str__(self):
        """Representación en string del pedido"""
        if not self.menus:
            return "Pedido vacío"
        
        # USO DE MAP para formatear items
        items_str = list(map(
            lambda menu: f"  {menu.cantidad}x {menu.nombre} - ${menu.precio * menu.cantidad:.2f}",
            self.menus
        ))
        
        return f"Pedido (Total: ${self.calcular_total():.2f}):\n" + "\n".join(items_str)

    def __repr__(self):
        return f"Pedido(menus={len(self.menus)}, total=${self.calcular_total():.2f})"
