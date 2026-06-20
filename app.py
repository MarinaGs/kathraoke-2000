import streamlit as st
import pandas as pd
import psycopg2

# --- 1. CONFIGURACIÓN VISUAL: DISEÑO ULTRA-COMPATIBLE MÓVIL ---
st.set_page_config(page_title="Kathraoke 2000", page_icon="🎤", layout="centered")

st.markdown("""
    <style>
    /* Bloqueo absoluto de estilos oscuros/negros intrusivos en móviles */
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

    /* Modificación del bloque expandible para evitar recuadros negros */
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.6) !important;
        border: 1px solid #b3ccff !important;
        border-radius: 12px !important;
    }
    
    div[data-testid="stExpander"] summary {
        background-color: transparent !important;
    }

    /* Cambiar el color del tick de los checkbox a azul oscuro (adiós al rojo/azul feo) */
    div[data-testid="stCheckbox"] input[type="checkbox"]:checked ~ div {
        background-color: #1a0066 !important;
        border-color: #1a0066 !important;
    }
    div[data-testid="stCheckbox"] span[data-baseweb="checkbox"] > div {
        background-color: #1a0066 !important;
        border-color: #1a0066 !important;
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

    .tag-container {
        display: flex;
        gap: 4px;
        flex-wrap: wrap;
    }

    /* Etiquetas de canciones limpias y legibles */
    .tag {
        display: inline-block !important;
        background-color: #ffffff !important;
        color: #1a0066 !important;
        padding: 2px 6px !important;
        border-radius: 20px !important;
        border: 1px solid #b3ccff !important;
        font-size: 10px !important;
        font-weight: bold !important;
    }

    /* Buscador blanco con texto oscuro */
    .stTextInput>div>div {
        background-color: #ffffff !important;
        border-radius: 12px !important;
    }
    
    .stTextInput input {
        background-color: #ffffff !important;
        border: 1px solid #b3ccff !important;
        color: #1a0066 !important; 
        border-radius: 12px !important;
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

# --- 4. BUSCADOR Y FILTROS MULTI-TIPO ---
buscar = st.text_input("✨ Busca tu temazo o artista favorito:", placeholder="Ej: Britney, Estopa, Daddy Yankee...")

# Definimos listas estáticas limpias para mapear los filtros de forma segura
modos_fijos = ["Solitario", "Dúo", "Fiesta"]
generos_fijos = ["Pop", "Rock", "Reggaetón", "Latino"]

with st.expander("🎛️ Filtrar por Género o Modo"):
    st.write("👥 **Modo de canto:**")
    filtro_modo = []
    col1, col2, col3 = st.columns(3)
    for i, m in enumerate(modos_fijos):
        target_col = [col1, col2, col3][i % 3]
        if target_col.checkbox(m, value=True, key=f"filter_modo_{m}"):
            filtro_modo.append(m)

    st.write("🎸 **Género musical:**")
    filtro_genero = []
    cols = st.columns(2)
    for i, g in enumerate(generos_fijos):
        target_col = cols[i % 2]
        if target_col.checkbox(g, value=True, key=f"filter_gen_{g}"):
            filtro_genero.append(g)

st.markdown("---")

# --- 5. MOSTRAR LISTA DE CANCIONES (LÓGICA CON SOPORTE PARA COMAS) ---
if df_completo.empty:
    st.info("La lista está vacía. Desplázate abajo al Panel de Administrador.")
else:
    # 1. Filtro por texto básico (Título o Artista)
    mask_texto = df_completo["titulo"].str.contains(buscar, case=False) | df_completo["artista"].str.contains(buscar, case=False)
    df_filtrado = df_completo[mask_texto]
    
    # 2. Filtro avanzado para filas que contienen múltiples tipos (separados por comas)
    canciones_validas = []
    for _, fila in df_filtrado.iterrows():
        # Separar los modos y géneros de la base de datos por comas y limpiar espacios
        modos_cancion = [m.strip() for m in str(fila["modo"]).split(",")]
        generos_cancion = [g.strip() for g in str(fila["genero"]).split(",")]
        
        # Comprobar si al menos uno de los tipos coincide con los filtros activos
        coincide_modo = any(m in filtro_modo for m in modos_cancion)
        coincide_genero = any(g in filtro_genero for g in generos_cancion)
        
        if coincide_modo and coincide_genero:
            canciones_validas.append(fila)
            
    df_final = pd.DataFrame(canciones_validas)

    if not df_final.empty:
        for _, fila in df_final.iterrows():
            # Convertir los textos con comas en cajitas HTML individuales
            tags_html = "".join([f'<span class="tag">{g.strip()}</span>' for g in str(fila["genero"]).split(",")])
            tags_html += "".join([f'<span class="tag" style="border-color:#ff99cc;">{m.strip()}</span>' for m in str(fila["modo"]).split(",")])
            
            st.markdown(f"""
            <div class="song-card">
                <div class="song-info">
                    <span class="song-title">🎵 {fila['titulo']}</span>
                    <span class="song-artist">🎤 {fila['artista']}</span>
                </div>
                <div class="tag-container">
                    {tags_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No encontramos ninguna canción que coincida.")

# --- 6. PANEL ADMIN: PERMITE ESCRIBIR VARIOS SEPARADOS POR COMAS ---
st.markdown("---")
with st.expander("🔒 Panel de Administrador"):
    password = st.text_input("Contraseña Admin:", type="password")
    
    if password == "admin123":
        st.success("Acceso autorizado")
        
        st.subheader("➕ Añadir Canción")
        nuevo_titulo = st.text_input("Título:")
        nuevo_artista = st.text_input("Artista:")
        
        st.info("💡 Puedes escribir varios tipos separados por comas. Ejemplo: 'Pop, Rock' o 'Solitario, Dúo'")
        nuevo_modo = st.text_input("Modos de canto (Ej: Solitario, Dúo):", value="Solitario")
        nuevo_genero = st.text_input("Géneros musicales (Ej: Pop, Latino):", value="Pop")
        
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
                
        st.markdown("---")
        st.subheader("🗑️ Eliminar Canción")
        if not df_completo.empty:
            opciones_eliminar = {f"{f['titulo']} - {f['artista']}": f['id'] for _, f in df_completo.iterrows()}
            cancion_a_eliminar = st.selectbox("Selecciona para borrar:", options=list(opciones_eliminar.keys()))
            
            if st.button("❌ Eliminar definitivamente"):
                id_borrar = opciones_eliminar[cancion_a_eliminar]
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM canciones WHERE id = %s", (id_borrar,))
                conn.commit()
                cursor.close()
                conn.close()
                st.success("Eliminada.")
                st.rerun()