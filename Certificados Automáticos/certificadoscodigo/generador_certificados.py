import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import os
import sys
from datetime import datetime
import textwrap  # Para auto-ajustar el texto del proyecto

# --- Configuración de Archivos ---
DATA_FOLDER = "datos"
TEMPLATE_FOLDER = "plantilla"
DATA_FILENAME = "datos.xlsx" 
TEMPLATE_FILENAME = "Plantilla certificado.png"

DATA_FILE = os.path.join(DATA_FOLDER, DATA_FILENAME)
TEMPLATE_FILE = os.path.join(TEMPLATE_FOLDER, TEMPLATE_FILENAME)

OUTPUT_FOLDER = "certificados_generados" 

# --- Configuración de Texto Estático ---
TEXTO_INTRO = "La Facultad de Ingeniería Industrial Seccional Villavicencio hace constar que el estudiante:"
TEXTO_PONENTE = "Participó como ponente en modalidad Póster con el Proyecto:"
TEXTO_ESTUDIO = "estudio realizado en el espacio académico de"
# -------------------------------------

# ----- ¡AJUSTE FINAL: MÁS ARRIBA Y MÁS COMPACTO! -----
# --- Configuración de Posiciones (en PÍXELES ORIGINALES) ---
# (Posición de inicio alta y segura, "más pegado al título")
Y_START_PIXEL = 790 # <-- ¡MÁS ALTO AÚN! (Antes 760)
# -----------------------------------------------

def clean_filename(name):
    """Limpia un nombre para que sea un nombre de archivo seguro."""
    name = str(name).replace(' ', '_').replace('ñ', 'n').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    return "".join(c for c in name if c.isalnum() or c == '_').lower()

def clean_data(text):
    """Limpia el texto de comillas extra o espacios."""
    if isinstance(text, str):
        return text.strip().strip('"').strip("'").strip()
    return str(text)

def clean_code(code):
    """Convierte el código a string, manejando si se lee como float (ej. 12345.0)"""
    try:
        return str(int(float(code)))
    except (ValueError, TypeError):
        return str(code).strip()

def generar_certificado(nombre, codigo, proyecto, espacio, template_path, output_path, template_pixel_size, page_size):
    """
    Genera un único certificado en PDF escalando todo a un
    tamaño de página estándar (Hoja Carta horizontal).
    """
    page_width, page_height = page_size
    tpl_width, tpl_height = template_pixel_size

    c = canvas.Canvas(output_path, pagesize=page_size)
    
    # 1. Dibujar la plantilla como fondo
    c.drawImage(template_path, 0, 0, width=page_width, height=page_height)

    # 2. Función interna para escalar las coordenadas Y
    def scale_y(y_pixel):
        """Convierte una coordenada Y de píxel a punto de PDF."""
        return (y_pixel / tpl_height) * page_height

    # 3. Configurar fuentes y X central
    x_center = page_width / 2
    
    # 4. Escribir los datos con espaciado dinámico y fuentes más pequeñas
    
    # Definimos la posición Y de inicio (en puntos de PDF)
    current_y = scale_y(Y_START_PIXEL) # <-- Empezamos MÁS ARRIBA

    # --- Texto estático: Intro ---
    c.setFont('Helvetica', 11) # (Fuente pequeña)
    c.setFillColor(colors.HexColor('#000000'))
    c.drawCentredString(x_center, current_y, TEXTO_INTRO)
    current_y -= 30 # <-- Espacio COMPACTO

    # --- Nombre del estudiante ---
    c.setFont('Helvetica-Bold', 18) # (Fuente pequeña)
    c.drawCentredString(x_center, current_y, nombre.upper())
    current_y -= 22 # <-- Espacio COMPACTO

    # --- Código del estudiante ---
    c.setFont('Helvetica', 12) # (Fuente pequeña)
    c.setFillColor(colors.HexColor('#444444'))
    c.drawCentredString(x_center, current_y, f"Con Código o Identificación: {codigo}")
    current_y -= 25 # <-- Espacio COMPACTO

    # --- Texto estático: Ponente ---
    c.setFont('Helvetica', 11) # (Fuente pequeña)
    c.setFillColor(colors.HexColor('#000000'))
    c.drawCentredString(x_center, current_y, TEXTO_PONENTE)
    current_y -= 22 # <-- Espacio COMPACTO

    # --- Nombre del Proyecto (con auto-ajuste/wrap) ---
    c.setFont('Helvetica-Bold', 14) # (Fuente pequeña)
    c.setFillColor(colors.HexColor('#444444'))
    
    proyecto_text = f'"{proyecto.upper()}"'
    MAX_LINE_LENGTH = 65  # Máximo 65 caracteres por línea
    lines = textwrap.wrap(proyecto_text, width=MAX_LINE_LENGTH)
    line_height = 18 # Espacio entre líneas del proyecto (fuente 14 + 4)
    
    for line in lines:
        c.drawCentredString(x_center, current_y, line)
        current_y -= line_height # Mover Y para cada línea del proyecto

    # --- Siguientes textos con posición dinámica ---
    
    current_y -= 24 # <-- Espacio COMPACTO

    # --- Texto estático: Estudio ---
    c.setFont('Helvetica', 11) # (Fuente pequeña)
    c.setFillColor(colors.HexColor('#000000'))
    c.drawCentredString(x_center, current_y, TEXTO_ESTUDIO)
    current_y -= 22 # <-- Espacio COMPACTO

    # --- Espacio Académico ---
    c.setFont('Helvetica-Bold', 12) # (Fuente pequeña)
    c.drawCentredString(x_center, current_y, espacio.upper())
    current_y -= 25 # <-- Espacio COMPACTO

    # --- Fecha Automática ---
    hoy = datetime.now()
    meses_es = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
                "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    dia = hoy.day
    mes = meses_es[hoy.month - 1] 
    ano = hoy.year
    fecha_dinamica = f"El certificado es otorgado el día {dia} de {mes} de {ano}"

    c.setFont('Helvetica', 11) # (Fuente pequeña)
    c.drawCentredString(x_center, current_y, fecha_dinamica)
    
    # 5. Guardar el PDF
    c.save()
    print(f"Certificado generado para: {nombre}")

