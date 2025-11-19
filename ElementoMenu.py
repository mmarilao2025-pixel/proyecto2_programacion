from dataclasses import dataclass, field
from typing import List, Optional
from Ingrediente import Ingrediente
from Stock import Stock
from IMenu import IMenu

@dataclass
class CrearMenu(IMenu):
    nombre: str
    ingredientes: List[Ingrediente]
    precio: float = 0.0
    icono_path: Optional[str] = None
    cantidad: int = field(default=0, compare=False)

    def esta_disponible(self, stock: Stock) -> bool:
        for req in self.ingredientes:
            ok = False
            for ing in stock.lista_ingredientes:
                if ing.nombre == req.nombre and (req.unidad is None or ing.unidad == req.unidad):
                    if float(ing.cantidad) >= float(req.cantidad):
                        ok = True
                        break
            if not ok:
                return False
        return True

    def __str__(self):
        return f"{self.nombre} - ${self.precio:.2f}"

    def __repr__(self):
        return f"CrearMenu(nombre='{self.nombre}', precio={self.precio}, cantidad={self.cantidad})"

