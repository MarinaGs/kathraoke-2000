import streamlit as st
import pandas as pd
import psycopg2

# --- 1. ESTILOS VISUALES (COMPACTOS Y ANTI-MODO OSCURO) ---
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
    
    /* Títulos generales y del expansor constantes en morado */
    div[data-testid="stWidgetLabel"] p, label, .stMarkdown p,
    div[data-testid="stExpander"] details summary, div[data-testid="stExpander"] details[open] summary p { 
        color: #1a0066 !important; 
        font-weight: bold !important; 
        font-family: 'Courier New', monospace !important;
    }
    
    /* Contenedor del expansor limpio */
    div[data-testid="stExpander"] { background: rgba(255, 255, 255, 0.6) !important; border: 1px solid #b3ccff !important; border-radius: 12px !important; }
    div[data-testid="stExpander"] details summary p { display: inline-block !important; }
    
    /* -------------------------------------------------------------
       REESCRITURA CRÍTICA DE CHECKBOXES (ELIMINACIÓN DE AZUL Y ROJO)
       ------------------------------------------------------------- */
    
    /* 1. Limpieza absoluta de la fila del checkbox y sus estados activos */
    div[data-testid="stCheckbox"], 
    div[data-testid="stCheckbox"] > label,
    div[data-testid="stCheckbox"] [data-baseweb="checkbox"] {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
    }

    /* 2. Forzar que las palabras NUNCA tengan fondo azul ni cambien al marcar */
    div[data-testid="stCheckbox"] p,
    div[data-testid="stCheckbox"] [data-baseweb="checkbox"] p,
    div[data-testid="stCheckbox"] input[type="checkbox"]:checked ~ div + p,
    div[data-testid="stCheckbox"] label span p {
        color: #1a0066 !important; 
        font-weight: bold !important; 
        background-color: transparent !important;
        background: transparent !important;
        text-shadow: none !important;
    }

    /* 3. Estilo base del cuadradito (Desmarcado) */
    div[data-testid="stCheckbox"] span[data-baseweb="checkbox"] > div:first-child {
        border-radius: 4px !important;
        border: 2px solid #1a0066 !important;
        background-color: #ffffff !important;
        width: 18px !important;
        height: 18px !important;
    }
    
    /* 4. Estilo del cuadradito (Marcado) - Reemplaza el rojo por un lila/rosa suave */
    div[data-testid="stCheckbox"] input[type="checkbox"]:checked + div,
    div[data-testid="stCheckbox"] input[type="checkbox"]:checked ~ div,
    div[data-testid="stCheckbox"] [data-baseweb="checkbox"] div[background-color] { 
        background-color: #b3ccff !important; /* Fondo lila suave armonioso */
        border-color: #1a0066 !important;
    }
    
    /* 5. Color del tick interno (Morado oscuro en vez de blanco/rojo) */
    div[data-testid="stCheckbox"] svg,
    div[data-testid="stCheckbox"] [data-baseweb="checkbox"] svg {
        fill: none !important;
        stroke: #1a0066 !important; /* El tick interno ahora es morado */
        stroke-width: 4px !important;
    }
    
    /* Remover cualquier sombra o resplandor azul de enfoque nativo */
    div[data-testid="stCheckbox"] :focus, 
    div[data-testid="stCheckbox"] [data-baseweb="checkbox"] > div:blur {
        box-shadow: none !important;
        outline: none !important;
    }
    /* ------------------------------------------------------------- */

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
    st.write("👥 **Modo:**")
    filtro_modo = [m for m, col in zip(modos_fijos, st.columns(3)) if col.checkbox(m, value=True, key=f"m_{m}")]
    st.write("🎸 **Género:**")
    filtro_genero = [g for g, col in zip(generos_fijos, st.columns(4)) if col.checkbox(g, value=True, key=f"g_{g}")]

st.markdown("---")

# --- 4. LISTA DE CANCIONES ---
if df_completo.empty:
    st.info("La lista está vacía.")
else:
    mask_texto = df_completo["titulo"].str.contains(buscar, case=False) | df_completo["artista"].str.contains(buscar, case=False)
    canciones_validas = []
    
    for _, fila in df_completo[mask_texto].iterrows():
        coincide_m = any(m.strip() in filtro_modo for m in str(fila["modo"]).split(","))
        coincide_g = any(g.strip() in filtro_genero for g in str(fila["genero"]).split(","))
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