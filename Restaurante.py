from ElementoMenu import CrearMenu
import customtkinter as ctk
from tkinter import ttk, Toplevel, Label, messagebox
from Ingrediente import Ingrediente
from Stock import Stock
import re
from PIL import Image
from CTkMessagebox import CTkMessagebox
from Pedido import Pedido
from BoletaFacade import BoletaFacade
import pandas as pd
from tkinter import filedialog
from Menu_catalog import get_default_menus
from menu_pdf import create_menu_pdf
from ctk_pdf_viewer import CTkPDFViewer
import os
from tkinter.font import nametofont
from grafico_ingredientes import generar_grafico_ingredientes, CTkGraphViewer
from conexion import get_session


class AplicacionConPestanas(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Gestión de ingredientes y pedidos")
        self.geometry("870x700")
        nametofont("TkHeadingFont").configure(size=14)
        nametofont("TkDefaultFont").configure(size=11)
        self.stock = Stock()
        self.menus_creados = set()
        self.pedido = Pedido()
        self.menus = get_default_menus()  
        self.tabview = ctk.CTkTabview(self,command=self.on_tab_change)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)
        self.crear_pestanas()

    def actualizar_treeview(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        for ingrediente in self.stock.lista_ingredientes:
            self.tree.insert("", "end", values=(ingrediente.nombre,ingrediente.unidad, ingrediente.cantidad))    

    def on_tab_change(self):
        selected_tab = self.tabview.get()

        if selected_tab == "carga de ingredientes":
            print('carga de ingredientes')

        elif selected_tab == "Stock":
            self.actualizar_treeview()

        elif selected_tab == "Pedido":
            self.actualizar_treeview_pedido()
            self.cargar_tarjetas_disponibles()


        elif selected_tab == "Carta restorante":
            print('Carta restorante')

        if selected_tab == "Boleta":
            self.actualizar_treeview()
            print('Boleta')   

        elif selected_tab == "Boleta":
            print('Boleta')

    def crear_pestanas(self):
        self.tab3 = self.tabview.add("carga de ingredientes")  
        self.tab1 = self.tabview.add("Stock")
        self.tab4 = self.tabview.add("Carta restorante")  
        self.tab2 = self.tabview.add("Pedido")
        self.tab5 = self.tabview.add("Boleta")
        self.tab6 = self.tabview.add("Gráfico")
        
        self.configurar_pestana1()
        self.configurar_pestana2()
        self.configurar_pestana3()
        self._configurar_pestana_crear_menu()
        self._configurar_pestana_ver_boleta()
        self.configurar_pestana_grafico()

    def configurar_pestana3(self):
        label = ctk.CTkLabel(self.tab3, text="Carga de archivo CSV")
        label.pack(pady=20)
        boton_cargar_csv = ctk.CTkButton(self.tab3, text="Cargar CSV", fg_color="#1976D2", text_color="white",command=self.cargar_csv)

        boton_cargar_csv.pack(pady=10)

        self.frame_tabla_csv = ctk.CTkFrame(self.tab3)
        self.frame_tabla_csv.pack(fill="both", expand=True, padx=10, pady=10)
        self.df_csv = None   
        self.tabla_csv = None

        self.boton_agregar_stock = ctk.CTkButton(self.frame_tabla_csv, text="Agregar al Stock", command=self.agregar_csv_al_stock )
        self.boton_agregar_stock.pack(side="bottom", pady=10)
 
    def agregar_csv_al_stock(self):
        if self.df_csv is None:
            CTkMessagebox(title="Error", message="Primero debes cargar un archivo CSV.", icon="warning")
            return

        if 'nombre' not in self.df_csv.columns or 'cantidad' not in self.df_csv.columns or 'unidad' not in self.df_csv.columns:
            CTkMessagebox(title="Error", message="El CSV debe tener columnas 'nombre', 'unidad' y 'cantidad'.", icon="warning")
            return
        
        try:
            # Usar el método agregar_ingrediente que ya funciona en Stock
            for _, row in self.df_csv.iterrows():
                nombre = str(row['nombre']).strip()
                unidad = str(row['unidad']).strip()
                cantidad = int(row['cantidad'])
                
                ingrediente = Ingrediente(nombre=nombre, unidad=unidad, cantidad=cantidad)
                self.stock.agregar_ingrediente(ingrediente)
            
            CTkMessagebox(title="Stock Actualizado", message="Ingredientes agregados al stock correctamente.", icon="info")
            self.actualizar_treeview()
            
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al agregar ingredientes al stock: {str(e)}", icon="cancel")

    def cargar_csv(self):
        archivo = filedialog.askopenfile(filetypes=[("Archivos CSV", "*.csv")])
        if not archivo:
            return

        # Lee el archivo CSV con una codificación
        DataFrame = pd.read_csv(archivo, encoding='utf-8', skipinitialspace=True, engine='python')
        
        # Limpia el encabezado de posibles caracteres extra
        DataFrame.columns = [col.replace('\ufeff', '').replace('ï»¿', '').strip() for col in DataFrame.columns]

        # Elimina espacios en nombres y unidades
        DataFrame['nombre'] = DataFrame['nombre'].astype(str).str.strip()
        DataFrame['unidad'] = DataFrame['unidad'].astype(str).str.strip()

        self.df_csv = DataFrame
        self.mostrar_dataframe_en_tabla(DataFrame)


    def mostrar_dataframe_en_tabla(self, df):
        if self.tabla_csv:
            self.tabla_csv.destroy()

        print(list(df.columns))
        self.tabla_csv = ttk.Treeview(self.frame_tabla_csv, columns=list(df.columns), show="headings")
        for col in df.columns:
            self.tabla_csv.heading(col, text=col)
            self.tabla_csv.column(col, width=100, anchor="center")


        for _, row in df.iterrows():
            self.tabla_csv.insert("", "end", values=list(row))

        self.tabla_csv.pack(expand=True, fill="both", padx=10, pady=10)

    def actualizar_treeview_pedido(self):
        for item in self.treeview_menu.get_children():
            self.treeview_menu.delete(item)

        for menu in self.pedido.menus:
            self.treeview_menu.insert("", "end", values=(menu.nombre, menu.cantidad, f"${menu.precio:.2f}"))
            
    def _configurar_pestana_crear_menu(self):
        contenedor = ctk.CTkFrame(self.tab4)
        contenedor.pack(expand=True, fill="both", padx=10, pady=10)

        boton_menu = ctk.CTkButton(
            contenedor,
            text="Generar Carta (PDF)",
            command=self.generar_y_mostrar_carta_pdf
        )
        boton_menu.pack(pady=10)

        self.pdf_frame_carta = ctk.CTkFrame(contenedor)
        self.pdf_frame_carta.pack(expand=True, fill="both", padx=10, pady=10)

        self.pdf_viewer_carta = None
    def generar_y_mostrar_carta_pdf(self):
        try:
            pdf_path = "carta.pdf"
            create_menu_pdf(self.menus, pdf_path,
                titulo_negocio="Restaurante",
                subtitulo="Carta Primavera 2025",
                moneda="$")
            
            if self.pdf_viewer_carta is not None:
                try:
                    self.pdf_viewer_carta.pack_forget()
                    self.pdf_viewer_carta.destroy()
                except Exception:
                    pass
                self.pdf_viewer_carta = None

            abs_pdf = os.path.abspath(pdf_path)
            self.pdf_viewer_carta = CTkPDFViewer(self.pdf_frame_carta, file=abs_pdf)
            self.pdf_viewer_carta.pack(expand=True, fill="both")

        except Exception as e:
            CTkMessagebox(title="Error", message=f"No se pudo generar/mostrar la carta.\n{e}", icon="warning")

    def _configurar_pestana_ver_boleta(self):
        contenedor = ctk.CTkFrame(self.tab5)
        contenedor.pack(expand=True, fill="both", padx=10, pady=10)
    
        boton_boleta = ctk.CTkButton(
            contenedor,
            text="Mostrar Boleta (PDF)",
            command=self.mostrar_boleta
        )
        boton_boleta.pack(pady=10)
    
        self.pdf_frame_boleta = ctk.CTkFrame(contenedor)
        self.pdf_frame_boleta.pack(expand=True, fill="both", padx=10, pady=10)
    
        self.pdf_viewer_boleta = None
        

    def mostrar_boleta(self):
        pdf_path = "boleta.pdf"

        if not os.path.exists(pdf_path):
            CTkMessagebox(title="Error", message="No se ha generado ninguna boleta aún. Debes generar una boleta desde la pestaña 'Pedido'.", icon="warning")
            return
        try:  #eliminar el visor anterior (ventanita, para actualizarlo bien)
            if self.pdf_viewer_boleta is not None:
                try:
                    self.pdf_viewer_boleta.pack_forget()
                    self.pdf_viewer_boleta.destroy()
                except Exception:
                    pass
                    self.pdf_viewer_boleta = None  

            abs_pdf = os.path.abspath(pdf_path) # obtener la ruta absoluta del PDF

             #crear el nuevo visor con el PDF actualizado
            self.pdf_viewer_boleta = CTkPDFViewer(self.pdf_frame_boleta, file=abs_pdf)
            self.pdf_viewer_boleta.pack(expand=True, fill="both")

        except Exception as e: # si la carga del pdf falla mostrar error
            CTkMessagebox(title="Error", message=f"No se pudo mostrar la boleta.\n{e}", icon="warning")

    def configurar_pestana1(self):
        # Dividir la Pestaña 1 en two frames
        frame_formulario = ctk.CTkFrame(self.tab1)
        frame_formulario.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        frame_treeview = ctk.CTkFrame(self.tab1)
        frame_treeview.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Formulario en el primer frame
        label_nombre = ctk.CTkLabel(frame_formulario, text="Nombre del Ingrediente:")
        label_nombre.pack(pady=5)
        self.entry_nombre = ctk.CTkEntry(frame_formulario)
        self.entry_nombre.pack(pady=5)

        label_cantidad = ctk.CTkLabel(frame_formulario, text="Unidad:")
        label_cantidad.pack(pady=5)
        self.combo_unidad = ctk.CTkComboBox(frame_formulario, values=["unid"])
        self.combo_unidad.pack(pady=5)

        label_cantidad = ctk.CTkLabel(frame_formulario, text="Cantidad:")
        label_cantidad.pack(pady=5)
        self.entry_cantidad = ctk.CTkEntry(frame_formulario)
        self.entry_cantidad.pack(pady=5)

        self.boton_ingresar = ctk.CTkButton(frame_formulario, text="Ingresar Ingrediente")
        self.boton_ingresar.configure(command=self.ingresar_ingrediente)
        self.boton_ingresar.pack(pady=10)

        self.boton_eliminar = ctk.CTkButton(frame_treeview, text="Eliminar Ingrediente", fg_color="black", text_color="white")
        self.boton_eliminar.configure(command=self.eliminar_ingrediente)
        self.boton_eliminar.pack(pady=10)

        self.tree = ttk.Treeview(self.tab1, columns=("Nombre", "Unidad","Cantidad"), show="headings",height=25)
        
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Unidad", text="Unidad")
        self.tree.heading("Cantidad", text="Cantidad")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        self.boton_generar_menu = ctk.CTkButton(frame_treeview, text="Generar Menú", command=self.generar_menus)
        self.boton_generar_menu.pack(pady=10)
    
    def ingresar_ingrediente(self):
        # Agrega un nuevo ingrediente al stock desde el formulario
        nombre = self.entry_nombre.get().strip()
        cantidad_str = self.entry_cantidad.get().strip()
        # Validaciones del formulario
        if not nombre:
            CTkMessagebox(title="Error", message="El nombre del ingrediente no puede estar vacío.", icon="warning")
            return
        
        if not self.validar_nombre(nombre):
            return
        
        if not cantidad_str:
            CTkMessagebox(title="Error", message="La cantidad no puede estar vacía.", icon="warning")
            return
        
        if not self.validar_cantidad(cantidad_str):
            return
        
        try:
            cantidad = int(cantidad_str)
            if cantidad <= 0:
                CTkMessagebox(title="Error", message="La cantidad debe ser un número entero positivo.", icon="warning")
                return
        except ValueError:
            CTkMessagebox(title="Error", message="La cantidad debe ser un número entero válido.", icon="warning")
            return
        
        # Crea y agrega el ingrediente ingresado 
        nuevo_ingrediente = Ingrediente(
            nombre=nombre,
            unidad="unid",  # Siempre "unid"
            cantidad=cantidad
        )
        self.stock.agregar_ingrediente(nuevo_ingrediente)
        
        # Limpia los campos del formulario
        self.entry_nombre.delete(0, 'end')
        self.entry_cantidad.delete(0, 'end')
        # Actualiza el treeview
        self.actualizar_treeview()
        CTkMessagebox(title="Éxito", message=f"Ingrediente '{nombre}' agregado correctamente.", icon="info")

    def tarjeta_click(self, event, menu):
        # Calcular cuántos de este menú ya están en el pedido
        cantidad_en_pedido = 0
        for item in self.pedido.menus:
            if item.nombre == menu.nombre:
                cantidad_en_pedido = item.cantidad
                break
        
        # Verificar stock suficiente para (cantidad_en_pedido + 1) menús
        suficiente_stock = True
        ingredientes_insuficientes = []
        
        for ingrediente_necesario in menu.ingredientes:
            nombre_necesario = ingrediente_necesario.nombre.strip().lower()
            unidad_necesaria = ingrediente_necesario.unidad.strip().lower()
            cantidad_necesaria_por_menu = int(ingrediente_necesario.cantidad)
            cantidad_total_necesaria = cantidad_necesaria_por_menu * (cantidad_en_pedido + 1)

            encontrado = False
            for ingrediente_stock in self.stock.lista_ingredientes:
                nombre_stock = ingrediente_stock.nombre.strip().lower()
                unidad_stock = ingrediente_stock.unidad.strip().lower()
                
                if nombre_necesario == nombre_stock and unidad_necesaria == unidad_stock:
                    encontrado = True
                    if int(ingrediente_stock.cantidad) < cantidad_total_necesaria:
                        suficiente_stock = False
                        ingredientes_insuficientes.append({
                            'nombre': nombre_necesario,
                            'necesario': cantidad_total_necesaria,
                            'disponible': int(ingrediente_stock.cantidad)
                        })
                    break
            
            if not encontrado:
                suficiente_stock = False
                ingredientes_insuficientes.append({
                    'nombre': nombre_necesario,
                    'necesario': cantidad_total_necesaria,
                    'disponible': 0
                })
            
            if not suficiente_stock:
                break

        if suficiente_stock:
            # NUEVO: Descontar los ingredientes usando el método del Stock que actualiza la BD
            requerimientos = {}
            for ingrediente_necesario in menu.ingredientes:
                nombre_ing = ingrediente_necesario.nombre.strip()
                cantidad_necesaria = int(ingrediente_necesario.cantidad)
                requerimientos[nombre_ing] = cantidad_necesaria
            
            # Usar el método descontar_stock que actualiza la base de datos
            if self.stock.descontar_stock(requerimientos):
                # Agregar 1 menú al pedido
                menu_a_agregar = CrearMenu(menu.nombre, menu.ingredientes, menu.precio, getattr(menu, "icono_path", None))
                self.pedido.agregar_menu(menu_a_agregar)

                # Actualizar Treeview y total
                self.actualizar_treeview_pedido()
                total = self.pedido.calcular_total()
                self.label_total.configure(text=f"Total: ${total:.2f}")
                
                # Actualizar disponibilidad de tarjetas
                self.cargar_tarjetas_disponibles()

                # 🔥 Actualizar la pestaña de Stock inmediatamente
                self.actualizar_treeview()
                
                CTkMessagebox(
                    title="Éxito",
                    message=f"'{menu.nombre}' agregado al pedido. Stock actualizado.",
                    icon="info"
                )
            else:
                CTkMessagebox(
                    title="Error",
                    message="No se pudo actualizar el stock en la base de datos.",
                    icon="cancel"
                )
                
        else:
            # Mostrar mensaje detallado de qué ingredientes faltan
            mensaje = f"No hay suficientes ingredientes para preparar '{menu.nombre}'.\n\n"
            for ing in ingredientes_insuficientes:
                mensaje += f"- {ing['nombre']}: Necesario {ing['necesario']}, Disponible {ing['disponible']}\n"
            
            CTkMessagebox(
                title="Stock Insuficiente",
                message=mensaje,
                icon="warning"
            )

    def cargar_icono_menu(self, ruta_icono):
        imagen = Image.open(ruta_icono)
        icono_menu = ctk.CTkImage(imagen, size=(64, 64))
        return icono_menu
    
    def generar_menus(self):
        pass

    def eliminar_menu(self):
        seleccion = self.treeview_menu.selection()

        if not seleccion:
            CTkMessagebox(title="Error", message="Por favor selecciona un menú para eliminar.", icon="warning")
            return

        item = seleccion[0]
        valores = self.treeview_menu.item(item, 'values')
        nombre_menu = valores[0]
        cantidad_eliminar = int(valores[1])

        # Confirmar eliminación
        respuesta = CTkMessagebox(
            title="Confirmar Eliminación",
            message=f"¿Estás seguro de que quieres eliminar {cantidad_eliminar} '{nombre_menu}' del pedido?",
            icon="question",
            option_1="Cancelar",
            option_2="Eliminar"
        )

        if respuesta.get() != "Eliminar":
            return

        # Buscar el menú en el pedido
        menu_encontrado = None
        for i, menu in enumerate(self.pedido.menus):
            if menu.nombre == nombre_menu:
                menu_encontrado = menu
                break

        if menu_encontrado:
            # SOLUCIÓN: Usar el método descontar_stock pero con cantidades NEGATIVAS para restaurar
            requerimientos_restaurar = {}
            for ingrediente_necesario in menu_encontrado.ingredientes:
                nombre_ing = ingrediente_necesario.nombre.strip()
                # Cantidad NEGATIVA para restaurar (esto suma en lugar de restar)
                cantidad_restaurar = -int(ingrediente_necesario.cantidad) * cantidad_eliminar
                requerimientos_restaurar[nombre_ing] = cantidad_restaurar
            
            # Usar el mismo método que ya funciona bien para actualizar la BD
            self.stock.descontar_stock(requerimientos_restaurar)
            
            # Eliminar el menú del pedido
            self.pedido.menus = [m for m in self.pedido.menus if m.nombre != nombre_menu]

        # Actualizar vistas
        self.actualizar_treeview_pedido()
        total = self.pedido.calcular_total()
        self.label_total.configure(text=f"Total: ${total:.2f}")
        self.cargar_tarjetas_disponibles()
        self.actualizar_treeview()
        
        CTkMessagebox(title="Éxito", message=f"{cantidad_eliminar} '{nombre_menu}' eliminados del pedido.", icon="info")

    def generar_boleta(self):
        if not self.pedido.menus:
            CTkMessagebox(title="Error", message="No hay menús en el pedido para generar una boleta.", icon="warning")
            return

        try:
            # OBTENER CLIENTE SELECCIONADO
            cliente_rut = self.obtener_rut_cliente_seleccionado()
            
            # PROCESAR COMPRA CON CLIENTE
            pedido_procesado = self.pedido.procesar_compra(cliente_rut)
            
            if not pedido_procesado:
                CTkMessagebox(title="Error", message="No se pudo procesar la compra. Verifique el stock.", icon="cancel")
                return

            # GENERAR BOLETA
            boleta_facade = BoletaFacade(self.pedido)
            pdf_path = boleta_facade.generar_boleta()

            # Mostrar mensaje de éxito con info del cliente
            cliente_nombre = self.combo_clientes.get().split("(")[0].strip()
            CTkMessagebox(
                title="Boleta Generada", 
                message=f"Boleta para {cliente_nombre} generada en: boleta.pdf", 
                icon="info"
            )

            # Limpiar pedido
            self.pedido.menus = []
            self.actualizar_treeview_pedido()
            self.label_total.configure(text="Total: $0.00")
            self.cargar_tarjetas_disponibles()  # Actualizar disponibilidad

        except Exception as e:
            CTkMessagebox(title="Error al Generar Boleta", message=f"Ocurrió un error al generar la boleta.\n{e}", icon="cancel")

    def configurar_pestana2(self):
        frame_superior = ctk.CTkFrame(self.tab2)
        frame_superior.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        frame_intermedio = ctk.CTkFrame(self.tab2)
        frame_intermedio.pack(side="top", fill="x", padx=10, pady=5)

        global tarjetas_frame
        tarjetas_frame = ctk.CTkFrame(frame_superior)
        tarjetas_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.boton_eliminar_menu = ctk.CTkButton(frame_intermedio, text="Eliminar Menú", command=self.eliminar_menu)
        self.boton_eliminar_menu.pack(side="right", padx=10)

        self.label_total = ctk.CTkLabel(frame_intermedio, text="Total: $0.00", anchor="e", font=("Helvetica", 12, "bold"))
        self.label_total.pack(side="right", padx=10)

        frame_inferior = ctk.CTkFrame(self.tab2)
        frame_inferior.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)

        self.treeview_menu = ttk.Treeview(frame_inferior, columns=("Nombre", "Cantidad", "Precio Unitario"), show="headings")
        self.treeview_menu.heading("Nombre", text="Nombre del Menú")
        self.treeview_menu.heading("Cantidad", text="Cantidad")
        self.treeview_menu.heading("Precio Unitario", text="Precio Unitario")
        self.treeview_menu.pack(expand=True, fill="both", padx=10, pady=10)

        self.boton_generar_boleta=ctk.CTkButton(frame_inferior,text="Generar Boleta",command=self.generar_boleta)
        self.boton_generar_boleta.pack(side="bottom",pady=10)

            # AGREGAR: Selección de cliente
        frame_cliente = ctk.CTkFrame(frame_intermedio)
        frame_cliente.pack(side="left", fill="x", padx=10, pady=5)
        
        label_cliente = ctk.CTkLabel(frame_cliente, text="Cliente:")
        label_cliente.pack(side="left", padx=5)
        
        self.combo_clientes = ctk.CTkComboBox(
            frame_cliente, 
            values=self.obtener_clientes_combo(),
            width=200
        )
        self.combo_clientes.pack(side="left", padx=5)
        
        self.boton_actualizar_clientes = ctk.CTkButton(
            frame_cliente, 
            text="Actualizar", 
            command=self.actualizar_lista_clientes,
            width=80
        )
        self.boton_actualizar_clientes.pack(side="left", padx=5)

    def obtener_clientes_combo(self):
        db = next(get_session())
        try:
            from crud.cliente_crud import ClienteCRUD
            clientes = ClienteCRUD.leer_clientes(db)
            return [f"{c.nombre} ({c.rut})" for c in clientes] if clientes else ["Cliente General (11111111-1)"]
        except Exception as e:
            print(f"Error al cargar clientes: {e}")
            return ["Cliente General (11111111-1)"]
        finally:
            db.close()

    def actualizar_lista_clientes(self):
        """Actualiza la lista de clientes en el ComboBox"""
        self.combo_clientes.configure(values=self.obtener_clientes_combo())
        CTkMessagebox(title="Éxito", message="Lista de clientes actualizada", icon="info")

    def obtener_rut_cliente_seleccionado(self):
        """Extrae el RUT del cliente seleccionado en el ComboBox"""
        seleccion = self.combo_clientes.get()
        if seleccion and "(" in seleccion and ")" in seleccion:
            return seleccion.split("(")[1].split(")")[0]
        return "11111111-1"  # Valor por defecto

    def crear_tarjeta(self, menu):
        num_tarjetas = len(self.menus_creados)
        fila = 0
        columna = num_tarjetas

        tarjeta = ctk.CTkFrame(
            tarjetas_frame,
            corner_radius=10,
            border_width=1,
            border_color="#4CAF50",
            width=64,
            height=140,
            fg_color="gray",
        )
        tarjeta.grid(row=fila, column=columna, padx=15, pady=15, sticky="nsew")

        tarjeta.bind("<Button-1>", lambda event: self.tarjeta_click(event, menu))
        tarjeta.bind("<Enter>", lambda event: tarjeta.configure(border_color="#FF0000"))
        tarjeta.bind("<Leave>", lambda event: tarjeta.configure(border_color="#4CAF50"))

        if getattr(menu, "icono_path", None):
            try:
                icono = self.cargar_icono_menu(menu.icono_path)
                imagen_label = ctk.CTkLabel(
                    tarjeta, image=icono, width=64, height=64, text="", bg_color="transparent"
                )
                imagen_label.image = icono
                imagen_label.pack(anchor="center", pady=5, padx=10)
                imagen_label.bind("<Button-1>", lambda event: self.tarjeta_click(event, menu))
            except Exception as e:
                print(f"No se pudo cargar la imagen '{menu.icono_path}': {e}")

        texto_label = ctk.CTkLabel(
            tarjeta,
            text=f"{menu.nombre}",
            text_color="black",
            font=("Helvetica", 12, "bold"),
            bg_color="transparent",
        )
        texto_label.pack(anchor="center", pady=1)
        texto_label.bind("<Button-1>", lambda event: self.tarjeta_click(event, menu))

    def validar_nombre(self, nombre):
        if re.match(r"^[a-zA-Z\s]+$", nombre):
            return True
        else:
            CTkMessagebox(title="Error de Validación", message="El nombre debe contener solo letras y espacios.", icon="warning")
            return False

    def validar_cantidad(self, cantidad):
        #Valida que la cantidad sea un número entero positivo
        if cantidad.isdigit():
            if int(cantidad) > 0:
                return True
            else:
                CTkMessagebox(title="Error de Validación", message="La cantidad debe ser mayor a 0.", icon="warning")
                return False
        else:
            CTkMessagebox(title="Error de Validación", message="La cantidad debe ser un número entero positivo.", icon="warning")
            return False

    def eliminar_ingrediente(self):
        # Elimina el ingrediente seleccionado en el treeview
        seleccion = self.tree.selection()
        
        if not seleccion:
            CTkMessagebox(title="Error", message="Por favor, selecciona un ingrediente para eliminar.", icon="warning")
            return
        
        # Obtiene el nombre del ingrediente selecionado
        item = seleccion[0]
        valores = self.tree.item(item, 'values')
        nombre_ingrediente = valores[0]
        
        # Confirma la eliminación del ingrediente
        respuesta = CTkMessagebox(
            title="Confirmar Eliminación", 
            message=f"¿Estás seguro de que quieres eliminar '{nombre_ingrediente}' del stock?",
            icon="question", 
            option_1="Cancelar", 
            option_2="Eliminar"
        )
        
        if respuesta.get() == "Eliminar":
            self.stock.eliminar_ingrediente(nombre_ingrediente)
            self.actualizar_treeview()
            CTkMessagebox(title="Éxito", message=f"Ingrediente '{nombre_ingrediente}' eliminado correctamente.", icon="info")

    def actualizar_treeview(self):
        # Limpiar el treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insertar los ingredientes actualizados
        for ingrediente in self.stock.lista_ingredientes:
            self.tree.insert("", "end", values=(ingrediente.nombre, ingrediente.unidad, ingrediente.cantidad))

    def menu_disponible(self, menu):
        for ingrediente_necesario in menu.ingredientes:
            nombre_necesario = ingrediente_necesario.nombre.strip().lower()
            cantidad_necesaria = int(ingrediente_necesario.cantidad)
            encontrado = False
            for ingrediente_stock in self.stock.lista_ingredientes:
                nombre_stock = ingrediente_stock.nombre.strip().lower()
                if nombre_necesario == nombre_stock:
                    encontrado = True
                    if int(ingrediente_stock.cantidad) < cantidad_necesaria:
                        return False
                    break
            if not encontrado:
                return False
        return True

    
    def cargar_tarjetas_disponibles(self):
        # Limpiar tarjetas previas
        for widget in tarjetas_frame.winfo_children():
            widget.destroy()
        
        self.menus_creados.clear()

        for menu in self.menus:
            if self.menu_disponible(menu):
                self.crear_tarjeta(menu)
                self.menus_creados.add(menu.nombre)

    def configurar_pestana_grafico(self):
        frame = ctk.CTkFrame(self.tab6)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        label = ctk.CTkLabel(frame, text="Gráfico de Ingredientes", font=("Helvetica", 16, "bold"))
        label.pack(pady=20)

        # Botón para generar el gráfico
        boton_generar = ctk.CTkButton(
            frame, 
            text="Generar Gráfico de Stock", 
            command=self.generar_grafico_stock
        )
        boton_generar.pack(pady=10)

        # Etiqueta informativa
        info_label = ctk.CTkLabel(
            frame, 
            text="Haz clic en el botón para generar un gráfico con los ingredientes en stock",
            text_color="gray"
        )
        info_label.pack(pady=5)

    def generar_grafico_stock(self):
        try:
            # 1. Preparar datos del stock para el gráfico
            datos_grafico = {}
            for ingrediente in self.stock.lista_ingredientes:
                datos_grafico[ingrediente.nombre] = ingrediente.cantidad
            
            # 2. Generar el gráfico usando tu función
            ruta_grafico = generar_grafico_ingredientes(datos_grafico)
            
            # 3. Mostrar el gráfico en ventana emergente
            ventana_grafico = CTkGraphViewer(self, ruta_grafico, title="Gráfico de Stock - Ingredientes")
            ventana_grafico.focus()
            
        except ValueError as e:
            CTkMessagebox(title="Error", message=str(e), icon="warning")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al generar el gráfico: {str(e)}", icon="cancel")




if __name__ == "__main__":
    import customtkinter as ctk
    from tkinter import ttk

    ctk.set_appearance_mode("Dark")  
    ctk.set_default_color_theme("blue") 
    ctk.set_widget_scaling(1.0)
    ctk.set_window_scaling(1.0)

    app = AplicacionConPestanas()

    try:
        style = ttk.Style(app)   
        style.theme_use("clam")
    except Exception:
        pass

    app.mainloop()