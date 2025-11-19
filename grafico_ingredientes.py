import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import customtkinter
from PIL import Image, ImageTk
import os

# Generación de la imagen del gráfico (Matplotlib)
def generar_grafico_ingredientes(data: dict, filename: str = "grafico_ingredientes.png") -> str:
    """
    Genera un gráfico de barras a partir de datos de frecuencia de ingredientes.
    Retorna la ruta absoluta al archivo de imagen generado.
    """
    
    # Simulación de datos si no tienes la fuente real
    if not data:
        data = {
            'Tomate': 25,
            'Cebolla': 40,
            'Lechuga': 15,
            'Papas': 30,
            'Pollo': 50
        }

    ingredientes = list(data.keys())
    frecuencias = list(data.values())

    df = pd.DataFrame({'Ingrediente': ingredientes, 'Frecuencia': frecuencias})
    df = df.sort_values(by='Frecuencia', ascending=False)
    
    plt.style.use('seaborn-v0_8-pastel') # Un estilo visual agradable
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Crear el gráfico de barras
    bars = ax.bar(df['Ingrediente'], df['Frecuencia'], color=plt.cm.coolwarm(np.linspace(0.1, 0.9, len(df))))

    # Añadir etiquetas y título
    ax.set_ylabel('Frecuencia de Uso', fontsize=12)
    ax.set_xlabel('Ingrediente', fontsize=12)
    ax.set_title('Top 5 Ingredientes Más Usados en el Menú', fontsize=14, fontweight='bold')
    
    # Rotar etiquetas para mejor lectura
    plt.xticks(rotation=45, ha='right') 
    
    # Ajustar layout y guardar
    plt.tight_layout()
    
    # Guardar el gráfico como PNG
    abs_path = os.path.abspath(filename)
    fig.savefig(abs_path, dpi=100)
    plt.close(fig) # Cerrar la figura para liberar memoria
    return abs_path

# Visor de Gráficos (CustomTkinter)
class CTkGraphViewer(customtkinter.CTkToplevel):
    """
    Ventana para mostrar el gráfico PNG generado por Matplotlib.
    """
    def __init__(self, master, graph_file_path: str, title: str = "Reporte de Ingredientes", **kwargs):
        super().__init__(master, **kwargs)
        self.title(title)
        self.geometry("800x600")
        
        self.graph_file_path = graph_file_path
        
        self._load_graph()

    def _load_graph(self):
        try:
            # Abrir y redimensionar la imagen para que quepa en la ventana
            img = Image.open(self.graph_file_path)
            
            # Obtener dimensiones de la ventana para redimensionar la imagen (ej: 750px de ancho)
            new_width = 750 
            w_percent = (new_width / float(img.size[0]))
            new_height = int((float(img.size[1]) * float(w_percent)))
            
            # Redimensionar la imagen
            img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Crear el objeto CTkImage y Label
            self.graph_ctk_image = customtkinter.CTkImage(light_image=img, size=(new_width, new_height))
            
            self.graph_label = customtkinter.CTkLabel(self, text="", image=self.graph_ctk_image)
            self.graph_label.pack(pady=20, padx=20)
            
            # Añadir un mensaje de información
            info_label = customtkinter.CTkLabel(self, text="Gráfico de Matplotlib generado como imagen PNG.", 
                                                font=customtkinter.CTkFont(size=12, slant="italic"))
            info_label.pack(pady=(0, 10))

        except FileNotFoundError:
            error_label = customtkinter.CTkLabel(self, text=f"Error: No se encontró el archivo de gráfico en la ruta:\n{self.graph_file_path}", 
                                                 text_color="red")
            error_label.pack(pady=50)
        except Exception as e:
            error_label = customtkinter.CTkLabel(self, text=f"Ocurrió un error al cargar el gráfico: {e}", 
                                                 text_color="red")
            error_label.pack(pady=50)

# Ejemplo de uso (simulando la llamada desde la interfaz principal)
if __name__ == "__main__":
    
    # Generar la imagen del gráfico
    datos_ejemplo = {
        'Arroz': 100, 'Pollo': 85, 'Papas': 70, 
        'Tomate': 60, 'Queso': 55, 'Pescado': 40
    }
    try:
        ruta_grafico = generar_grafico_ingredientes(datos_ejemplo, "reporte_ingredientes.png")
        print(f"Gráfico generado en: {ruta_grafico}")
    
        # Inicializar la ventana principal de CustomTkinter
        app = customtkinter.CTk()
        app.title("Aplicación Principal")
        app.geometry("400x150")
        
        def mostrar_reporte():
            # Crear y mostrar la ventana del gráfico
            toplevel_window = CTkGraphViewer(app, ruta_grafico)
            toplevel_window.focus() # Enfocar la nueva ventana
            
        btn = customtkinter.CTkButton(app, text="Ver Reporte de Ingredientes", command=mostrar_reporte)
        btn.pack(pady=20)
        
        app.mainloop()

    except Exception as e:
        print(f"Error fatal en el ejemplo de Matplotlib/CTk: {e}")