import streamlit as st
import pandas as pd
import psycopg2

# --- 1. CONFIGURACIÓN VISUAL: PALETA DE COLORES Y2K CON FILTROS CORREGIDOS ---
st.set_page_config(page_title="Kathraoke 2000", page_icon="🎤", layout="centered")

st.markdown("""
    <style>
    /* Fondo con degradado difuminado tipo Holi moderno y suave */
    .stApp { 
        background: linear-gradient(135deg, #ffe6f2 0%, #e6f0ff 50%, #f0e6ff 100%);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #1a0066; 
        font-family: 'Courier New', monospace; 
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Título estilo 2000s optimizado con sombras aqua y rosa */
    h1 { 
        color: #ff3399 !important; 
        text-align: center; 
        text-shadow: 2px 2px 6px #00ffff, -2px -2px 6px #fff; 
        font-weight: 900;
        font-size: 24px !important;
        letter-spacing: 1px;
        margin-top: -40px !important;
        margin-bottom: 10px !important;
        padding-bottom: 0px !important;
    }

    /* Textos fijos y etiquetas encima de los inputs */
    div[data-testid="stWidgetLabel"] p, label, .stMarkdown p, .stText, p {
        color: #1a0066 !important;
        font-weight: bold !important;
        font-size: 14px !important;
    }

    /* SOLUCIÓN DE FILTROS: Forzar colores de los selectores dinámicos de Streamlit */
    div[data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 8px !important;
    }
    
    /* Cambiar el color de los elementos seleccionados dentro del filtro (Multiselect) */
    span[data-baseweb="tag"] {
        background-color: #d1e2ff !important; /* Azul pastel */
        color: #1a0066 !important; /* Texto oscuro legible */
        border-radius: 6px !important;
    }
    
    /* Color de la X para eliminar un filtro */
    span[data-baseweb="tag"] role[button], span[data-baseweb="tag"] svg {
        fill: #1a0066 !important;
    }

    /* Estilo para el contenedor desplegable (Expander) */
    .stContentBlock, div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.4) !important;
        border: 1px solid #b3ccff !important;
        border-radius: 12px !important;
    }
    
    /* Tarjeta compacta de canción estilo lista de reproducción */
    .song-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 8px 12px;
        margin-bottom: 6px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 4px 15px rgba(179, 204, 255, 0.2);
        
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .song-info {
        display: flex;
        flex-direction: column;
        flex-grow: 1;
        padding-right: 8px;
    }
    
    .song-title {
        font-size: 14px;
        font-weight: bold;
        color: #2b0080;
    }
    
    .song-artist {
        font-size: 12px;
        color: #555555;
        margin-top: 1px;
    }

    .song-tags {
        display: flex;
        gap: 4px;
        flex-shrink: 0;
    }

    /* Etiquetas internas de las canciones en la lista */
    .tag {
        display: inline-block;
        background: linear-gradient(90deg, #3385ff, #00ccff);
        color: white !important;
        padding: 3px 8px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: bold;
    }
    
    .tag-modo {
        background: linear-gradient(90deg, #ff3399, #ff99cc);
    }

    /* Buscador e Inputs generales */
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 12px !important;
        border: 1px solid #ff99cc !important;
        color: #1a0066 !important;
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

    filtro_modo = st.multiselect("👥 Modo de canto:", options=modos_disponibles, default=modos_disponibles)
    filtro_genero = st.multiselect("🎸 Género musical:", options=generos_disponibles, default=generos_disponibles)

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