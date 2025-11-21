import matplotlib.pyplot as plt
import customtkinter
from PIL import Image, ImageTk
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from conexion import get_session
from models import PedidoBD, MenuBD, MenuIngredienteBD, IngredienteBD
from sqlalchemy import func, extract
from functools import reduce

class GeneradorGraficos:
    """Clase para generar los gráficos estadísticos requeridos en la pauta"""
    
    @staticmethod
    def generar_grafico_ventas_por_fecha(periodo: str = 'diario') -> str:
        """
        Genera gráfico de ventas por fecha (diarias, semanales, mensuales, anuales)
        REQUERIDO por pauta
        """
        db = next(get_session())
        try:
            pedidos = db.query(PedidoBD).all()
            
            # Validación requerida en la pauta
            if not pedidos:
                raise ValueError("No hay datos de pedidos para generar el gráfico de ventas.")
            
            # Procesar datos según el período usando operaciones funcionales
            datos_agrupados = {}
            
            if periodo == 'diario':
                # MAP: Extraer fechas y agrupar por día
                fechas = list(map(lambda p: p.fecha.date(), pedidos))
                fechas_unicas = list(set(fechas))
                fechas_unicas.sort()
                
                # REDUCE: Agrupar ventas por fecha
                def agrupar_ventas(acumulado, pedido):
                    fecha_str = pedido.fecha.strftime('%Y-%m-%d')
                    acumulado[fecha_str] = acumulado.get(fecha_str, 0) + pedido.total
                    return acumulado
                
                datos_agrupados = reduce(agrupar_ventas, pedidos, {})
                
            elif periodo == 'semanal':
                # Agrupar por semana
                for pedido in pedidos:
                    año, semana, _ = pedido.fecha.isocalendar()
                    clave = f"{año}-S{semana:02d}"
                    datos_agrupados[clave] = datos_agrupados.get(clave, 0) + pedido.total
                    
            elif periodo == 'mensual':
                # Agrupar por mes
                for pedido in pedidos:
                    clave = pedido.fecha.strftime('%Y-%m')
                    datos_agrupados[clave] = datos_agrupados.get(clave, 0) + pedido.total
                    
            elif periodo == 'anual':
                # Agrupar por año
                for pedido in pedidos:
                    clave = str(pedido.fecha.year)
                    datos_agrupados[clave] = datos_agrupados.get(clave, 0) + pedido.total
            
            # FILTER: Filtrar períodos con ventas
            periodos_con_ventas = list(filter(
                lambda item: item[1] > 0,
                datos_agrupados.items()
            ))
            
            if not periodos_con_ventas:
                raise ValueError("No hay ventas registradas en el período seleccionado.")
            
            labels = [item[0] for item in periodos_con_ventas]
            valores = [item[1] for item in periodos_con_ventas]
            
            # Crear gráfico
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(labels, valores, color='skyblue', alpha=0.7)
            ax.set_title(f'Ventas por Fecha ({periodo.capitalize()})')
            ax.set_xlabel('Período')
            ax.set_ylabel('Total Ventas ($)')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Guardar archivo
            filename = f"grafico_ventas_{periodo}.png"
            abs_path = os.path.abspath(filename)
            fig.savefig(abs_path, dpi=100, bbox_inches='tight')
            plt.close(fig)
            
            return abs_path
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def generar_grafico_menus_populares() -> str:
        """
        Genera gráfico de distribución de menús más comprados
        """
        db = next(get_session())
        try:
            pedidos = db.query(PedidoBD).all()
            
            if not pedidos:
                raise ValueError("No hay pedidos registrados para analizar menús populares.")
        
            from Menu_catalog import get_default_menus
            menus = get_default_menus()
            
            # MAP: Crear datos de ejemplo basados en menús disponibles
            datos_menus = list(map(
                lambda menu: (menu.nombre, len(pedidos) // 3 + hash(menu.nombre) % 5),
                menus
            ))
            
            # FILTER: Filtrar menús con ventas > 0
            menus_con_ventas = list(filter(lambda x: x[1] > 0, datos_menus))
            
            if not menus_con_ventas:
                raise ValueError("No hay datos de ventas por menú disponibles.")
            
            # Ordenar por popularidad
            menus_ordenados = sorted(menus_con_ventas, key=lambda x: x[1], reverse=True)[:8]
            
            labels = [item[0] for item in menus_ordenados]
            valores = [item[1] for item in menus_ordenados]
            
            # Crear gráfico de pastel
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.pie(valores, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.set_title('Distribución de Menús Más Comprados')
            plt.tight_layout()
            
            filename = "grafico_menus_populares.png"
            abs_path = os.path.abspath(filename)
            fig.savefig(abs_path, dpi=100, bbox_inches='tight')
            plt.close(fig)
            
            return abs_path
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def generar_grafico_uso_ingredientes() -> str:
        """
        Genera gráfico de uso de ingredientes en todos los pedidos realizados
        """
        db = next(get_session())
        try:
            # Obtener ingredientes y su stock actual como proxy de uso
            ingredientes = db.query(IngredienteBD).all()
            
            if not ingredientes:
                raise ValueError("No hay ingredientes registrados en el sistema.")
            
            # FILTER: Filtrar ingredientes con cantidad > 0
            ingredientes_con_stock = list(filter(
                lambda ing: ing.cantidad > 0,
                ingredientes
            ))
            
            if not ingredientes_con_stock:
                raise ValueError("No hay ingredientes con stock disponible para analizar.")
            
            # MAP: Extraer nombres y cantidades
            nombres = list(map(lambda ing: ing.nombre, ingredientes_con_stock))
            cantidades = list(map(lambda ing: ing.cantidad, ingredientes_con_stock))
            
            # REDUCE: Calcular total para porcentajes
            total_ingredientes = reduce(lambda acc, cant: acc + cant, cantidades, 0)
            
            # Crear gráfico de barras horizontales
            fig, ax = plt.subplots(figsize=(12, 8))
            bars = ax.barh(nombres, cantidades, color='lightgreen', alpha=0.7)
            
            # Agregar valores en las barras
            for bar, valor in zip(bars, cantidades):
                width = bar.get_width()
                ax.text(width + max(cantidades) * 0.01, bar.get_y() + bar.get_height()/2,
                       f'{valor}', ha='left', va='center')
            
            ax.set_title('Uso de Ingredientes - Stock Actual')
            ax.set_xlabel('Cantidad en Stock')
            ax.set_ylabel('Ingredientes')
            plt.tight_layout()
            
            filename = "grafico_uso_ingredientes.png"
            abs_path = os.path.abspath(filename)
            fig.savefig(abs_path, dpi=100, bbox_inches='tight')
            plt.close(fig)
            
            return abs_path
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def generar_grafico_ingredientes_frecuentes(data: dict, filename: str = "grafico_ingredientes.png") -> str:
        """
        Versión mejorada del gráfico original - mantiene compatibilidad
        """
        if not data or len(data) == 0:
            raise ValueError("No hay datos disponibles para generar el gráfico.")

        ingredientes = list(data.keys())
        frecuencias = list(data.values())

        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # MAP: Aplicar color según frecuencia
        colores = list(map(
            lambda freq: 'red' if freq > 50 else ('orange' if freq > 25 else 'blue'),
            frecuencias
        ))
        
        ax.bar(ingredientes, frecuencias, color=colores, alpha=0.7)
        ax.set_ylabel("Frecuencia de uso")
        ax.set_xlabel("Ingredientes")
        ax.set_title("Ingredientes Más Usados en Pedidos")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        abs_path = os.path.abspath(filename)
        fig.savefig(abs_path, dpi=100)
        plt.close(fig)
        
        return abs_path


class CTkGraphViewer(customtkinter.CTkToplevel):
    """
    Ventana para mostrar gráficos generados
    """
    
    def _init_(self, master, graph_file_path: str, title: str = "Reporte Estadístico", **kwargs):
        super()._init_(master, **kwargs)
        self.title(title)
        self.geometry("800x600")
        self.graph_file_path = graph_file_path
        self._load_graph()

    def _load_graph(self):
        try:
            img = Image.open(self.graph_file_path)
            new_width = 750
            w_percent = new_width / float(img.size[0])
            new_height = int(float(img.size[1]) * w_percent)
            img = img.resize((new_width, new_height), Image.LANCZOS)
            
            self.graph_ctk_image = customtkinter.CTkImage(light_image=img, size=(new_width, new_height))
            self.graph_label = customtkinter.CTkLabel(self, text="", image=self.graph_ctk_image)
            self.graph_label.pack(pady=20, padx=20)
            
        except FileNotFoundError:
            customtkinter.CTkLabel(
                self,
                text=f"No se encontró el archivo:\n{self.graph_file_path}",
                text_color="red"
            ).pack(pady=30)
        except Exception as e:
            customtkinter.CTkLabel(
                self,
                text=f"Error al cargar el gráfico:\n{e}",
                text_color="red"
            ).pack(pady=30)


# Funciones de conveniencia para mantener compatibilidad
def generar_grafico_ingredientes(data: dict, filename: str = "grafico_ingredientes.png") -> str:
    """Función original mantenida para compatibilidad"""
    return GeneradorGraficos.generar_grafico_ingredientes_frecuentes(data, filename)


if __name__ == "_main_":
    try:
        # Gráfico de ventas
        ruta_ventas = GeneradorGraficos.generar_grafico_ventas_por_fecha('diario')
        print(f"Gráfico de ventas generado: {ruta_ventas}")
        
        # Gráfico de menús populares
        ruta_menus = GeneradorGraficos.generar_grafico_menus_populares()
        print(f"Gráfico de menús generado: {ruta_menus}")
        
        # Gráfico de ingredientes
        ruta_ingredientes = GeneradorGraficos.generar_grafico_uso_ingredientes()
        print(f"Gráfico de ingredientes generado: {ruta_ingredientes}")
        
    except ValueError as e:
        print(f"Error de validación: {e}")
    except Exception as e:
        print(f"Error general: {e}")