# --- Función Principal ---
def main():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Carpeta '{OUTPUT_FOLDER}' creada.")
        
    NEW_PAGE_SIZE = landscape(letter)

    # 2. Obtener dimensiones de la plantilla
    try:
        with Image.open(TEMPLATE_FILE) as img:
            template_pixel_size = img.size 
        print(f"Plantilla '{TEMPLATE_FILE}' cargada. Dimensiones en píxeles: {template_pixel_size}")
    except FileNotFoundError:
        print(f"--- ERROR CRÍTICO (PLANTILLA) ---")
        print(f"No se encontró el archivo de plantilla: '{TEMPLATE_FILE}'")
        sys.exit(1) 

    # 3. Cargar datos del EXCEL
    try:
        # Leemos la hoja "Datos"
        df = pd.read_excel(DATA_FILE, sheet_name="Datos") 
        
        df.columns = df.columns.str.strip()
        print(f"Archivo de datos '{DATA_FILE}' (Hoja: 'Datos') cargado exitosamente.")
        
    except FileNotFoundError:
        print(f"--- ERROR CRÍTICO (DATOS) ---")
        print(f"No se encontró el archivo de datos: '{DATA_FILE}'")
        sys.exit(1) 
    except ImportError:
        print(f"--- ERROR DE LIBRERÍA (openpyxl) ---")
        print("Solución: En tu terminal, ejecuta: pip install openpyxl")
        sys.exit(1)
    except Exception as e:
        print(f"--- ERROR CRÍTICO LEYENDO EL EXCEL ---")
        print(f"Error: {e}")
        print("Solución: Asegúrate de que tu hoja de Excel se llame exactamente 'Datos' (con D mayúscula).")
        sys.exit(1) 

    # Columnas de estudiantes a procesar
    student_columns = [
        ('Nombre completo del estudiante 1', 'Código del estudiante 1'),
        ('Nombre completo del estudiante 2', 'Código del estudiante 2'),
        ('Nombre completo del estudiante 3', 'Código del estudiante 3'),
        ('Nombre completo del estudiante 4', 'Código del estudiante 4')
    ]
    
    total_certificados = 0
    errores_columna = 0

    # 4. Iterar sobre cada FILA (proyecto)
    for index, row in df.iterrows():
        try:
            proyecto = clean_data(row['Nombre del Proyecto'])
            espacio = clean_data(row['Selecciona el espacio académico'])
        except KeyError as e:
            if errores_columna == 0: 
                print(f"--- ERROR DE LECTURA DE COLUMNA ---")
                print(f"No se encontró la columna {e} en tu hoja 'Datos'.")
            errores_columna += 1
            continue 

        if pd.isna(proyecto) or pd.isna(espacio) or not proyecto or not espacio:
            print(f"Omitiendo fila {index+2} por falta de Proyecto o Espacio Académico.")
            continue

        # 5. Iterar sobre cada ESTUDIANTE (los 4 integrantes) dentro de la fila
        for nombre_col, codigo_col in student_columns:
            
            # Lógica Anti-NaN
            raw_nombre = row.get(nombre_col)
            raw_codigo = row.get(codigo_col)

            if pd.notna(raw_nombre) and pd.notna(raw_codigo):
                
                nombre = clean_data(raw_nombre)
                codigo = clean_code(raw_codigo)

                # Revisión de strings vacíos
                if nombre and nombre.strip() and codigo and str(codigo).strip():
                    
                    output_filename = os.path.join(OUTPUT_FOLDER, f"certificado_{clean_filename(nombre)}_{clean_filename(codigo)}.pdf")
                    
                    generar_certificado(
                        nombre,
                        codigo,
                        proyecto,
                        espacio,
                        TEMPLATE_FILE,
                        output_filename,
                        template_pixel_size, 
                        NEW_PAGE_SIZE        
                    )
                    total_certificados += 1

    print("\n--- ¡PROCESO FINALIZADO! ---")
    if errores_columna > 0:
        print(f"**Atención:** Se encontraron {errores_columna} errores al leer nombres de columna.")
    print(f"Se generaron {total_certificados} certificados (Opción A: uno por estudiante).")
    print(f"Los encontrarás en la carpeta: '{OUTPUT_FOLDER}'")


if __name__ == "__main__":
    main()