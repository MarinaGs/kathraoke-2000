import streamlit as st
import pandas as pd
import psycopg2

# --- 1. CONFIGURACIÓN VISUAL: PALETA Y2K LIMPIA SIN RECUADROS NEGROS ---
st.set_page_config(page_title="Kathraoke 2000", page_icon="🎤", layout="centered")

st.markdown("""
    <style>
    /* Desactivar cualquier resaltado o recuadro negro nativo en móviles */
    * {
        -webkit-tap-highlight-color: transparent !important;
        -webkit-focus-ring-color: transparent !important;
        outline: none !important;
    }

    /* Fondo con degradado difuminado tipo Holi moderno y suave */
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

    /* Título principal con sombra suave */
    h1 { 
        color: #1a0066 !important; 
        text-align: center !important; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1) !important; 
        font-weight: 900 !important;
        font-size: 24px !important;
        margin-top: -40px !important;
        margin-bottom: 10px !important;
        padding-bottom: 0px !important;
    }

    /* Textos de etiquetas globales */
    div[data-testid="stWidgetLabel"] p, label, .stMarkdown p, .stText, p, span {
        color: #1a0066 !important;
        font-weight: bold !important;
    }

    /* SOLUCIÓN DEFINITIVA AL RECUADRO NEGRO DEL DESPLEGABLE (EXPANDER) */
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.6) !important;
        border: 1px solid #b3ccff !important;
        border-radius: 12px !important;
    }
    
    /* Forzar que la barra del desplegable NUNCA se vuelva negra ni cambie de color al tocarla */
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] details,
    div[data-testid="stExpander"] details summary,
    div[data-testid="stExpander"] details[open] summary,
    div[data-testid="stExpander"] summary:hover,
    div[data-testid="stExpander"] summary:focus,
    div[data-testid="stExpander"] summary:active {
        background-color: transparent !important;
        background: transparent !important;
        color: #1a0066 !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stExpander"] details summary p,
    div[data-testid="stExpander"] details[open] summary p {
        color: #1a0066 !important;
    }

    /* CORRECCIÓN DE LOS TICKS: Cambiados a un azul índigo suave y estético */
    div[data-testid="stCheckbox"] input[type="checkbox"]:checked ~ div {
        background-color: #4d88ff !important;
        border-color: #4d88ff !important;
    }
    div[data-testid="stCheckbox"] span[data-baseweb="checkbox"] > div {
        background-color: #4d88ff !important;
        border-color: #4d88ff !important;
    }

    /* Tarjetas de canciones de la lista */
    .song-card {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        padding: 8px 12px !important;
        margin-bottom: 6px !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
        box-shadow: 0 4px 15px rgba(179, 204, 255, 0.2) !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
    }
    
    .song-title { color: #2b0080 !important; font-size: 14px !important; font-weight: bold !important; }
    .song-artist { color: #555555 !important; font-size: 12px !important; }

    /* Etiquetas internas de canciones */
    .tag {
        display: inline-block !important;
        background: linear-gradient(90deg, #3385ff, #00ccff) !important;
        color: white !important;
        padding: 3px 8px !important;
        border-radius: 20px !important;
        font-size: 10px !important;
        font-weight: bold !important;
    }
    .tag-modo { background: linear-gradient(90deg, #b3ccff, #80aaff) !important; color: #1a0066 !important; }

    /* Buscador e Inputs con letras oscuras totalmente legibles */
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid #b3ccff !important;
        color: #1a0066 !important; 
        border-radius: 12px !important;
    }
    
    .stTextInput input:focus {
        color: #1a0066 !important;
        background-color: #ffffff !important;
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

# --- 4. BUSCADOR Y FILTROS EN LA PÁGINA PRINCIPAL ---
buscar = st.text_input("✨ Busca tu temazo o artista favorito:", placeholder="Ej: Britney, Estopa, Daddy Yankee...")

with st.expander("🎛️ Filtrar por Género o Modo"):
    if not df_completo.empty:
        modos_disponibles = df_completo["modo"].unique().tolist()
        generos_disponibles = df_completo["genero"].unique().tolist()
    else:
        modos_disponibles = ["Solitario", "Dúo", "Fiesta"]
        generos_disponibles = ["Pop", "Rock", "Reggaetón", "Latino"]

    st.write("👥 **Modo de canto:**")
    filtro_modo = []
    col1, col2, col3 = st.columns(3)
    for i, m in enumerate(modos_disponibles):
        target_col = [col1, col2, col3][i % 3]
        if target_col.checkbox(m, value=True, key=f"modo_{m}"):
            filtro_modo.append(m)

    st.write("🎸 **Género musical:**")
    filtro_genero = []
    cols = st.columns(2)
    for i, g in enumerate(generos_disponibles):
        target_col = cols[i % 2]
        if target_col.checkbox(g, value=True, key=f"gen_{g}"):
            filtro_genero.append(g)

st.markdown("---")

# --- 5. MOSTRAR LISTA DE CANCIONES EN LÍNEAS COMPACTAS ---
if df_completo.empty:
    st.info("La lista está vacía. Desplázate abajo al Panel de Administrador para estrenar la base de datos.")
else:
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
        nuevo_modo = st.selectbox("Modo:", ["Solitario", "Dúo", "Fiesta"])
        nuevo_genero = st.text_input("Género:")
        
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