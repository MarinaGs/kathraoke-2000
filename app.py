import streamlit as st
import pandas as pd
import psycopg2

# --- 1. CONFIGURACIÓN VISUAL: DISEÑO COMPATIBLE 100% MÓVIL ---
st.set_page_config(page_title="Kathraoke 2000", page_icon="🎤", layout="centered")

st.markdown("""
    <style>
    /* Bloqueo absoluto de estilos intrusivos de los navegadores móviles */
    * {
        -webkit-tap-highlight-color: transparent !important;
        -webkit-focus-ring-color: transparent !important;
        outline: none !important;
        box-shadow: none !important;
    }

    /* Fondo degradado suave */
    .stApp { 
        background: linear-gradient(135deg, #ffe6f2 0%, #e6f0ff 50%, #f0e6ff 100%) !important;
        background-size: 400% 400% !important;
        animation: gradientBG 15s ease infinite !important;
        color: #1a0066 !important; 
        font-family: 'Courier New', monospace !important; 
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    h1 { 
        color: #1a0066 !important; 
        text-align: center !important; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1) !important; 
        font-weight: 900 !important;
        font-size: 24px !important;
        margin-top: -40px !important;
        margin-bottom: 10px !important;
    }

    /* Forzar color de etiquetas y textos generales */
    div[data-testid="stWidgetLabel"] p, label, .stMarkdown p, .stText, p, span {
        color: #1a0066 !important;
        font-weight: bold !important;
    }

    /* Forzar que las cajas de selección (Selectbox) sean blancas con texto oscuro */
    div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border: 1px solid #b3ccff !important;
        border-radius: 8px !important;
    }
    
    div[data-baseweb="select"] * {
        color: #1a0066 !important;
        background-color: transparent !important;
    }

    /* Modificación del bloque expandible para evitar recuadros negros */
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.6) !important;
        border: 1px solid #b3ccff !important;
        border-radius: 12px !important;
    }
    
    div[data-testid="stExpander"] summary {
        background-color: transparent !important;
    }

    /* Tarjetas de la lista de reproducción */
    .song-card {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        padding: 8px 12px !important;
        margin-bottom: 6px !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
    }
    
    .song-title { color: #2b0080 !important; font-size: 14px !important; font-weight: bold !important; }
    .song-artist { color: #555555 !important; font-size: 12px !important; }

    /* Etiquetas de canciones (Pop, Solitario, etc.) limpias y legibles */
    .tag, .tag-modo {
        display: inline-block !important;
        background-color: #ffffff !important;
        color: #1a0066 !important;
        padding: 3px 8px !important;
        border-radius: 20px !important;
        border: 1px solid #b3ccff !important;
        font-size: 11px !important;
        font-weight: bold !important;
    }

    /* Entrada de texto del buscador */
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid #b3ccff !important;
        color: #1a0066 !important; 
        border-radius: 12px !important;
    }
    
    hr {
        border-top: 1px solid #e6f0ff !important;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ ⚡ KATHRAOKE 2000 ⚡ ✨")

# --- 2. CONEXIÓN A NEON ---
DATABASE_URL = st.secrets["DATABASE_URL"]

def obtener_conexion():
    return psycopg2.connect(DATABASE_URL)

conn = obtener_conexion()
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS canciones (
    id SERIAL PRIMARY KEY,
    titulo TEXT,
    artista TEXT,
    modo TEXT,
    genero TEXT
)
""")
conn.commit()
cursor.close()
conn.close()

# --- 3. LEER DATOS ---
conn = obtener_conexion()
df_completo = pd.read_sql_query("SELECT * FROM canciones", conn)
conn.close()

# --- 4. BUSCADOR Y FILTROS SIMPLIFICADOS ---
buscar = st.text_input("✨ Busca tu temazo o artista favorito:", placeholder="Ej: Britney, Estopa, Daddy Yankee...")

with st.expander("🎛️ Filtrar por Género o Modo"):
    if not df_completo.empty:
        modos_disponibles = ["Todos"] + df_completo["modo"].unique().tolist()
        generos_disponibles = ["Todos"] + df_completo["genero"].unique().tolist()
    else:
        modos_disponibles = ["Todos", "Solitario", "Dúo", "Fiesta"]
        generos_disponibles = ["Todos", "Pop", "Rock", "Reggaetón", "Latino"]

    # Usamos selectbox simples que no se rompen con los colores del móvil
    seleccion_modo = st.selectbox("👥 Elige Modo de canto:", options=modos_disponibles)
    seleccion_genero = st.selectbox("🎸 Elige Género musical:", options=generos_disponibles)

st.markdown("---")

# --- 5. MOSTRAR LISTA DE CANCIONES ---
if df_completo.empty:
    st.info("La lista está vacía. Desplázate abajo al Panel de Administrador para estrenar la base de datos.")
else:
    # Lógica de filtrado adaptada al selectbox ("Todos")
    if seleccion_modo == "Todos":
        filtro_modo = df_completo["modo"].unique().tolist()
    else:
        filtro_modo = [seleccion_modo]

    if seleccion_genero == "Todos":
        filtro_genero = df_completo["genero"].unique().tolist()
    else:
        filtro_genero = [seleccion_genero]

    query_filtrada = df_completo[
        (df_completo["titulo"].str.contains(buscar, case=False) | df_completo["artista"].str.contains(buscar, case=False)) &
        (df_completo["modo"].isin(filtro_modo)) &
        (df_completo["genero"].isin(filtro_genero))
    ]
    
    if not query_filtrada.empty:
        for _, fila in query_filtrada.iterrows():
            st.markdown(f"""
            <div class="song-card">
                <div class="song-info">
                    <span class="song-title">🎵 {fila['titulo']}</span>
                    <span class="song-artist">🎤 {fila['artista']}</span>
                </div>
                <div class="song-tags">
                    <span class="tag">{fila['genero']}</span>
                    <span class="tag tag-modo">{fila['modo']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No encontramos esa canción. ¡Intenta otra búsqueda!")

# --- 6. PANEL ADMIN AL FINAL ---
st.markdown("---")
with st.expander("🔒 Panel de Administrador"):
    password = st.text_input("Contraseña Admin:", type="password")
    
    if password == "admin123":
        st.success("Acceso autorizado")
        nuevo_titulo = st.text_input("Título de la canción:")
        nuevo_artista = st.text_input("Artista:")
        nuevo_modo = st.selectbox("Modo de canto (Admin):", ["Solitario", "Dúo", "Fiesta"])
        nuevo_genero = st.text_input("Género musical (Admin):")
        
        if st.button("Añadir al repertorio"):
            if nuevo_titulo and nuevo_artista:
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO canciones (titulo, artista, modo, genero) VALUES (%s, %s, %s, %s)",
                               (nuevo_titulo, nuevo_artista, nuevo_modo, nuevo_genero))
                conn.commit()
                cursor.close()
                conn.close()
                st.success("¡Guardada!")
                st.rerun()
    elif password != "":
        st.error("Contraseña incorrecta")