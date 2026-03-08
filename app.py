import streamlit as st
from supabase import create_client
import time
from datetime import date, timedelta
import pandas as pd
import plotly.express as px
from io import BytesIO
from PIL import Image
from streamlit_cropper import st_cropper
import base64

# --- IMPORTANTE: LIBRERÍA CALENDARIO ---
try:
    from streamlit_calendar import calendar
except ImportError:
    calendar = None

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="Taescorer", 
    page_icon="favicon.png", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FUNCIÓN AUXILIAR: LOGO A BASE64 ---
def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded}"
    except:
        return "" 

logo_b64 = get_image_base64("logo-taescorer.png")

# --- 2. CONEXIÓN BASE DE DATOS (MÉTODO LIGERO PARA MÓVILES) ---
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]

supabase = create_client(url, key)
if 'access_token' in st.session_state and 'refresh_token' in st.session_state:
    try:
        supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
    except Exception:
        pass

# --- 3. LISTAS OFICIALES ---
CATEGORIAS_POOMSAE = [
    "Infantil (Menos de 11 años)", "Cadete (12-14 años)", "Juvenil (15-17 años)",
    "Under 30 (18-30 años)", "Under 40 (31-40 años)", "Under 50 (41-50 años)",
    "Under 60 (51-60 años)", "Under 65 (61-65 años)", "Over 65 (Más de 65 años)"
]

GRADOS_TKD = [
    "10° Gup (Blanco)", "9° Gup (Blanco p. Amarilla)", "8° Gup (Amarillo)",
    "7° Gup (Amarillo p. Verde)", "6° Gup (Verde)", "5° Gup (Verde p. Azul)",
    "4° Gup (Azul)", "3° Gup (Azul p. Roja)", "2° Gup (Rojo)", "1° Gup (Rojo p. Negra)",
    "1er Poom", "2do Poom", "3er Poom", "1er Dan", "2do Dan", "3er Dan",
    "4to Dan", "5to Dan", "6to Dan", "7mo Dan", "8vo Dan", "9no Dan"
]

LISTA_POOMSAE_OFICIAL = [
    "Taeguk 1 (Il Jang)", "Taeguk 2 (Yi Jang)", "Taeguk 3 (Sam Jang)", "Taeguk 4 (Sa Jang)",
    "Taeguk 5 (Oh Jang)", "Taeguk 6 (Yuk Jang)", "Taeguk 7 (Chil Jang)", "Taeguk 8 (Pal Jang)",
    "Koryo", "Keumgang", "Taebek", "Pyongwon", "Sipjin", "Jitae", "Chonkwon", "Hansu"
]

