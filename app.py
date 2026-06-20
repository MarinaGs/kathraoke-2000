import streamlit as st
import pandas as pd
import psycopg2

# --- 1. ESTILOS VISUALES (COMPACTOS Y LIMPIOS) ---
st.set_page_config(page_title="Kathraoke 2000", page_icon="🎤", layout="centered")
st.markdown("""
    <style>
    * { -webkit-tap-highlight-color: transparent !important; outline: none !important; }
    .stApp { 
        background: linear-gradient(135deg, #ffe6f2 0%, #e6f0ff 50%, #f0e6ff 100%) !important;
        background-size: 400% 400% !important; animation: gradientBG 15s ease infinite !important;
        color: #1a0066 !important; font-family: 'Courier New', monospace !important; 
    }
    @keyframes gradientBG { 0% { background-position:0% 50%; } 50% { background-position:100% 50%; } 100% { background-position:0% 50%; } }
    h1 { color: #1a0066 !important; text-align: center !important; font-size: 24px !important; margin-top: -40px; }
    
    /* Títulos generales constantes en morado */
    div[data-testid="stWidgetLabel"] p, label, .stMarkdown p,
    div[data-testid="stExpander"] details summary, div[data-testid="stExpander"] details[open] summary p { 
        color: #1a0066 !important; 
        font-weight: bold !important; 
        font-family: 'Courier New', monospace !important;
    }
    
    /* Contenedor del expansor limpio */
    div[data-testid="stExpander"] { background: rgba(255, 255, 255, 0.6) !important; border: 1px solid #b3ccff !important; border-radius: 12px !important; }
    div[data-testid="stExpander"] details summary p { display: inline-block !important; }

    /* PREVENCIÓN DE COLOR NEGRO EN ST.PILLS PARA MÓVILES */
    div[data-testid="stPills"] > div, 
    div[data-testid="stPills"] button,
    div[data-testid="stPills"] button:focus,
    div[data-testid="stPills"] button:active,
    div[data-testid="stPills"] button:hover {
        background-color: transparent !important;
        color: #1a0066 !important;
        box-shadow: none !important;
    }

    /* Estilo de la píldora cuando está seleccionada de forma activa */
    div[data-testid="stPills"] button[aria-selected="true"] {
        background-color: #b3ccff !important;
        color: #1a0066 !important;
        border: 1px solid #1a0066 !important;
    }

    /* Estilo de la píldora cuando está desmarcada */
    div[data-testid="stPills"] button[aria-selected="false"] {
        background-color: rgba(255, 255, 255, 0.4) !important;
        color: #1a0066 !important;
        border: 1px solid rgba(26, 0, 102, 0.2) !important;
        opacity: 0.7;
    }

    /* Diseño de las tarjetas de canciones */
    .song-card { background: rgba(255, 255, 255, 0.7) !important; padding: 8px 12px !important; margin-bottom: 6px !important; border-radius: 10px !important; border: 1px solid rgba(255, 255, 255, 0.6) !important; display: flex !important; justify-content: space-between !important; align-items: center !important; }
    .song-title { color: #2b0080 !important; font-size: 14px !important; font-weight: bold !important; }
    .song-artist { color: #555555 !important; font-size: 12px !important; }
    .tag-container { display: flex; gap: 4px; flex-wrap: wrap; }
    .tag { display: inline-block !important; background-color: #ffffff !important; color: #1a0066 !important; padding: 2px 6px !important; border-radius: 20px !important; border: 1px solid #b3ccff !important; font-size: 10px !important; font-weight: bold !important; }
    .stTextInput input { background-color: #ffffff !important; border: 1px solid #b3ccff !important; color: #1a0066 !important; border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ ⚡ KATHRAOKE 2000 ⚡ ✨")

# --- 2. BASE DE DATOS ---
DATABASE_URL = st.secrets["DATABASE_URL"]
def run_query(query, params=(), is_select=False):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if is_select: return cur.fetchall(), [desc[0] for desc in cur.description]
            conn.commit()

run_query("CREATE TABLE IF NOT EXISTS canciones (id SERIAL PRIMARY KEY, titulo TEXT, artista TEXT, modo TEXT, genero TEXT)")
data, cols = run_query("SELECT * FROM canciones", is_select=True)
df_completo = pd.DataFrame(data, columns=cols)

# --- 3. BUSCADOR Y FILTROS ---
buscar = st.text_input("✨ Busca tu temazo, artista o cantante:", placeholder="Ej: Britney, Shakira, Estopa...")
modos_fijos, generos_fijos = ["Solitario", "Dúo", "Fiesta"], ["Pop", "Rock", "Reggaetón", "Latino"]

with st.expander("🎛️ Filtros"):
    filtro_modo = st.pills("👥 Modo:", opciones=modos_fijos, default=modos_fijos, selection_mode="multi")
    filtro_genero = st.pills("🎸 Género:", opciones=generos_fijos, default=generos_fijos, selection_mode="multi")

st.markdown("---")

# --- 4. LISTA DE CANCIONES ---
if df_completo.empty:
    st.info("La lista está vacía.")
else:
    mask_texto = df_completo["titulo"].str.contains(buscar, case=False) | df_completo["artista"].str.contains(buscar, case=False)
    canciones_validas = []
    
    modos_activos = filtro_modo if filtro_modo else []
    generos_activos = filtro_genero if filtro_genero else []

    for _, fila in df_completo[mask_texto].iterrows():
        coincide_m = any(m.strip() in modos_activos for m in str(fila["modo"]).split(","))
        coincide_g = any(g.strip() in generos_activos for g in str(fila["genero"]).split(","))
        if coincide_m and coincide_g: canciones_validas.append(fila)

    if canciones_validas:
        for fila in canciones_validas:
            tags = "".join([f'<span class="tag">{g.strip()}</span>' for g in str(fila["genero"]).split(",")])
            tags += "".join([f'<span class="tag" style="border-color:#ff99cc;">{m.strip()}</span>' for m in str(fila["modo"]).split(",")])
            st.markdown(f"""
            <div class="song-card">
                <div class="song-info">
                    <span class="song-title">🎵 {fila['titulo']}</span><br>
                    <span class="song-artist">🎤 {fila['artista']}</span>
                </div>
                <div class="tag-container">{tags}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No hay resultados.")

# --- 5. PANEL ADMIN ---
st.markdown("---")
with st.expander("🔒 Panel Admin"):
    if st.text_input("Contraseña:", type="password") == "admin123":
        st.subheader("➕ Añadir")
        t, a = st.text_input("Título:"), st.text_input("Artistas:")
        m, g = st.text_input("Modos:", value="Solitario"), st.text_input("Géneros:", value="Pop")
        
        if st.button("Guardar") and t and a:
            run_query("INSERT INTO canciones (titulo, artista, modo, genero) VALUES (%s,%s,%s,%s)", (t, a, m, g))
            st.success("¡Añadida!")
            st.rerun()
            
        st.markdown("---")
        st.subheader("🗑️ Eliminar")
        if not df_completo.empty:
            opc = {f"{f['titulo']} - {f['artista']}": f['id'] for _, f in df_completo.iterrows()}
            seleccionado = st.selectbox("Elige la canción a borrar:", options=list(opc.keys()))
            
            if st.button("❌ Borrar Seleccionada"):
                id_borrar = opc[seleccionado]
                run_query("DELETE FROM canciones WHERE id = %s", (id_borrar,))
                st.success("Canción eliminada correctamente.")
                st.rerun()
        else:
            st.text("No hay canciones para borrar.")