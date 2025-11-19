from fpdf import FPDF
from datetime import datetime
import os

def _latin1(s: str) -> str:
    return s.encode("latin-1", "replace").decode("latin-1")

class BoletaFacade:
    def __init__(self, pedido):
        self.pedido = pedido
        self.items_detalle = []
        self.subtotal = 0.0
        self.iva = 0.0
        self.total = 0.0

    def _format_currency(self, amount: float) -> str:
        return f"${amount:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")

    def generar_detalle_boleta(self):
        if not self.pedido.menus:
            raise ValueError("El pedido no contiene productos para generar la boleta.")

        self.items_detalle = []

        for item in self.pedido.menus:
            if not hasattr(item, "precio") or not hasattr(item, "cantidad"):
                raise AttributeError("El menú carece de atributos requeridos (precio o cantidad).")

            subtotal_item = item.precio * item.cantidad

            self.items_detalle.append({
                "nombre": item.nombre,
                "cantidad": item.cantidad,
                "precio": item.precio,
                "subtotal": subtotal_item
            })

        self.subtotal = sum(x["subtotal"] for x in self.items_detalle)
        self.iva = self.subtotal * 0.19
        self.total = self.subtotal + self.iva

    def crear_pdf(self, pdf_path: str = "boleta.pdf"):
        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, _latin1("Boleta Restaurante"), ln=True)

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, _latin1("Razón Social del Negocio"), ln=True)
        pdf.cell(0, 8, "RUT: 12.345.678-9", ln=True)
        pdf.cell(0, 8, _latin1("Dirección: Calle Falsa 123"), ln=True)
        pdf.cell(0, 8, _latin1("Teléfono: +56 9 1234 5678"), ln=True)
        pdf.cell(0, 8, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align='R')
        pdf.ln(8)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(70, 10, _latin1("Menú"), border=1)
        pdf.cell(20, 10, _latin1("Cant."), border=1, align='C')
        pdf.cell(35, 10, _latin1("Precio Unit."), border=1, align='R')
        pdf.cell(30, 10, "Subtotal", border=1, ln=1, align='R')

        pdf.set_font("Arial", size=12)

        for item in self.items_detalle:
            pdf.cell(70, 10, _latin1(item["nombre"]), border=1)
            pdf.cell(20, 10, str(item["cantidad"]), border=1, align='C')
            pdf.cell(35, 10, self._format_currency(item["precio"]), border=1, align='R')
            pdf.cell(30, 10, self._format_currency(item["subtotal"]), border=1, ln=1, align='R')

        pdf.set_font("Arial", "B", 12)
        pdf.cell(125, 10, "Subtotal:", 0, 0, 'R')
        pdf.cell(30, 10, self._format_currency(self.subtotal), ln=1, align='R')

        pdf.cell(125, 10, "IVA (19%):", 0, 0, 'R')
        pdf.cell(30, 10, self._format_currency(self.iva), ln=1, align='R')

        pdf.cell(125, 10, "Total:", 0, 0, 'R')
        pdf.cell(30, 10, self._format_currency(self.total), ln=1, align='R')

        pdf.ln(5)
        pdf.set_font("Arial", "I", 10)
        pdf.set_text_color(90, 90, 90)
        pdf.cell(0, 8, _latin1("Gracias por su compra."), 0, 1, 'C')

        abs_path = os.path.abspath(pdf_path)
        pdf.output(abs_path)
        return abs_path

    def generar_boleta(self, pdf_path: str = "boleta.pdf"):
        self.generar_detalle_boleta()
        final_path = self.crear_pdf(pdf_path)
        return final_path
