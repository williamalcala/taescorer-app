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

logo_b64 = get_image_base64("logotaescorer.png")

# --- 2. CONEXIÓN BASE DE DATOS (CLIENTE POR SESIÓN) ---
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

def get_supabase():
    """Crea un cliente Supabase fresco por cada llamada, autenticado con el token del usuario actual.
    Esto evita que múltiples usuarios compartan el mismo cliente y vean datos cruzados."""
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    if 'access_token' in st.session_state and 'refresh_token' in st.session_state:
        try:
            client.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
        except Exception:
            pass
    return client

# Cliente para operaciones SIN sesión (login y signup)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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

LUGARES_COMPETICION = [
    "1er Lugar", "2do Lugar", "3er Lugar", "4to Lugar", "5to Lugar", 
    "6to Lugar", "7mo Lugar", "8vo Lugar", "9no Lugar", "10mo Lugar", 
    "Participación"
]

# --- 4. CSS MAESTRO ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}
    .stApp {{ background-color: #1f202b !important; }}
    div[data-testid="stDialog"] {{ background-color: #1f202b !important; }}
    header[data-testid="stHeader"] {{ background-color: #1f202b !important; }}
    .stDeployButton, footer, .viewerBadge_container__1QSob, div[class^="viewerBadge_"] {{ display: none !important; visibility: hidden !important; }}
    .logo-login-container {{ display: flex; justify-content: center; width: 100%; margin-bottom: 20px; }}
    .logo-login-img {{ width: 50%; max-width: 300px; height: auto; object-fit: contain; }}
    @media (max-width: 768px) {{ .logo-login-img {{ width: 30% !important; }} }}
    section[data-testid="stSidebar"] div[data-testid="stImage"] img {{ display: block !important; margin-left: auto !important; margin-right: auto !important; width: 50% !important; align-self: center !important; }}
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {{ gap: 0rem !important; }}
    section[data-testid="stSidebar"] button {{ border: none !important; color: white !important; font-weight: 600 !important; box-shadow: none !important; width: 100% !important; transition: all 0.2s !important; }}
    section[data-testid="stSidebar"] button:hover {{ filter: brightness(1.15) !important; z-index: 10 !important; }}
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
""", unsafe_allow_html=True)

# --- GESTIÓN DE SESIÓN ---
if 'user' not in st.session_state: st.session_state.user = None
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'page_selection' not in st.session_state: st.session_state.page_selection = "Dashboard"

# ==========================================
# FUNCIONES DE LÓGICA 
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
    try: supabase.auth.sign_out()
    except: pass
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.query_params.clear()
    st.rerun()

def cargar_perfil():
    if st.session_state.user:
        try:
            data = get_supabase().table("perfiles").select("*").eq("id", st.session_state.user.id).execute()
            if data.data: st.session_state.perfil = data.data[0]
            else: st.session_state.perfil = {}
        except: pass

def actualizar_perfil(datos, archivo_foto_bytes):
    user_id = st.session_state.user.id
    foto_url = st.session_state.perfil.get('foto_url') if st.session_state.perfil else None
    
    if archivo_foto_bytes:
        try:
            file_path = f"{user_id}/avatar.jpg"
            sb = get_supabase()
            sb.storage.from_("avatars").upload(file_path, archivo_foto_bytes, {"content-type": "image/jpeg", "upsert": "true"})
            foto_url = sb.storage.from_("avatars").get_public_url(file_path) + f"?t={int(time.time())}"
        except Exception as e:
            st.error(f"Error al subir la foto: {e}")
            
    try:
        with st.spinner("Guardando perfil..."):
            datos_actualizados = {"id": user_id, **datos}
            if foto_url: datos_actualizados["foto_url"] = foto_url
            get_supabase().table("perfiles").upsert(datos_actualizados).execute()
            st.success("✅ Perfil guardado correctamente.")
            cargar_perfil()
            time.sleep(1)
            st.rerun()
    except Exception as e: 
        st.error(f"Error técnico al guardar en base de datos: {e}")

def get_lista_rivales():
    try:
        user_id = st.session_state.user.id
        resp = get_supabase().table("registros_poomsae").select("nombre_rival").eq("user_id", user_id).execute()
        df = pd.DataFrame(resp.data)
        return sorted(df['nombre_rival'].dropna().unique().tolist()) if not df.empty else []
    except: return []

def guardar_torneo(datos_torneo, lista_poomsaes):
    user_id = st.session_state.user.id
    try:
        with st.spinner("Guardando torneo..."):
            sb = get_supabase()
            data_torneo = {"user_id": user_id, "nombre_torneo": datos_torneo["nombre"], "fecha_torneo": str(datos_torneo["fecha"]), "categoria": datos_torneo["categoria"], "modalidad": datos_torneo["modalidad"]}
            res_torneo = sb.table("torneos").insert(data_torneo).execute()
            torneo_id = res_torneo.data[0]['id']
            poomsaes_a_insertar = []
            for p in lista_poomsaes:
                poomsaes_a_insertar.append({"user_id": user_id, "torneo_id": torneo_id, "ronda": p["ronda"], "nombre_poomsae": p["nombre"], "mi_nota_tecnica": p["mi_tec"], "mi_nota_presentacion": p["mi_pres"], "mi_nota_final": p["mi_total"], "nombre_rival": p["rival_nombre"], "rival_nota_tecnica": p["rival_tec"], "rival_nota_presentacion": p["rival_pres"], "rival_nota_final": p["rival_total"], "resultado": p["resultado"], "comentarios": p["comentarios"]})
            sb.table("registros_poomsae").insert(poomsaes_a_insertar).execute()
            return True
    except: return False

def guardar_evento_agenda(nombre, inicio, fin, estatus, comentarios, asistencia="⏳ Pendiente"):
    user_id = st.session_state.user.id
    try:
        with st.spinner("Agendando..."):
            data = {
                "user_id": user_id, 
                "nombre": nombre, 
                "fecha_inicio": str(inicio), 
                "fecha_fin": str(fin), 
                "estatus": estatus, 
                "comentarios": comentarios,
                "asistencia": asistencia
            }
            get_supabase().table("agenda").insert(data).execute()
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
        resultados = df_t['resultado'].astype(str).tolist()
        rondas = df_t['ronda'].astype(str).tolist()
        
        # Nueva Lógica de Medallas (Basada en el Lugar explícito seleccionado)
        if any('1er Lugar' in r for r in resultados):
            conteo["Oro"] += 1
        elif any('2do Lugar' in r for r in resultados):
            conteo["Plata"] += 1
        elif any('3er Lugar' in r for r in resultados) or any('4to Lugar' in r for r in resultados):
            conteo["Bronce"] += 1
        elif any('Lugar' in r for r in resultados) or any('Participación' in r for r in resultados):
            conteo["Participacion"] += 1
        else:
            # Lógica antigua de rescate (para torneos registrados antes de esta actualización)
            ronda_max = ""
            if any("Final" in r for r in rondas): ronda_max = "Final"
            elif any("Semi" in r for r in rondas): ronda_max = "Semi"
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
    # Extraer el lugar de la nueva columna resultado si existe
    res_raw = str(row.get('Resultado_Raw', ''))
    if " - " in res_raw:
        return res_raw.split(" - ")[1]
        
    # Lógica antigua de rescate
    ronda = str(row.get('ronda', ''))
    if "Final" in ronda: return "🥇 1er Lugar" if res_raw == "Ganador" else "🥈 2do Lugar"
    elif "Semi" in ronda: return "🥈 Plata" if res_raw == "Ganador" else "🥉 3er Lugar"
    elif "4tos" in ronda: return "5to - 8vo Lugar"
    else: return "Participación"

# ==========================================
# PANTALLAS VISUALES
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
        n = st.text_input("Nombre Completo", value=p.get('nombre_completo', ''))
        edad_actual = p.get('edad')
        try: edad_actual = int(edad_actual) if edad_actual is not None else 18
        except: edad_actual = 18
        e = st.number_input("Edad", 5, 99, value=edad_actual)
        cat_val = p.get('categoria')
        cat_idx = CATEGORIAS_POOMSAE.index(cat_val) if cat_val in CATEGORIAS_POOMSAE else 0
        cat = st.selectbox("Categoría", CATEGORIAS_POOMSAE, index=cat_idx)
        gr_val = p.get('grado')
        gr_idx = GRADOS_TKD.index(gr_val) if gr_val in GRADOS_TKD else 0
        gr = st.selectbox("Grado", GRADOS_TKD, index=gr_idx)
        gen_val = p.get('genero')
        gen_idx = ["Masculino", "Femenino"].index(gen_val) if gen_val in ["Masculino", "Femenino"] else 0
        gen = st.radio("Género", ["Masculino", "Femenino"], index=gen_idx, horizontal=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Guardar Cambios", type="primary", use_container_width=True): 
            actualizar_perfil({"nombre_completo": n, "edad": int(e), "categoria": cat, "grado": gr, "genero": gen}, img_bytes)


def mostrar_formulario_registro():
    st.header("📝 Nuevo Torneo (Resultados)")
    st.info("Ingresa tus notas P1 y P2. Recuerda que el 1er lugar es Ganador y el resto es Perdedor para las métricas.")
    rivales_existentes = get_lista_rivales()
    
    # 1. Ajuste Visual: Modalidad visible como selectbox
    c1, c2, c3, c4 = st.columns(4)
    nom = c1.text_input("Nombre del torneo", key="t_nombre")
    fec = c2.date_input("Fecha", date.today(), key="t_fecha")
    cat = c3.selectbox("Categoría", ["Elite", "Liga", "G2", "Open"], key="t_cat")
    mod = c4.selectbox("Modalidad", ["Individual", "Pareja", "Equipo", "Freestyle"], key="t_mod")
    
    n_rondas = st.number_input("Cantidad de rondas a registrar", 1, 5, 1, key="t_rondas")
    st.divider()
    
    datos_rondas = []
    tipos = ["Preliminar", "8vos", "4tos", "Semi", "Final"]
    
    for i in range(n_rondas):
        st.subheader(f"🥋 Ronda {i+1}")
        cr1, cr2, cr3 = st.columns(3)
        tr = cr1.selectbox(f"Fase {i+1}", tipos, key=f"tr_{i}")
        
        # 2. Selector de Puesto / Lugar
        lugar_obtenido = cr2.selectbox(f"Lugar en {tr}", LUGARES_COMPETICION, key=f"lugar_{i}")
        
        opcion_rival = cr3.selectbox(f"Rival (Ronda {i+1})", ["➕ Nuevo Rival..."] + rivales_existentes, key=f"sel_riv_{i}")
        if opcion_rival == "➕ Nuevo Rival...": 
            nr = st.text_input(f"Escribe nombre del rival (Ronda {i+1})", key=f"text_riv_{i}")
        else: 
            nr = opcion_rival
            
        comentarios = st.text_area(f"Comentarios Ronda {i+1}", key=f"comm_{i}")

        tp1, tp2 = st.tabs(["Poomsae 1", "Poomsae 2"])
        with tp1:
            np1 = st.selectbox("Poomsae", LISTA_POOMSAE_OFICIAL, key=f"np1_{i}")
            c_m1, c_m2, c_m3 = st.columns(3)
            mt1 = c_m1.number_input("Mi nota técnica", 0.0, 4.0, step=0.01, key=f"mt1_{i}")
            mp1 = c_m2.number_input("Mi nota presentación", 0.0, 6.0, step=0.01, key=f"mp1_{i}")
            total_yo_1 = mt1 + mp1
            c_m3.metric("Final P1", f"{total_yo_1:.2f}")
            
            c_r1, c_r2, c_r3 = st.columns(3)
            rt1 = c_r1.number_input("Rival técnica", 0.0, 4.0, step=0.01, key=f"rt1_{i}")
            rp1 = c_r2.number_input("Rival presentación", 0.0, 6.0, step=0.01, key=f"rp1_{i}")
            total_riv_1 = rt1 + rp1
            c_r3.metric("Final P1 (Rival)", f"{total_riv_1:.2f}")
            
        with tp2:
            np2 = st.selectbox("Poomsae", LISTA_POOMSAE_OFICIAL, key=f"np2_{i}")
            c_m1, c_m2, c_m3 = st.columns(3)
            mt2 = c_m1.number_input("Mi nota técnica", 0.0, 4.0, step=0.01, key=f"mt2_{i}")
            mp2 = c_m2.number_input("Mi nota presentación", 0.0, 6.0, step=0.01, key=f"mp2_{i}")
            total_yo_2 = mt2 + mp2
            c_m3.metric("Final P2", f"{total_yo_2:.2f}")
            
            c_r1, c_r2, c_r3 = st.columns(3)
            rt2 = c_r1.number_input("Rival técnica", 0.0, 4.0, step=0.01, key=f"rt2_{i}")
            rp2 = c_r2.number_input("Rival presentación", 0.0, 6.0, step=0.01, key=f"rp2_{i}")
            total_riv_2 = rt2 + rp2
            c_r3.metric("Final P2 (Rival)", f"{total_riv_2:.2f}")

        # 3. Lógica de Victoria estricta: Solo 1er Lugar = Ganador.
        if lugar_obtenido == "1er Lugar":
            res = f"Ganador - {lugar_obtenido}"
        else:
            res = f"Perdedor - {lugar_obtenido}"
            
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
                    if key in keys_a_borrar or any(x in key for x in ["np1_", "mt1_", "mp1_", "rt1_", "rp1_", "np2_", "mt2_", "mp2_", "rt2_", "rp2_", "tr_", "nr_", "sel_riv_", "text_riv_", "comm_", "lugar_"]):
                        del st.session_state[key]
                time.sleep(1.5)
                st.rerun()
        else: st.warning("⚠️ Debes escribir el nombre del torneo.")


def mostrar_calendario():
    st.title("📅 Calendario de Torneos")
    st.info("Visualiza todo tu año competitivo, agrega nuevas fechas y gestiona tus eventos desde la lista.")
    
    # --- 1. AGREGAR EVENTO ---
    st.subheader("➕ Agregar Nuevo Evento")
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
                # Al agendar desde aquí, la asistencia por defecto será "⏳ Pendiente"
                if guardar_evento_agenda(evt_nombre, evt_inicio, evt_fin, evt_estatus, evt_coment):
                    st.success("Evento agregado exitosamente.")
                    time.sleep(1)
                    st.rerun()
            else: st.warning("Por favor, ingresa el nombre del evento.")

    st.divider()

    # Obtener eventos de la base de datos
    try: 
        eventos_db = get_supabase().table("agenda").select("*").eq("user_id", st.session_state.user.id).execute().data
    except: 
        eventos_db = []

    # --- 2. VISTA DE CALENDARIO (TODO EL AÑO) ---
    st.subheader("👁️ Vista Anual de Eventos")
    calendar_events = []
    for evt in eventos_db:
        color = "#3788d8"
        if evt['estatus'] == "Confirmado": color = "#28a745"
        elif evt['estatus'] == "Sin Confirmar": color = "#dc3545"
        elif evt['estatus'] == "Internacional": color = "#007bff"
        
        # Añadimos un pequeño indicador visual al título del calendario si ya se definió asistencia
        prefijo = ""
        asist = evt.get('asistencia', "⏳ Pendiente")
        if asist == "✅ Asistí": prefijo = "✅ "
        elif asist == "❌ No Asistí": prefijo = "❌ "

        calendar_events.append({
            "title": f"{prefijo}{evt['nombre']}", 
            "start": evt['fecha_inicio'], 
            "end": str(pd.to_datetime(evt['fecha_fin']) + timedelta(days=1)).split(" ")[0], 
            "backgroundColor": color, 
            "borderColor": color, 
            "extendedProps": {"description": evt.get('comentarios', '')}
        })

    # Opciones para mostrar "multiMonthYear"
    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next", 
            "center": "title", 
            "right": "multiMonthYear,dayGridMonth"
        }, 
        "buttonText": {
            "today": "Hoy", 
            "year": "Año", 
            "month": "Mes"
        }, 
        "initialView": "multiMonthYear", 
        "locale": "es", 
        "height": 850
    }
    
    if calendar: 
        st_calendar = calendar(events=calendar_events, options=calendar_options)

    st.divider()

    # --- 3. LISTADO DE EVENTOS (ORDENADO Y EDITABLE) ---
    st.subheader("📋 Listado y Edición de Eventos")
    st.markdown("Aquí puedes ver todos tus eventos ordenados por fecha. **Puedes editar cualquier dato directamente en la tabla**.")
    
    if eventos_db:
        df_agenda = pd.DataFrame(eventos_db)
        df_agenda['fecha_inicio'] = pd.to_datetime(df_agenda['fecha_inicio']).dt.date
        df_agenda['fecha_fin'] = pd.to_datetime(df_agenda['fecha_fin']).dt.date
        
        # Asegurar que la columna 'asistencia' exista en el DataFrame (por los registros viejos)
        if 'asistencia' not in df_agenda.columns:
            df_agenda['asistencia'] = "⏳ Pendiente"
        else:
            df_agenda['asistencia'] = df_agenda['asistencia'].fillna("⏳ Pendiente")
        
        # Ordenar por fecha cronológicamente
        df_agenda = df_agenda.sort_values(by="fecha_inicio", ascending=True).reset_index(drop=True)
        
        column_config = {
            "id": None, "user_id": None, "created_at": None, "nombre": "Nombre del Evento",
            "fecha_inicio": st.column_config.DateColumn("Fecha Inicio"), 
            "fecha_fin": st.column_config.DateColumn("Fecha Fin"),
            "estatus": st.column_config.SelectboxColumn("Estatus", options=["Confirmado", "Sin Confirmar", "Internacional"]),
            "asistencia": st.column_config.SelectboxColumn("Asistencia", options=["⏳ Pendiente", "✅ Asistí", "❌ No Asistí"]),
            "comentarios": "Comentarios Adicionales"
        }
        
        edited_df = st.data_editor(df_agenda, column_config=column_config, use_container_width=True, hide_index=True)

        if st.button("💾 Guardar Cambios en la Lista", type="primary"):
            with st.spinner("Sincronizando agenda..."):
                sb = get_supabase()
                ids_originales = [row['id'] for row in eventos_db]
                ids_finales = []
                for index, row in edited_df.iterrows():
                    if pd.notna(row.get('id')):
                        ids_finales.append(row['id'])
                        sb.table("agenda").update({
                            "nombre": row['nombre'], 
                            "fecha_inicio": str(row['fecha_inicio']), 
                            "fecha_fin": str(row['fecha_fin']), 
                            "estatus": row['estatus'], 
                            "asistencia": row['asistencia'],
                            "comentarios": row['comentarios']
                        }).eq("id", row['id']).execute()
                    else: 
                        guardar_evento_agenda(row['nombre'], row['fecha_inicio'], row['fecha_fin'], row['estatus'], row['comentarios'], row['asistencia'])
                
                for old_id in ids_originales:
                    if old_id not in ids_finales: sb.table("agenda").delete().eq("id", old_id).execute()
            
            st.success("Lista de eventos actualizada correctamente.")
            time.sleep(1)
            st.rerun()
    else: 
        st.info("Aún no tienes eventos registrados en tu agenda.")


def mostrar_historial_editor():
    st.header("📝 Base de Torneos")
    st.info("Aquí puedes editar todos los datos de tus torneos, ver los promedios finales y eliminar los que no necesites.")
    user_id = st.session_state.user.id
    
    try:
        torneos_resp = get_supabase().table("torneos").select("*").eq("user_id", user_id).order("fecha_torneo", desc=True).execute()
        df_torneos = pd.DataFrame(torneos_resp.data)
        
        if df_torneos.empty:
            st.warning("No tienes torneos registrados.")
            return
        
        opciones_lista = ["Ver Todos"] + [f"{row['nombre_torneo']} ({row['fecha_torneo']})" for idx, row in df_torneos.iterrows()]
        mapa_torneos = {f"{row['nombre_torneo']} ({row['fecha_torneo']})": row['id'] for idx, row in df_torneos.iterrows()}
        
        seleccion = st.selectbox("Selecciona un Torneo:", opciones_lista)
        st.divider()

        if seleccion == "Ver Todos":
            # ====== MODO "VER TODOS" ======
            st.subheader("📋 Todos los Torneos (Editar Metadata)")
            df_torneos_edit = df_torneos.copy()
            df_torneos_edit['fecha_torneo'] = pd.to_datetime(df_torneos_edit['fecha_torneo']).dt.date
            
            col_config_torneos = {
                "id": None, "user_id": None, "created_at": None,
                "nombre_torneo": "Nombre del Torneo",
                "fecha_torneo": st.column_config.DateColumn("Fecha"),
                "categoria": st.column_config.SelectboxColumn("Categoría", options=["Elite", "Liga", "G2", "Open"]),
                "modalidad": st.column_config.SelectboxColumn("Modalidad", options=["Individual", "Pareja", "Equipo", "Freestyle"])
            }
            
            edited_torneos = st.data_editor(df_torneos_edit, column_config=col_config_torneos, use_container_width=True, hide_index=True)
            
            if st.button("💾 Guardar Cambios de Torneos (Nombres/Fechas)", type="primary"):
                with st.spinner("Actualizando metadata de torneos..."):
                    sb = get_supabase()
                    for idx, row in edited_torneos.iterrows():
                        sb.table("torneos").update({
                            "nombre_torneo": row['nombre_torneo'], "fecha_torneo": str(row['fecha_torneo']),
                            "categoria": row['categoria'], "modalidad": row['modalidad']
                        }).eq("id", row['id']).execute()
                    st.success("✅ Torneos actualizados.")
                    time.sleep(1)
                    st.rerun()

            st.divider()
            
            # --- PROMEDIOS FINALES (TODOS) ---
            st.subheader("📊 Promedios Finales por Ronda (Todos los Torneos)")
            registros_resp = get_supabase().table("registros_poomsae").select("*, torneos(nombre_torneo)").eq("user_id", user_id).execute()
            df_reg_all = pd.DataFrame(registros_resp.data)
            
            if not df_reg_all.empty:
                df_reg_all['Torneo'] = df_reg_all['torneos'].apply(lambda x: x['nombre_torneo'] if x else '-')
                df_promedios = df_reg_all.copy()
                df_promedios['Ronda Base'] = df_promedios['ronda'].apply(lambda x: str(x).split(" (")[0])
                
                promedios_all = df_promedios.groupby(['Torneo', 'Ronda Base', 'nombre_rival']).agg({
                    'mi_nota_final': 'mean',
                    'rival_nota_final': 'mean',
                    'resultado': 'first' # Tomamos el resultado para mostrarlo
                }).reset_index()

                promedios_all = promedios_all.rename(columns={
                    'nombre_rival': 'Rival', 'mi_nota_final': 'Mi Promedio Ronda', 
                    'rival_nota_final': 'Promedio Rival', 'resultado': 'Lugar Obtenido'
                })
                
                st.dataframe(promedios_all.style.format({'Mi Promedio Ronda': "{:.2f}", 'Promedio Rival': "{:.2f}"}), use_container_width=True, hide_index=True)
                
            st.divider()
            st.subheader("✏️ Editar Todos los Poomsaes Individuales")
            if not df_reg_all.empty:
                # Extraer "Lugar" del resultado para poder editarlo fácilmente
                df_reg_all['Lugar'] = df_reg_all['resultado'].apply(lambda x: str(x).split(" - ")[1] if " - " in str(x) else ("1er Lugar" if "Ganador" in str(x) else "Participación"))
                
                col_config_reg = {
                    "id": None, "user_id": None, "torneo_id": None, "created_at": None, "torneos": None, "Torneo": "Torneo",
                    "nombre_poomsae": "Poomsae", "ronda": "Ronda",
                    "mi_nota_tecnica": st.column_config.NumberColumn("Mi Técnica", min_value=0.0, max_value=4.0, step=0.01),
                    "mi_nota_presentacion": st.column_config.NumberColumn("Mi Pres.", min_value=0.0, max_value=6.0, step=0.01),
                    "mi_nota_final": None, "nombre_rival": "Rival",
                    "rival_nota_tecnica": st.column_config.NumberColumn("Riv. Técnica", min_value=0.0, max_value=4.0, step=0.01),
                    "rival_nota_presentacion": st.column_config.NumberColumn("Riv. Pres.", min_value=0.0, max_value=6.0, step=0.01),
                    "rival_nota_final": None, "resultado": None, "comentarios": "Comentarios",
                    "Lugar": st.column_config.SelectboxColumn("Lugar Obtenido", options=LUGARES_COMPETICION)
                }
                edited_regs = st.data_editor(df_reg_all, column_config=col_config_reg, use_container_width=True, hide_index=True)
                
                if st.button("💾 Guardar Cambios en Poomsaes", type="primary"):
                    with st.spinner("Guardando poomsaes..."):
                        sb = get_supabase()
                        for index, row in edited_regs.iterrows():
                            mi_total = round(row['mi_nota_tecnica'] + row['mi_nota_presentacion'], 2)
                            riv_total = round(row['rival_nota_tecnica'] + row['rival_nota_presentacion'], 2)
                            lugar = row.get('Lugar', 'Participación')
                            res = f"Ganador - {lugar}" if lugar == "1er Lugar" else f"Perdedor - {lugar}"
                            
                            update_data = {
                                "nombre_poomsae": row['nombre_poomsae'], "ronda": row['ronda'], "nombre_rival": row['nombre_rival'],
                                "mi_nota_tecnica": row['mi_nota_tecnica'], "mi_nota_presentacion": row['mi_nota_presentacion'], "mi_nota_final": mi_total,
                                "rival_nota_tecnica": row['rival_nota_tecnica'], "rival_nota_presentacion": row['rival_nota_presentacion'], "rival_nota_final": riv_total, "resultado": res,
                                "comentarios": row.get('comentarios', '')
                            }
                            sb.table("registros_poomsae").update(update_data).eq("id", row['id']).execute()
                        st.success("✅ Poomsaes actualizados.")
                        time.sleep(1)
                        st.rerun()

        else:
            # ====== MODO "TORNEO ESPECÍFICO" ======
            torneo_id_selec = mapa_torneos[seleccion]
            torneo_info = df_torneos[df_torneos['id'] == torneo_id_selec].iloc[0]

            st.subheader("⚙️ Editar Datos del Torneo")
            c1, c2, c3, c4 = st.columns(4)
            t_nombre = c1.text_input("Nombre Torneo", value=torneo_info['nombre_torneo'])
            
            try: t_fecha_val = pd.to_datetime(torneo_info['fecha_torneo']).date()
            except: t_fecha_val = date.today()
            t_fecha = c2.date_input("Fecha", value=t_fecha_val)
            
            cats = ["Elite", "Liga", "G2", "Open"]
            t_cat = c3.selectbox("Categoría", cats, index=cats.index(torneo_info['categoria']) if torneo_info['categoria'] in cats else 0)
            
            mods = ["Individual", "Pareja", "Equipo", "Freestyle"]
            t_mod = c4.selectbox("Modalidad", mods, index=mods.index(torneo_info['modalidad']) if torneo_info['modalidad'] in mods else 0)

            # --- BOTONES DE GUARDAR O ELIMINAR ---
            col_btn_guardar, col_btn_borrar = st.columns(2)
            with col_btn_guardar:
                if st.button("💾 Guardar Datos del Torneo", use_container_width=True):
                    get_supabase().table("torneos").update({
                        "nombre_torneo": t_nombre, "fecha_torneo": str(t_fecha), "categoria": t_cat, "modalidad": t_mod
                    }).eq("id", torneo_id_selec).execute()
                    st.success("Info del torneo actualizada.")
                    time.sleep(1)
                    st.rerun()

            with col_btn_borrar:
                eliminar_check = st.checkbox("Habilitar botón de borrado")
                if eliminar_check:
                    if st.button("🗑️ Eliminar Torneo Definitivamente", type="primary", use_container_width=True):
                        with st.spinner("Eliminando torneo y sus registros..."):
                            sb = get_supabase()
                            sb.table("registros_poomsae").delete().eq("torneo_id", torneo_id_selec).execute()
                            sb.table("torneos").delete().eq("id", torneo_id_selec).execute()
                        st.success("Torneo eliminado correctamente.")
                        time.sleep(1)
                        st.rerun()

            st.divider()
            
            registros_resp = get_supabase().table("registros_poomsae").select("*").eq("torneo_id", torneo_id_selec).execute()
            df_registros = pd.DataFrame(registros_resp.data)
            
            if not df_registros.empty:
                st.subheader("📊 NOTA FINAL (Promedio de la Ronda)")
                df_promedios = df_registros.copy()
                df_promedios['Ronda Base'] = df_promedios['ronda'].apply(lambda x: str(x).split(" (")[0])
                
                prom_group = df_promedios.groupby(['Ronda Base', 'nombre_rival']).agg({
                    'mi_nota_final': 'mean',
                    'rival_nota_final': 'mean',
                    'resultado': 'first'
                }).reset_index()

                prom_group = prom_group.rename(columns={
                    'nombre_rival': 'Rival', 'mi_nota_final': 'Mi Promedio Ronda', 
                    'rival_nota_final': 'Promedio Rival', 'resultado': 'Lugar Obtenido'
                })
                
                st.dataframe(prom_group.style.format({'Mi Promedio Ronda': "{:.2f}", 'Promedio Rival': "{:.2f}"}), use_container_width=True, hide_index=True)
                st.divider()

            st.subheader("✏️ Editar Poomsaes Individuales")
            if not df_registros.empty:
                df_registros['Lugar'] = df_registros['resultado'].apply(lambda x: str(x).split(" - ")[1] if " - " in str(x) else ("1er Lugar" if "Ganador" in str(x) else "Participación"))
                
                col_config = {
                    "id": None, "user_id": None, "torneo_id": None, "created_at": None,
                    "nombre_poomsae": "Poomsae", "ronda": "Ronda",
                    "mi_nota_tecnica": st.column_config.NumberColumn("Mi Técnica", min_value=0.0, max_value=4.0, step=0.01),
                    "mi_nota_presentacion": st.column_config.NumberColumn("Mi Pres.", min_value=0.0, max_value=6.0, step=0.01),
                    "mi_nota_final": None, "nombre_rival": "Nombre Rival",
                    "rival_nota_tecnica": st.column_config.NumberColumn("Riv. Técnica", min_value=0.0, max_value=4.0, step=0.01),
                    "rival_nota_presentacion": st.column_config.NumberColumn("Riv. Pres.", min_value=0.0, max_value=6.0, step=0.01),
                    "rival_nota_final": None, "resultado": None, "comentarios": "Comentarios",
                    "Lugar": st.column_config.SelectboxColumn("Lugar Obtenido", options=LUGARES_COMPETICION)
                }
                
                edited_df = st.data_editor(df_registros, column_config=col_config, use_container_width=True, hide_index=True)
                
                if st.button("💾 Guardar Notas", type="primary"):
                    with st.spinner("Guardando cambios..."):
                        sb = get_supabase()
                        for index, row in edited_df.iterrows():
                            mi_total = round(row['mi_nota_tecnica'] + row['mi_nota_presentacion'], 2)
                            riv_total = round(row['rival_nota_tecnica'] + row['rival_nota_presentacion'], 2)
                            lugar = row.get('Lugar', 'Participación')
                            res = f"Ganador - {lugar}" if lugar == "1er Lugar" else f"Perdedor - {lugar}"
                            
                            update_data = {
                                "nombre_poomsae": row['nombre_poomsae'], "ronda": row['ronda'], "nombre_rival": row['nombre_rival'],
                                "mi_nota_tecnica": row['mi_nota_tecnica'], "mi_nota_presentacion": row['mi_nota_presentacion'], "mi_nota_final": mi_total,
                                "rival_nota_tecnica": row['rival_nota_tecnica'], "rival_nota_presentacion": row['rival_nota_presentacion'], "rival_nota_final": riv_total, "resultado": res,
                                "comentarios": row.get('comentarios', '')
                            }
                            sb.table("registros_poomsae").update(update_data).eq("id", row['id']).execute()
                        st.success("✅ Datos actualizados correctamente.")
                        time.sleep(1)
                        st.rerun()

    except Exception as e: st.error(f"Error cargando historial: {e}")


def mostrar_dashboard():
    user_id = st.session_state.user.id
    try:
        data = get_supabase().table("registros_poomsae").select("*, torneos(nombre_torneo, fecha_torneo)").eq("user_id", user_id).execute()
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
            # Solo los poomsaes marcados como "Ganador" (que ahora es exclusivamente 1er Lugar) cuentan
            wins = len(df_gen[df_gen['resultado'].astype(str).str.contains('Ganador')]) if total_matches > 0 else 0
            winrate = (wins / total_matches * 100) if total_matches > 0 else 0
            promedio = df_gen['Nota Final'].mean() if total_matches > 0 else 0

            c_win.metric("Winrate (1er Lugar)", f"{winrate:.1f}%", f"{wins} Oros / {total_matches} Rondas")
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
            resp = get_supabase().table("perfiles").select("*").execute()
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
            try: st.image("logotaescorer.png")
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
            if st.session_state.perfil and st.session_state.perfil.get('rol') == 'admin': 
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