# --- 4. CSS MAESTRO (SOLUCIÓN DEFINITIVA DEL MENÚ MÓVIL) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}

    /* FONDO OSCURO */
    .stApp {{ background-color: #1f202b !important; }}
    div[data-testid="stDialog"] {{ background-color: #1f202b !important; }}

    /* LIMPIEZA TOTAL DE ICONOS (Corona, Github, etc.) */
    footer, #MainMenu, .stDeployButton, [data-testid="stToolbar"], 
    [data-testid="stDecoration"], [data-testid="stStatusWidget"], 
    .viewerBadge_container__1QSob, div[class^="viewerBadge_"], 
    div[class^="styles_viewerBadge"] {{ 
        display: none !important; visibility: hidden !important; 
    }}

    /* ==================================================
       EL TRUCO PARA EL MENÚ HAMBURGUESA
       ================================================== */
    
    /* 1. Ponemos el header de Streamlit en la CAPA MÁS ALTA y lo hacemos transparente */
    header[data-testid="stHeader"] {{
        background-color: transparent !important;
        z-index: 999999 !important; /* Capa más alta */
    }}
    
    /* 2. Forzamos a que el ícono de las tres rayitas sea BLANCO y visible */
    header[data-testid="stHeader"] button {{
        color: white !important;
    }}
    header[data-testid="stHeader"] button svg {{
        fill: white !important;
        stroke: white !important;
    }}

    /* 3. Aseguramos que el menú lateral se abra por encima del header */
    section[data-testid="stSidebar"] {{
        z-index: 9999999 !important; 
    }}

    /* 4. Tu barra negra con el logo va en la capa DE ABAJO del menú nativo */
    .custom-header {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 60px;
        background-color: #1f202b;
        border-bottom: 1px solid #333;
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 999990 !important; /* Justo por debajo de 999999 */
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }}
    .custom-header img {{
        height: 35px;
        object-fit: contain;
    }}

    /* Empujar contenido hacia abajo para no tapar lo principal */
    .block-container {{ padding-top: 5rem !important; }}

    /* ================================================== */

    /* LOGO DEL LOGIN (50% PC / 30% MOVIL) */
    .logo-login-container {{ display: flex; justify-content: center; width: 100%; margin-bottom: 20px; }}
    .logo-login-img {{ width: 50%; max-width: 300px; height: auto; object-fit: contain; }}
    @media (max-width: 768px) {{
        .logo-login-img {{ width: 30% !important; }}
    }}

    /* DISEÑO DEL MENÚ LATERAL (BOTONES UNIDOS) */
    section[data-testid="stSidebar"] div[data-testid="stImage"] img {{ display: block !important; margin-left: auto !important; margin-right: auto !important; width: 50% !important; align-self: center !important; }}
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {{ gap: 0rem !important; }}
    section[data-testid="stSidebar"] button {{ border: none !important; color: white !important; font-weight: 600 !important; box-shadow: none !important; width: 100% !important; transition: all 0.2s !important; }}
    section[data-testid="stSidebar"] button:hover {{ filter: brightness(1.15) !important; z-index: 10 !important; }}

    /* Colores Específicos */
    section[data-testid="stSidebar"] div.stButton:nth-of-type(1) {{ padding-bottom: 20px !important; }}
    section[data-testid="stSidebar"] div.stButton:nth-of-type(1) button {{ background-color: #2b2c35 !important; border-radius: 8px !important; }}
    section[data-testid="stSidebar"] div.stButton:nth-of-type(2) button {{ background-color: #0bb4fa !important; border-radius: 10px 10px 0 0 !important; margin-bottom: 1px !important; }}
    section[data-testid="stSidebar"] div.stButton:nth-of-type(3) button {{ background-color: #00f9b1 !important; color: #1e1e1e !important; border-radius: 0 !important; margin-bottom: 1px !important; }}
    section[data-testid="stSidebar"] div.stButton:nth-of-type(4) button {{ background-color: #3a2783 !important; border-radius: 0 !important; margin-bottom: 1px !important; }}
    section[data-testid="stSidebar"] div.stButton:nth-of-type(5) button {{ background-color: #ff9f1c !important; border-radius: 0 0 10px 10px !important; }}
    section[data-testid="stSidebar"] div.stButton:nth-of-type(6) {{ padding-top: 40px !important; }}
    section[data-testid="stSidebar"] div.stButton:nth-of-type(6) button {{ background-color: #2b2c35 !important; border-radius: 8px !important; }}
    section[data-testid="stSidebar"] div.stButton:nth-of-type(7) {{ padding-top: 10px !important; }}
    section[data-testid="stSidebar"] div.stButton:nth-of-type(7) button {{ background-color: #581818 !important; border-radius: 8px !important; border: 1px solid #ff4b4b !important; }}

    div[role="radiogroup"] {{ display: none !important; }}
</style>

<div class="custom-header">
    <img src="{logo_b64}" alt="Taescorer">
</div>
""", unsafe_allow_html=True)

# --- GESTIÓN DE SESIÓN ---
if 'user' not in st.session_state: st.session_state.user = None
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'page_selection' not in st.session_state: st.session_state.page_selection = "Dashboard"

# ==========================================
# 5. FUNCIONES DE LÓGICA 
# ==========================================

def login(email, password):
    try:
        with st.spinner("🥋 Entrando al dojang..."):
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state.user = response.user
            st.session_state.access_token = response.session.access_token
            st.session_state.refresh_token = response.session.refresh_token
            cargar_perfil()
            time.sleep(0.5)
            st.rerun()
    except Exception as e: 
        st.error(f"Error: {e}")

def sign_up(email, password, full_name):
    try:
        with st.spinner("📝 Registrando atleta..."):
            response = supabase.auth.sign_up({"email": email, "password": password, "options": {"data": {"full_name": full_name}}})
            st.session_state.user = response.user
            if response.session:
                st.session_state.access_token = response.session.access_token
                st.session_state.refresh_token = response.session.refresh_token
            st.success("Cuenta creada exitosamente.")
            time.sleep(1)
            st.rerun()
    except Exception as e: 
        st.error(f"Error: {e}")

def logout():
    try:
        supabase.auth.sign_out()
    except:
        pass
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.rerun()

def cargar_perfil():
    if st.session_state.user:
        try:
            data = supabase.table("perfiles").select("*").eq("id", st.session_state.user.id).execute()
            if data.data: st.session_state.perfil = data.data[0]
        except: pass

def actualizar_perfil(datos, archivo_foto_bytes):
    user_id = st.session_state.user.id
    foto_url = st.session_state.perfil.get('foto_url') if st.session_state.perfil else None
    if archivo_foto_bytes:
        try:
            file_path = f"{user_id}/avatar.jpg"
            supabase.storage.from_("avatars").upload(file_path, archivo_foto_bytes, {"content-type": "image/jpeg", "upsert": "true"})
            foto_url = supabase.storage.from_("avatars").get_public_url(file_path) + f"?t={int(time.time())}"
        except: pass
    try:
        with st.spinner("Guardando perfil..."):
            supabase.table("perfiles").update({**datos, "foto_url": foto_url}).eq("id", user_id).execute()
            st.success("✅ Perfil actualizado")
            cargar_perfil()
            time.sleep(1)
            st.rerun()
    except: pass

def get_lista_rivales():
    try:
        user_id = st.session_state.user.id
        resp = supabase.table("registros_poomsae").select("nombre_rival").eq("user_id", user_id).execute()
        df = pd.DataFrame(resp.data)
        return sorted(df['nombre_rival'].dropna().unique().tolist()) if not df.empty else []
    except: return []

def guardar_torneo(datos_torneo, lista_poomsaes):
    user_id = st.session_state.user.id
    try:
        with st.spinner("Guardando torneo..."):
            data_torneo = {"user_id": user_id, "nombre_torneo": datos_torneo["nombre"], "fecha_torneo": str(datos_torneo["fecha"]), "categoria": datos_torneo["categoria"], "modalidad": datos_torneo["modalidad"]}
            res_torneo = supabase.table("torneos").insert(data_torneo).execute()
            torneo_id = res_torneo.data[0]['id']
            poomsaes_a_insertar = []
            for p in lista_poomsaes:
                poomsaes_a_insertar.append({"user_id": user_id, "torneo_id": torneo_id, "ronda": p["ronda"], "nombre_poomsae": p["nombre"], "mi_nota_tecnica": p["mi_tec"], "mi_nota_presentacion": p["mi_pres"], "mi_nota_final": p["mi_total"], "nombre_rival": p["rival_nombre"], "rival_nota_tecnica": p["rival_tec"], "rival_nota_presentacion": p["rival_pres"], "rival_nota_final": p["rival_total"], "resultado": p["resultado"], "comentarios": p["comentarios"]})
            supabase.table("registros_poomsae").insert(poomsaes_a_insertar).execute()
            return True
    except: return False

def guardar_evento_agenda(nombre, inicio, fin, estatus, comentarios):
    user_id = st.session_state.user.id
    try:
        with st.spinner("Agendando..."):
            data = {
                "user_id": user_id, "nombre": nombre,
                "fecha_inicio": str(inicio), "fecha_fin": str(fin),
                "estatus": estatus, "comentarios": comentarios
            }
            supabase.table("agenda").insert(data).execute()
            return True
    except Exception as e:
        st.error(f"Error guardando agenda: {e}")
        return False

def calcular_medallas(df_completo):
    conteo = {"Oro": 0, "Plata": 0, "Bronce": 0, "Participacion": 0}
    if df_completo.empty: return conteo
    torneos_ids = df_completo['torneo_id'].unique()
    for t_id in torneos_ids:
        df_t = df_completo[df_completo['torneo_id'] == t_id]
        rondas_jugadas = df_t['ronda'].unique()
        ronda_max = ""
        if any("Final" in r for r in rondas_jugadas): ronda_max = "Final"
        elif any("Semi" in r for r in rondas_jugadas): ronda_max = "Semi"
        else: ronda_max = "Otra"
        df_ronda_final = df_t[df_t['ronda'].str.contains(ronda_max)]
        es_ganador = "Ganador" in df_ronda_final['resultado'].values
        if ronda_max == "Final":
            if es_ganador: conteo["Oro"] += 1
            else: conteo["Plata"] += 1
        elif ronda_max == "Semi":
            if es_ganador: conteo["Plata"] += 1 
            else: conteo["Bronce"] += 1
        else:
            conteo["Participacion"] += 1
    return conteo

def determinar_lugar(row):
    ronda = row['Ronda'] if 'Ronda' in row else row['ronda']
    res = row['Resultado_Raw']
    if "Final" in ronda: return "🥇 1er Lugar" if res == "Ganador" else "🥈 2do Lugar"
    elif "Semi" in ronda: return "🥈 Plata" if res == "Ganador" else "🥉 3er Lugar"
    elif "4tos" in ronda: return "5to - 8vo Lugar"
    else: return "Participación"

# ==========================================
# 6. PANTALLAS (VISUALES)
# ==========================================

def mostrar_perfil():
    st.header("👤 Completar Perfil")
    p = st.session_state.perfil if st.session_state.perfil else {}
    c1, c2 = st.columns([1, 2])
    with c1:
        if p.get('foto_url'): st.image(p.get('foto_url'), width=150)
        uploaded = st.file_uploader("Foto", type=["jpg", "png"])
        img_bytes = None
        if uploaded:
            img = Image.open(uploaded)
            img.thumbnail((500,500))
            crop = st_cropper(img, aspect_ratio=(1,1), box_color='#FF0000', key="crop")
            buf = BytesIO()
            crop.save(buf, format="JPEG")
            img_bytes = buf.getvalue()
    with c2:
        with st.form("fp"):
            n = st.text_input("Nombre", value=p.get('nombre_completo', ''))
            e = st.number_input("Edad", 5, 99, value=p.get('edad', 18))
            cat = st.selectbox("Categoría", CATEGORIAS_POOMSAE, index=CATEGORIAS_POOMSAE.index(p.get('categoria')) if p.get('categoria') in CATEGORIAS_POOMSAE else 0)
            gr = st.selectbox("Grado", GRADOS_TKD, index=GRADOS_TKD.index(p.get('grado')) if p.get('grado') in GRADOS_TKD else 0)
            gen = st.radio("Género", ["Masculino", "Femenino"], index=["Masculino", "Femenino"].index(p.get('genero')) if p.get('genero') in ["Masculino", "Femenino"] else 0, horizontal=True)
            if st.form_submit_button("Guardar"): actualizar_perfil({"nombre": n, "edad": e, "categoria": cat, "grado": gr, "genero": gen}, img_bytes)

def mostrar_formulario_registro():
    st.header("📝 Nuevo Torneo (Resultados)")
    st.info("Ingresa las notas y verás el cálculo final en tiempo real.")
    rivales_existentes = get_lista_rivales()
    
    c1, c2, c3 = st.columns(3)
    nom = c1.text_input("Nombre del torneo", key="t_nombre")
    fec = c2.date_input("Fecha", date.today(), key="t_fecha")
    cat = c3.selectbox("Categoría", ["Elite", "Liga", "G2", "Open"], key="t_cat")
    col_mod, col_rond = st.columns(2)
    mod = col_mod.radio("Modalidad", ["Individual", "Pareja", "Equipo"], horizontal=True, key="t_mod")
    n_rondas = col_rond.number_input("Rondas", 1, 5, 1, key="t_rondas")
    st.divider()
    
    datos_rondas = []
    tipos = ["Preliminar", "8vos", "4tos", "Semi", "Final"]
    
    for i in range(n_rondas):
        st.subheader(f"🥋 Ronda {i+1}")
        cr1, cr2 = st.columns(2)
        tr = cr1.selectbox(f"Fase {i+1}", tipos, key=f"tr_{i}")
        opcion_rival = cr2.selectbox(f"Seleccionar Rival (Ronda {i+1})", ["➕ Nuevo Rival..."] + rivales_existentes, key=f"sel_riv_{i}")
        if opcion_rival == "➕ Nuevo Rival...": nr = cr2.text_input(f"Escribe nombre del rival", key=f"text_riv_{i}")
        else: nr = opcion_rival
        comentarios = st.text_area(f"Comentarios Ronda {i+1}", key=f"comm_{i}")

        tp1, tp2 = st.tabs(["Poomsae 1", "Poomsae 2"])
        with tp1:
            np1 = st.selectbox("Selecciona el poomsae", LISTA_POOMSAE_OFICIAL, key=f"np1_{i}")
            st.markdown("**🔵 Mis Notas**")
            c1, c2, c3 = st.columns(3)
            mt1 = c1.number_input("Mi nota técnica", 0.0, 4.0, step=0.01, key=f"mt1_{i}")
            mp1 = c2.number_input("Mi nota presentación", 0.0, 6.0, step=0.01, key=f"mp1_{i}")
            total_yo_1 = mt1 + mp1
            c3.metric(label="Final", value=f"{total_yo_1:.2f}")
            st.markdown("**🔴 Notas Rival**")
            rc1, rc2, rc3 = st.columns(3)
            rt1 = rc1.number_input("Rival nota técnica", 0.0, 4.0, step=0.01, key=f"rt1_{i}")
            rp1 = rc2.number_input("Rival nota presentación", 0.0, 6.0, step=0.01, key=f"rp1_{i}")
            total_riv_1 = rt1 + rp1
            rc3.metric(label="Final", value=f"{total_riv_1:.2f}")
        with tp2:
            np2 = st.selectbox("Selecciona el poomsae", LISTA_POOMSAE_OFICIAL, key=f"np2_{i}")
            st.markdown("**🔵 Mis Notas**")
            c1, c2, c3 = st.columns(3)
            mt2 = c1.number_input("Mi nota técnica", 0.0, 4.0, step=0.01, key=f"mt2_{i}")
            mp2 = c2.number_input("Mi nota presentación", 0.0, 6.0, step=0.01, key=f"mp2_{i}")
            total_yo_2 = mt2 + mp2
            c3.metric(label="Final", value=f"{total_yo_2:.2f}")
            st.markdown("**🔴 Notas Rival**")
            rc1, rc2, rc3 = st.columns(3)
            rt2 = rc1.number_input("Rival nota técnica", 0.0, 4.0, step=0.01, key=f"rt2_{i}")
            rp2 = rc2.number_input("Rival nota presentación", 0.0, 6.0, step=0.01, key=f"rp2_{i}")
            total_riv_2 = rt2 + rp2
            rc3.metric(label="Final", value=f"{total_riv_2:.2f}")

        myt = total_yo_1 + total_yo_2
        rivt = total_riv_1 + total_riv_2
        res = "Ganador" if myt > rivt else ("Perdedor" if myt < rivt else "Empate")
        datos_rondas.append({"ronda": f"{tr} (P1)", "nombre": np1, "mi_tec": mt1, "mi_pres": mp1, "mi_total": total_yo_1, "rival_nombre": nr, "rival_tec": rt1, "rival_pres": rp1, "rival_total": total_riv_1, "resultado": res, "comentarios": comentarios})
        datos_rondas.append({"ronda": f"{tr} (P2)", "nombre": np2, "mi_tec": mt2, "mi_pres": mp2, "mi_total": total_yo_2, "rival_nombre": nr, "rival_tec": rt2, "rival_pres": rp2, "rival_total": total_riv_2, "resultado": res, "comentarios": comentarios})

    st.markdown("---")
    if st.button("💾 Guardar Torneo", type="primary"):
        if nom: 
            exito = guardar_torneo({"nombre": nom, "fecha": fec, "categoria": cat, "modalidad": mod}, datos_rondas)
            if exito:
                st.success("¡Torneo guardado exitosamente!")
                keys_a_borrar = ["t_nombre", "t_fecha", "t_cat", "t_mod", "t_rondas"]
                for key in list(st.session_state.keys()):
                    if key in keys_a_borrar or any(x in key for x in ["np1_", "mt1_", "mp1_", "rt1_", "rp1_", "np2_", "mt2_", "mp2_", "rt2_", "rp2_", "tr_", "nr_", "sel_riv_", "text_riv_", "comm_"]):
                        del st.session_state[key]
                time.sleep(1.5)
                st.rerun()
        else: st.warning("⚠️ Debes escribir el nombre del torneo.")

def mostrar_calendario():
    st.title("📅 Calendario de Torneos")
    
    st.subheader("🛠️ Gestión de Agenda")
    tab_add, tab_edit = st.tabs(["➕ Agregar Evento", "✏️ Editar / Eliminar Eventos"])

    with tab_add:
        with st.form("form_agenda"):
            c1, c2, c3 = st.columns(3)
            evt_nombre = c1.text_input("Nombre del Torneo")
            evt_estatus = c2.selectbox("Estatus", ["Confirmado", "Sin Confirmar", "Internacional"])
            evt_coment = c3.text_input("Comentario Corto")
            
            c4, c5 = st.columns(2)
            evt_inicio = c4.date_input("Fecha Inicio", date.today())
            evt_fin = c5.date_input("Fecha Fin", date.today())
            
            if st.form_submit_button("📅 Agendar Evento"):
                if evt_nombre:
                    if guardar_evento_agenda(evt_nombre, evt_inicio, evt_fin, evt_estatus, evt_coment):
                        st.success("Evento agregado")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.warning("Falta el nombre")

    with tab_edit:
        st.caption("Modifica los datos directamente en la tabla y presiona 'Guardar Cambios' para actualizar o marca la casilla para borrar.")
        
        try:
            user_id = st.session_state.user.id
            resp = supabase.table("agenda").select("*").eq("user_id", user_id).execute()
            eventos_db = resp.data
        except:
            eventos_db = []

        if eventos_db:
            df_agenda = pd.DataFrame(eventos_db)
            df_agenda['fecha_inicio'] = pd.to_datetime(df_agenda['fecha_inicio']).dt.date
            df_agenda['fecha_fin'] = pd.to_datetime(df_agenda['fecha_fin']).dt.date

            column_config = {
                "id": None, "user_id": None, "created_at": None,
                "nombre": "Nombre Evento",
                "fecha_inicio": st.column_config.DateColumn("Inicio"),
                "fecha_fin": st.column_config.DateColumn("Fin"),
                "estatus": st.column_config.SelectboxColumn("Estatus", options=["Confirmado", "Sin Confirmar", "Internacional"]),
                "comentarios": "Comentarios"
            }
            
            edited_df = st.data_editor(df_agenda, column_config=column_config, use_container_width=True, hide_index=True, key="editor_agenda", num_rows="dynamic")

            if st.button("💾 Guardar Cambios en Agenda", type="primary"):
                try:
                    with st.spinner("Sincronizando agenda..."):
                        ids_originales = [row['id'] for row in eventos_db]
                        ids_finales = []
                        for index, row in edited_df.iterrows():
                            if pd.notna(row.get('id')):
                                ids_finales.append(row['id'])
                                supabase.table("agenda").update({
                                    "nombre": row['nombre'], "fecha_inicio": str(row['fecha_inicio']), 
                                    "fecha_fin": str(row['fecha_fin']), "estatus": row['estatus'], 
                                    "comentarios": row['comentarios']
                                }).eq("id", row['id']).execute()
                            else:
                                guardar_evento_agenda(row['nombre'], row['fecha_inicio'], row['fecha_fin'], row['estatus'], row['comentarios'])
                        
                        for old_id in ids_originales:
                            if old_id not in ids_finales:
                                supabase.table("agenda").delete().eq("id", old_id).execute()

                    st.success("Agenda actualizada correctamente.")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al sincronizar: {e}")
        else:
            st.info("No hay eventos registrados para editar.")

    st.divider()

    calendar_events = []
    for evt in eventos_db:
        color = "#3788d8"
        if evt['estatus'] == "Confirmado": color = "#28a745"
        elif evt['estatus'] == "Sin Confirmar": color = "#dc3545"
        elif evt['estatus'] == "Internacional": color = "#007bff"

        calendar_events.append({
            "title": evt['nombre'],
            "start": evt['fecha_inicio'],
            "end": str(pd.to_datetime(evt['fecha_fin']) + timedelta(days=1)).split(" ")[0], 
            "backgroundColor": color,
            "borderColor": color,
            "extendedProps": {"description": evt.get('comentarios', '')}
        })

    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,multiMonthYear,listMonth"
        },
        "buttonText": {
            "today": "Hoy", "month": "Mes", "multiMonthYear": "Año Completo",
            "list": "Lista", "prev": "Ant", "next": "Sig"
        },
        "initialView": "dayGridMonth",
        "locale": "es",          
        "height": 800,  
        "navLinks": True,
        "selectable": True,
        "editable": False,
    }

    if calendar:
        st_calendar = calendar(events=calendar_events, options=calendar_options, custom_css="""
            .fc-event-title { font-weight: bold !important; }
            .fc-daygrid-day:hover { background-color: #f0f2f6; }
            .fc-col-header-cell { background-color: #f8f9fa; }
        """)
        if st_calendar.get("eventClick"):
            evt_click = st_calendar["eventClick"]["event"]
            st.info(f"📌 **{evt_click['title']}**\n\n{evt_click['extendedProps']['description']}")
    else:
        st.warning("Instala 'streamlit-calendar' para ver el calendario visual.")


def mostrar_historial_editor():
    st.header("📝 Base de Torneos")
    st.info("Selecciona un torneo para editar. Los cambios se guardan automáticamente en la base de datos.")
    user_id = st.session_state.user.id
    try:
        torneos_resp = supabase.table("torneos").select("*").eq("user_id", user_id).order("fecha_torneo", desc=True).execute()
        df_torneos = pd.DataFrame(torneos_resp.data)
        if df_torneos.empty:
            st.warning("No tienes torneos registrados.")
            return
        
        torneo_opciones = {f"{row['nombre_torneo']} ({row['fecha_torneo']})": row['id'] for index, row in df_torneos.iterrows()}
        seleccion_nombre = st.selectbox("Selecciona Torneo:", list(torneo_opciones.keys()))
        torneo_id_selec = torneo_opciones[seleccion_nombre]
        st.divider()
        
        registros_resp = supabase.table("registros_poomsae").select("*").eq("torneo_id", torneo_id_selec).execute()
        df_registros = pd.DataFrame(registros_resp.data)
        
        column_config = {
            "id": None, "user_id": None, "torneo_id": None, "created_at": None,
            "nombre_poomsae": "Poomsae", "ronda": "Ronda",
            "mi_nota_tecnica": st.column_config.NumberColumn("Mi Técnica", min_value=0, max_value=4, step=0.01),
            "mi_nota_presentacion": st.column_config.NumberColumn("Mi Pres.", min_value=0, max_value=6, step=0.01),
            "mi_nota_final": None, "nombre_rival": "Nombre Rival",
            "rival_nota_tecnica": st.column_config.NumberColumn("Riv. Técnica", min_value=0, max_value=4, step=0.01),
            "rival_nota_presentacion": st.column_config.NumberColumn("Riv. Pres.", min_value=0, max_value=6, step=0.01),
            "rival_nota_final": None, "resultado": None, "comentarios": "Comentarios"
        }
        
        edited_df = st.data_editor(df_registros, column_config=column_config, use_container_width=True, hide_index=True, key="editor_torneos")
        
        if st.button("💾 Guardar Cambios", type="primary"):
            try:
                with st.spinner("Guardando cambios..."):
                    for index, row in edited_df.iterrows():
                        mi_total = round(row['mi_nota_tecnica'] + row['mi_nota_presentacion'], 2)
                        riv_total = round(row['rival_nota_tecnica'] + row['rival_nota_presentacion'], 2)
                        res = "Ganador" if mi_total > riv_total else ("Perdedor" if mi_total < riv_total else "Empate")
                        update_data = {
                            "nombre_poomsae": row['nombre_poomsae'], "ronda": row['ronda'], "nombre_rival": row['nombre_rival'],
                            "mi_nota_tecnica": row['mi_nota_tecnica'], "mi_nota_presentacion": row['mi_nota_presentacion'], "mi_nota_final": mi_total,
                            "rival_nota_tecnica": row['rival_nota_tecnica'], "rival_nota_presentacion": row['rival_nota_presentacion'], "rival_nota_final": riv_total, "resultado": res,
                            "comentarios": row.get('comentarios', '')
                        }
                        supabase.table("registros_poomsae").update(update_data).eq("id", row['id']).execute()
                    st.success("✅ Datos actualizados correctamente.")
                    time.sleep(1)
                    st.rerun()
            except Exception as e: st.error(f"Error al actualizar: {e}")
    except Exception as e: st.error(f"Error cargando historial: {e}")

def mostrar_dashboard():
    user_id = st.session_state.user.id
    try:
        data = supabase.table("registros_poomsae").select("*, torneos(nombre_torneo, fecha_torneo)").eq("user_id", user_id).execute()
        df = pd.DataFrame(data.data)
        
        if not df.empty:
            df['fecha_torneo'] = pd.to_datetime(df['torneos'].apply(lambda x: x['fecha_torneo'] if x else '2024-01-01'))
            df['nombre_torneo'] = df['torneos'].apply(lambda x: x['nombre_torneo'] if x else '-')
            df['label_grafica'] = df['mi_nota_final'].astype(str)
            df.rename(columns={'fecha_torneo': 'Fecha del Torneo', 'mi_nota_final': 'Nota Final', 'nombre_poomsae': 'Poomsae'}, inplace=True)
            df = df.sort_values('Fecha del Torneo')

            # BLOQUE 1
            st.title("📈 Métricas Generales")
            st.subheader("Selecciona los datos")
            c_f1, c_f2, c_f3 = st.columns(3)
            with c_f1:
                opcion_tiempo = st.selectbox("📅 Rango de Fechas", ["Histórico Completo", "Este Año", "Últimos 6 Meses", "Último Mes", "Seleccionar Rango"], key="gen_time")
                start_date = df['Fecha del Torneo'].min()
                end_date = df['Fecha del Torneo'].max()
                hoy = pd.Timestamp.now()
                if opcion_tiempo == "Este Año": start_date = pd.Timestamp(f"{hoy.year}-01-01")
                elif opcion_tiempo == "Últimos 6 Meses": start_date = hoy - pd.DateOffset(months=6)
                elif opcion_tiempo == "Último Mes": start_date = hoy - pd.DateOffset(months=1)
                elif opcion_tiempo == "Seleccionar Rango":
                    fechas_input = st.date_input("Elige fechas", [], key="gen_date_input")
                    if len(fechas_input) == 2:
                        start_date = pd.Timestamp(fechas_input[0])
                        end_date = pd.Timestamp(fechas_input[1])
                df_gen = df[(df['Fecha del Torneo'] >= start_date) & (df['Fecha del Torneo'] <= end_date)]

            with c_f2:
                lista_poomsaes = ["Todos"] + list(df['Poomsae'].unique())
                filtro_poom = st.selectbox("Poomsae", lista_poomsaes, key="gen_poom")
                if filtro_poom != "Todos": df_gen = df_gen[df_gen['Poomsae'] == filtro_poom]

            with c_f3:
                todos_rivales = df_gen['nombre_rival'].dropna().unique()
                rivales_gen = st.multiselect("Comparar con Rival", options=todos_rivales, key="gen_rival")

            st.divider()
            c_win, c_avg, c_med = st.columns(3)
            total_matches = len(df_gen)
            wins = len(df_gen[df_gen['resultado'] == 'Ganador']) if total_matches > 0 else 0
            winrate = (wins / total_matches * 100) if total_matches > 0 else 0
            promedio = df_gen['Nota Final'].mean() if total_matches > 0 else 0

            c_win.metric("Winrate", f"{winrate:.1f}%", f"{wins} Vic / {total_matches} Tot")
            c_avg.metric("Promedio Nota", f"{promedio:.2f}")
            conteo_medallas = calcular_medallas(df_gen)
            c_med.markdown(f"🥇 **{conteo_medallas['Oro']}** Oro &nbsp; 🥈 **{conteo_medallas['Plata']}** Plata <br>🥉 **{conteo_medallas['Bronce']}** Bronce &nbsp; 🟠 **{conteo_medallas['Participacion']}** Part.", unsafe_allow_html=True)

            st.subheader(f"Rendimiento General: {filtro_poom}")
            fig = px.line(df_gen, x="Fecha del Torneo", y="Nota Final", markers=True, text="label_grafica", title="")
            fig.update_traces(name="Yo", line=dict(color="blue", width=4), textposition="top center")
            colores = ["red", "orange", "green", "purple", "pink"]
            for idx, rival in enumerate(rivales_gen):
                datos_rival = df_gen[df_gen['nombre_rival'] == rival]
                fig.add_scatter(x=datos_rival['Fecha del Torneo'], y=datos_rival['rival_nota_final'], mode='lines+markers+text', 
                                text=datos_rival['rival_nota_final'], textposition="top center", 
                                texttemplate='%{text:.2f}', name=f"Rival: {rival}", line=dict(color=colores[idx % 5], dash='dot'))
            st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.markdown("---")

            # BLOQUE 2
            st.header("🔬 Métrica Detallada (Técnica vs Presentación)")
            st.info("Filtra aquí independientemente para ver detalles específicos.")
            
            c_check1, c_check2 = st.columns(2)
            ver_tecnica = c_check1.checkbox("Ver Técnica", value=True)
            ver_pres = c_check2.checkbox("Ver Presentación", value=True)

            c_d1, c_d2, c_d3 = st.columns(3)
            with c_d1:
                opcion_tiempo_det = st.selectbox("📅 Fechas Detalle", ["Histórico Completo", "Este Año", "Últimos 6 Meses", "Último Mes", "Seleccionar Rango"], key="det_time")
                start_date_d = df['Fecha del Torneo'].min()
                if opcion_tiempo_det == "Este Año": start_date_d = pd.Timestamp(f"{hoy.year}-01-01")
                elif opcion_tiempo_det == "Últimos 6 Meses": start_date_d = hoy - pd.DateOffset(months=6)
                elif opcion_tiempo_det == "Último Mes": start_date_d = hoy - pd.DateOffset(months=1)
                df_det = df[df['Fecha del Torneo'] >= start_date_d]

            with c_d2:
                lista_poom_det = ["Todos"] + list(df['Poomsae'].unique())
                filtro_poom_det = st.selectbox("Poomsae Detalle", lista_poom_det, key="det_poom")
                if filtro_poom_det != "Todos": df_det = df_det[df_det['Poomsae'] == filtro_poom_det]

            with c_d3:
                todos_rivales_det = df_det['nombre_rival'].dropna().unique()
                rival_det = st.selectbox("Comparar Detalles con:", ["Ninguno"] + list(todos_rivales_det), key="det_rival")

            if not df_det.empty:
                st.markdown("")
                c_k1, c_k2 = st.columns(2)
                avg_tec = df_det['mi_nota_tecnica'].mean()
                avg_pres = df_det['mi_nota_presentacion'].mean()
                
                df_sorted = df_det.sort_values('Fecha del Torneo')
                delta_tech = 0
                delta_pres = 0
                if len(df_sorted) >= 2:
                    last_tech = df_sorted.iloc[-1]['mi_nota_tecnica']
                    last_pres = df_sorted.iloc[-1]['mi_nota_presentacion']
                    prev_tech = df_sorted.iloc[-2]['mi_nota_tecnica']
                    prev_pres = df_sorted.iloc[-2]['mi_nota_presentacion']
                    delta_tech = last_tech - prev_tech
                    delta_pres = last_pres - prev_pres
                
                c_k1.metric("Promedio Técnica", f"{avg_tec:.2f}", f"{delta_tech:+.2f} vs ant.")
                c_k2.metric("Promedio Presentación", f"{avg_pres:.2f}", f"{delta_pres:+.2f} vs ant.")

            vars_to_melt = []
            if ver_tecnica:
                vars_to_melt.append('mi_nota_tecnica')
                if rival_det != "Ninguno": vars_to_melt.append('rival_nota_tecnica')
            if ver_pres:
                vars_to_melt.append('mi_nota_presentacion')
                if rival_det != "Ninguno": vars_to_melt.append('rival_nota_presentacion')

            if vars_to_melt:
                df_detalle_graf = df_det[['Fecha del Torneo', 'nombre_torneo', 'Poomsae', 'mi_nota_tecnica', 'mi_nota_presentacion', 'rival_nota_tecnica', 'rival_nota_presentacion', 'nombre_rival']]
                if rival_det != "Ninguno":
                    df_detalle_graf = df_detalle_graf[df_detalle_graf['nombre_rival'] == rival_det]
                else:
                    st.caption("Mostrando solo tu evolución.")

                df_melted = df_detalle_graf.melt(id_vars=['Fecha del Torneo', 'Poomsae'], value_vars=vars_to_melt, var_name='Tipo Nota', value_name='Puntaje')
                mapa_nombres = {'mi_nota_tecnica': 'Mi Técnica', 'mi_nota_presentacion': 'Mi Presentación', 'rival_nota_tecnica': 'Rival Técnica', 'rival_nota_presentacion': 'Rival Presentación'}
                df_melted['Tipo Nota'] = df_melted['Tipo Nota'].map(mapa_nombres)
                
                fig_det = px.line(df_melted, x="Fecha del Torneo", y="Puntaje", color="Tipo Nota", symbol="Tipo Nota", markers=True, text="Puntaje", hover_data=["Poomsae"],
                                  color_discrete_map={'Mi Técnica': 'blue', 'Mi Presentación': 'cyan', 'Rival Técnica': 'red', 'Rival Presentación': 'orange'})
                fig_det.update_traces(textposition="top center", texttemplate='%{text:.2f}')
                st.plotly_chart(fig_det, use_container_width=True)
            else:
                st.warning("Selecciona al menos una variable (Técnica o Presentación) para ver la gráfica.")

            st.divider()
            st.markdown("---")

            # BLOQUE 3
            st.subheader("📋 Detalles del Torneo (Independiente)")
            st.info("Selecciona un torneo para ver sus datos sin filtros previos.")
            df_full_torneos = df.copy() 
            lista_torneos = df_full_torneos['nombre_torneo'].unique()
            torneo_selec = st.selectbox("Selecciona Torneo:", lista_torneos, key="torneo_detail_select")
            if torneo_selec:
                df_torneo = df_full_torneos[df_full_torneos['nombre_torneo'] == torneo_selec].copy()
                df_torneo['Resultado_Raw'] = df_torneo['resultado']
                df_torneo['Mi Lugar alcanzado'] = df_torneo.apply(determinar_lugar, axis=1)
                cols_mostrar = ['ronda', 'Poomsae', 'Nota Final', 'nombre_rival', 'rival_nota_final', 'Mi Lugar alcanzado', 'comentarios']
                rename_dict = {'nombre_rival': 'Rival', 'rival_nota_final': 'Nota Rival', 'comentarios': 'Comentarios'}
                if 'ronda' in df_torneo.columns: rename_dict['ronda'] = 'Ronda'
                df_tabla = df_torneo[cols_mostrar].rename(columns=rename_dict)
                st.dataframe(df_tabla, use_container_width=True)
        else:
            st.info("Aún no tienes torneos registrados.")
    except Exception as e:
        st.error(f"Error cargando métricas: {e}")

# --- 8. FUNCIÓN PANEL ADMINISTRADOR ---
def mostrar_admin_users():
    st.title("👮 Panel de Administrador")
    st.info("Listado completo de atletas registrados en la base de datos.")
    try:
        with st.spinner("Cargando base de datos..."):
            resp = supabase.table("perfiles").select("*").execute()
            df_users = pd.DataFrame(resp.data)
            if not df_users.empty:
                cols = ['nombre_completo', 'email', 'grado', 'categoria', 'edad', 'genero', 'created_at']
                cols_final = [c for c in cols if c in df_users.columns]
                st.dataframe(df_users[cols_final], use_container_width=True)
                st.metric("Total Usuarios", len(df_users))
            else:
                st.warning("No hay usuarios registrados en la tabla perfiles.")
    except Exception as e:
        st.error(f"Error al cargar usuarios: {e}")

# --- 9. MAIN LOOP ---
def main():
    if not st.session_state.user:
        # LOGIN
        c_espacio1, c_central, c_espacio2 = st.columns([1, 2, 1])
        with c_central:
            st.markdown(f'''
                <div class="logo-login-container">
                    <img src="{logo_b64}" class="logo-login-img">
                </div>
            ''', unsafe_allow_html=True)
            
            t1, t2 = st.tabs(["Entrar", "Crear Cuenta"])
            with t1:
                el = st.text_input("Email", key="le")
                pl = st.text_input("Pass", type="password", key="lp")
                if st.button("Iniciar Sesión", type="primary", use_container_width=True): login(el, pl)
            with t2:
                nn = st.text_input("Nombre", key="rn")
                ne = st.text_input("Email", key="re")
                np = st.text_input("Pass", type="password", key="rp")
                if st.button("Registrarse", use_container_width=True): sign_up(ne, np, nn)
    else:
        # APP PRINCIPAL
        if not st.session_state.perfil: cargar_perfil()
        p = st.session_state.perfil
        foto = p.get('foto_url') if p else "https://cdn-icons-png.flaticon.com/512/847/847969.png"
        nom = p.get('nombre_completo', "Atleta")
        
        with st.sidebar:
            try: st.image("logo-taescorer.png")
            except: pass
            st.markdown(f"""
                <style>
                    .avatar-img {{ width: 100px; height: 100px; border-radius: 50%; object-fit: cover; display: block; margin: 0 auto; border: 2px solid #3498db; }}
                    .user-name {{ text-align: center; font-weight: bold; margin-top: 10px; font-size: 1.1rem; }}
                </style>
                <img src="{foto}" class="avatar-img">
                <p class="user-name">{nom}</p>
            """, unsafe_allow_html=True)
            
            # 1. PERFIL
            if st.button("Ir a Mi Perfil", use_container_width=True): st.session_state.page_selection = "Mi Perfil"; st.rerun()
            st.divider()
            
            # BLOQUE UNIDO DE BOTONES
            if st.button("Dashboard", use_container_width=True): st.session_state.page_selection = "Dashboard"; st.rerun()
            if st.button("Registrar Resultados", use_container_width=True): st.session_state.page_selection = "Registrar Torneo"; st.rerun()
            if st.button("Base de Torneos", use_container_width=True): st.session_state.page_selection = "Base de Torneos"; st.rerun()
            if st.button("Calendario", use_container_width=True): st.session_state.page_selection = "Calendario"; st.rerun() 
            
            st.divider()
            # 6. SALIR
            if st.button("Salir", use_container_width=True): logout()

            # --- ZONA DE ADMINISTRADOR ---
            if st.session_state.user.email == "williamgazzu@gmail.com": 
                st.divider()
                st.caption("🔒 Admin Zone")
                if st.button("Ver Usuarios", use_container_width=True):
                    st.session_state.page_selection = "Admin Users"
                    st.rerun()

        # ROUTER DE PÁGINAS
        if st.session_state.page_selection == "Dashboard": mostrar_dashboard()
        elif st.session_state.page_selection == "Registrar Torneo": mostrar_formulario_registro()
        elif st.session_state.page_selection == "Base de Torneos": mostrar_historial_editor()
        elif st.session_state.page_selection == "Calendario": mostrar_calendario() 
        elif st.session_state.page_selection == "Mi Perfil": mostrar_perfil()
        elif st.session_state.page_selection == "Admin Users": mostrar_admin_users()

if __name__ == "__main__":
    main()
