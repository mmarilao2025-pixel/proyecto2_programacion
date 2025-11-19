import matplotlib.pyplot as plt
import customtkinter
from PIL import Image, ImageTk
import os


def generar_grafico_ingredientes(data: dict, filename: str = "grafico_ingredientes.png") -> str:
    """
    Genera un gráfico de barras con la frecuencia de ingredientes usados.
    Si no existen datos, lanza ValueError (la pauta exige mostrar un mensaje).
    Retorna la ruta absoluta del archivo PNG generado.
    """

    # Validación requerida en la pauta
    if not data or len(data) == 0:
        raise ValueError("No hay datos disponibles para generar el gráfico.")

    ingredientes = list(data.keys())
    frecuencias = list(data.values())

    # Crear figura simple (sin estilos extra)
    fig, ax = plt.subplots(figsize=(8, 5))

    # Gráfico de barras simple
    ax.bar(ingredientes, frecuencias)

    # Etiquetas
    ax.set_ylabel("Frecuencia de uso")
    ax.set_xlabel("Ingredientes")
    ax.set_title("Ingredientes más usados")

    # Rotar etiquetas del eje X
    plt.xticks(rotation=45, ha="right")

    # Ajuste automático
    plt.tight_layout()

    # Guardar imagen física
    abs_path = os.path.abspath(filename)
    fig.savefig(abs_path, dpi=100)
    plt.close(fig)  # liberar memoria

    return abs_path


class CTkGraphViewer(customtkinter.CTkToplevel):
    """
    Ventana para mostrar el gráfico generado por Matplotlib como PNG.
    """

    def __init__(self, master, graph_file_path: str, title: str = "Reporte de Ingredientes", **kwargs):
        super().__init__(master, **kwargs)
        self.title(title)
        self.geometry("800x600")

        self.graph_file_path = graph_file_path
        self._load_graph()

    def _load_graph(self):
        try:
            img = Image.open(self.graph_file_path)

            # Redimensionar imagen a un ancho fijo
            new_width = 750
            w_percent = new_width / float(img.size[0])
            new_height = int(float(img.size[1]) * w_percent)

            img = img.resize((new_width, new_height), Image.LANCZOS)

            # Convertir a imagen compatible con CustomTkinter
            self.graph_ctk_image = customtkinter.CTkImage(light_image=img, size=(new_width, new_height))

            # Mostrar imagen
            self.graph_label = customtkinter.CTkLabel(self, text="", image=self.graph_ctk_image)
            self.graph_label.pack(pady=20, padx=20)

        except FileNotFoundError:
            customtkinter.CTkLabel(
                self,
                text=f"❌ No se encontró el archivo:\n{self.graph_file_path}",
                text_color="red"
            ).pack(pady=30)

        except Exception as e:
            customtkinter.CTkLabel(
                self,
                text=f"❌ Error al cargar el gráfico:\n{e}",
                text_color="red"
            ).pack(pady=30)



#Ejemplo de prueba (Puedes eliminarlo en producción)

if __name__ == "__main__":

    # Datos de ejemplo para prueba
    datos_ejemplo = {
        'Tomate': 50,
        'Cebolla': 40,
        'Pollo': 60,
        'Lechuga': 20
    }

    try:
        ruta = generar_grafico_ingredientes(datos_ejemplo)

        app = customtkinter.CTk()
        app.geometry("400x200")

        def abrir():
            v = CTkGraphViewer(app, ruta)
            v.focus()

        btn = customtkinter.CTkButton(app, text="Ver Gráfico", command=abrir)
        btn.pack(pady=40)

        app.mainloop()

    except Exception as e:
        print("Error:", e)