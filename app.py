import streamlit as st
import pandas as pd
import psycopg2

# --- 1. ESTILOS VISUALES (COMPACTOS, ESTABLES Y ANTI-MODO OSCURO) ---
st.set_page_config(page_title="Kathraoke 2000", page_icon="🎤", layout="centered")
st.markdown("""
    <style>
    /* RESET REGLAS INTERNAS DE ENFOQUE Y TÁCTIL */
    * { -webkit-tap-highlight-color: transparent !important; outline: none !important; }
    
    /* Fondo animado principal */
    .stApp { 
        background: linear-gradient(135deg, #ffe6f2 0%, #e6f0ff 50%, #f0e6ff 100%) !important;
        background-size: 400% 400% !important; animation: gradientBG 15s ease infinite !important;
        color: #1a0066 !important; font-family: 'Courier New', monospace !important; 
    }
    @keyframes gradientBG { 0% { background-position:0% 50%; } 50% { background-position:100% 50%; } 100% { background-position:0% 50%; } }
    h1 { color: #1a0066 !important; text-align: center !important; font-size: 24px !important; margin-top: -40px; }
    
    /* FORZAR TEXTOS SIEMPRE EN MORADO */
    div[data-testid="stWidgetLabel"] p, label, .stMarkdown p, 
    div[data-testid="stExpander"] summary p, div[data-testid="stExpander"] p { 
        color: #1a0066 !important; 
        font-weight: bold !important; 
        font-family: 'Courier New', monospace !important;
    }
    
    /* EVITAR QUE EL FILTRO SE VUELVA NEGRO AL INTERACTUAR */
    div[data-testid="stExpander"] { 
        background: rgba(255, 255, 255, 0.6) !important; 
        border: 1px solid #b3ccff !important; 
        border-radius: 12px !important; 
    }
    div[data-testid="stExpander"] details, 
    div[data-testid="stExpander"] details[open], 
    div[data-testid="stExpander"] summary {
        background-color: transparent !important;
        background: transparent !important;
    }
    div[data-testid="stExpander"] summary:hover, 
    div[data-testid="stExpander"] summary:active, 
    div[data-testid="stExpander"] summary:focus {
        background-color: transparent !important;
        color: #1a0066 !important;
    }
    div[data-testid="stExpander"] svg { fill: #1a0066 !important; }

    /* CONTROL TOTAL AGRESIVO DE ST.PILLS (ANTI-BOTÓN NEGRO EN MÓVIL) */
    div[data-testid="stPills"] button {
        font-family: 'Courier New', monospace !important;
        font-weight: bold !important;
        transition: background-color 0.2s ease, color 0.2s ease !important;
    }
    
    /* 1. Control de píldoras NO seleccionadas y sus sub-elementos internos */
    div[data-testid="stPills"] button[aria-selected="false"],
    div[data-testid="stPills"] button[aria-selected="false"] *,
    div[data-testid="stPills"] button[aria-selected="false"]:hover,
    div[data-testid="stPills"] button[aria-selected="false"]:focus,
    div[data-testid="stPills"] button[aria-selected="false"]:active,
    div[data-testid="stPills"] button[aria-selected="false"]:focus-visible {
        background-color: rgba(255, 255, 255, 0.7) !important;
        background: rgba(255, 255, 255, 0.7) !important;
        color: #1a0066 !important;
        border: 1px solid #ff99cc !important;
    }
    
    /* 2. Control de píldoras SI seleccionadas y sus sub-elementos internos */
    div[data-testid="stPills"] button[aria-selected="true"],
    div[data-testid="stPills"] button[aria-selected="true"] *,
    div[data-testid="stPills"] button[aria-selected="true"]:hover,
    div[data-testid="stPills"] button[aria-selected="true"]:focus,
    div[data-testid="stPills"] button[aria-selected="true"]:active,
    div[data-testid="stPills"] button[aria-selected="true"]:focus-visible {
        background-color: #1a0066 !important;
        background: #1a0066 !important;
        color: #ffffff !important;
        border: 1px solid #1a0066 !important;
        box-shadow: 0px 2px 5px rgba(26,0,102,0.2) !important;
    }

    /* Eliminar cajas de sombras oscuras residuales de Streamlit */
    div[data-testid="stPills"] button:focus-visible, 
    div[data-testid="stPills"] button div {
        box-shadow: none !important;
        background-color: transparent !important;
    }

    /* TARJETAS DE CANCIONES Y BUSCADOR */
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
    filtro_modo = st.pills("👥 Modo:", options=modos_fijos, default=modos_fijos, selection_mode="multi")
    filtro_genero = st.pills("🎸 Género:", options=generos_fijos, default=generos_fijos, selection_mode="multi")

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
        t = st.text_input("Título:")
        a = st.text_input("Artistas:")
        m = st.text_input("Modos:", value="Solitario")
        g = st.text_input("Géneros:", value="Pop")
        
        if st.button("Guardar") and t and a:
            # Uso de la consulta parametrizada segura para escapar caracteres como comillas o acentos
            query_insert = "INSERT INTO canciones (titulo, artista, modo, genero) VALUES (%s, %s, %s, %s)"
            run_query(query_insert, (t.strip(), a.strip(), m.strip(), g.strip()))
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