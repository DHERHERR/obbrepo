import math
from pathlib import Path
from datetime import datetime
from collections import Counter
import re
import random

import pandas as pd
import pydeck as pdk
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# --- Configuracion basica ---
st.set_page_config(
    page_title="Train Stations Map - Austria",
    page_icon="\U0001F682",
    layout="wide",
)

FILE_OPINIONES = Path(__file__).with_name("opiniones_austria.csv")

STATIONS_DATA = [
    {"estacion": "Hauptbahnhof", "ciudad": "Viena", "lat": 48.186667, "lon": 16.38, "linea": "Nodo principal Este"},
    {"estacion": "Mitte (Landstrasse)", "ciudad": "Viena", "lat": 48.206389, "lon": 16.384722, "linea": "S-Bahn / CAT"},
    {"estacion": "Floridsdorf", "ciudad": "Viena", "lat": 48.256389, "lon": 16.4, "linea": "Norte / S-Bahn"},
    {"estacion": "Hetzendorf", "ciudad": "Viena", "lat": 48.147, "lon": 16.322, "linea": "S1 / S2"},
    {"estacion": "Liesing", "ciudad": "Viena", "lat": 48.1541, "lon": 16.2925, "linea": "S2 / S3 / S4"},
    {"estacion": "Handelskai", "ciudad": "Viena", "lat": 48.2377, "lon": 16.3861, "linea": "S45 / S7"},
    {"estacion": "Praterstern", "ciudad": "Viena", "lat": 48.2168, "lon": 16.3924, "linea": "S1 / S2 / S3 / S7"},
    {"estacion": "Rennweg", "ciudad": "Viena", "lat": 48.201, "lon": 16.3935, "linea": "S7"},
    {"estacion": "Quartier Belvedere", "ciudad": "Viena", "lat": 48.1937, "lon": 16.3898, "linea": "S1 / S2 / S3"},
    {"estacion": "Aspern Nord", "ciudad": "Viena", "lat": 48.2436, "lon": 16.5094, "linea": "S1"},
    {"estacion": "Leopoldau", "ciudad": "Viena", "lat": 48.2625, "lon": 16.4147, "linea": "S1 / S2 / S3 / S4"},
    {"estacion": "Traisengasse", "ciudad": "Viena", "lat": 48.2358, "lon": 16.3826, "linea": "Stammstrecke"},
    {"estacion": "Kaiserebersdorf", "ciudad": "Viena", "lat": 48.146039, "lon": 16.465389, "linea": "S7"},
    {"estacion": "Matzleinsdorfer Platz", "ciudad": "Viena", "lat": 48.1801806, "lon": 16.3581194, "linea": "Stammstrecke"},
    {"estacion": "Ottakring", "ciudad": "Viena", "lat": 48.2117111, "lon": 16.3112111, "linea": "Vorortelinie"},
    {"estacion": "Heiligenstadt", "ciudad": "Viena", "lat": 48.248785, "lon": 16.365726, "linea": "S40 / S45"},
    {"estacion": "Strebersdorf", "ciudad": "Viena", "lat": 48.285669, "lon": 16.38147, "linea": "S3 / S4"},
    {"estacion": "Gersthof", "ciudad": "Viena", "lat": 48.23125, "lon": 16.329, "linea": "Vorortelinie"},
    {"estacion": "Nussdorf", "ciudad": "Viena", "lat": 48.25995, "lon": 16.36793, "linea": "Franz-Josefs-Bahn"},
    {"estacion": "Spittelau", "ciudad": "Viena", "lat": 48.2354, "lon": 16.3581889, "linea": "S40 / S45"},
    {"estacion": "Simmering", "ciudad": "Viena", "lat": 48.1701389, "lon": 16.41975, "linea": "Laaer Ostbahn"},
    {"estacion": "Speising", "ciudad": "Viena", "lat": 48.17345, "lon": 16.2842111, "linea": "Lainzer Tunnel"},
    {"estacion": "Franz-Josefs-Bahnhof", "ciudad": "Viena", "lat": 48.226867, "lon": 16.360852, "linea": "S40"},
]

CUSTOM_CSS = """
<style>
:root { --primary: #cc0000; }
.stApp { background-color: #ffffff; color: #000000; }
[data-testid="stHeader"] { background-color: var(--primary); }
[data-testid="stHeader"] h1 { color: white !important; margin: 0; padding: 6px 0; }
h1, h2, h3, h4, h5, h6 { color: #000000; }
div.stButton > button { background-color: var(--primary); color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 16px; }
button[key="btn_global_angry"], button[key="btn_global_neutral"], button[key="btn_global_happy"] { font-size: 52px !important; height: 76px; }
</style>
"""

EMOJI_UNKNOWN = "\U0001F610"  # neutral face
EMOJI_HAPPY = "\U0001F604"
EMOJI_GOOD = "\U0001F642"
EMOJI_BAD = "\U0001F621"

# --- Utilidades de datos ---
def normaliza_estacion(nombre: str) -> str:
    if pd.isna(nombre):
        return ""
    return re.sub(r"^wien\s+", "", str(nombre), flags=re.IGNORECASE).strip()


@st.cache_data
def cargar_opiniones() -> pd.DataFrame:
    if not FILE_OPINIONES.exists():
        return pd.DataFrame(columns=["fecha", "estacion", "texto", "satisfaccion"])
    df = pd.read_csv(FILE_OPINIONES, encoding="utf-8")
    if "satisfaccion" not in df.columns:
        df["satisfaccion"] = pd.NA
    return df


def guardar_opinion(fecha: str, estacion: str, texto: str, satisfaccion: int) -> None:
    df = cargar_opiniones()
    nueva = pd.DataFrame([
        {
            "fecha": fecha,
            "estacion": estacion,
            "texto": texto,
            "satisfaccion": satisfaccion,
        }
    ])
    df = pd.concat([df, nueva], ignore_index=True)
    df.to_csv(FILE_OPINIONES, index=False, encoding="utf-8")
    cargar_opiniones.clear()


def score_to_emoji_color(score):
    # pd.NA no soporta comparaciones booleanas; normalizamos con pd.isna
    if score is None or pd.isna(score):
        return EMOJI_UNKNOWN, [180, 180, 180, 180]
    if score >= 4:
        return EMOJI_HAPPY, [0, 200, 0, 200]
    if score >= 3:
        return EMOJI_GOOD, [230, 180, 0, 200]
    return EMOJI_BAD, [220, 0, 0, 200]


def estaciones_con_satisfaccion(opiniones: pd.DataFrame) -> pd.DataFrame:
    estaciones = pd.DataFrame(STATIONS_DATA).drop_duplicates("estacion")
    estaciones["estacion_norm"] = estaciones["estacion"].apply(normaliza_estacion)

    if not opiniones.empty and "satisfaccion" in opiniones.columns:
        opiniones_local = opiniones.copy()
        opiniones_local["estacion_norm"] = opiniones_local["estacion"].apply(normaliza_estacion)
        agg = (
            opiniones_local.dropna(subset=["satisfaccion"])
            .groupby("estacion_norm")["satisfaccion"]
            .mean()
            .reset_index(name="satisfaccion_media")
        )
        estaciones = estaciones.merge(agg, on="estacion_norm", how="left")
    else:
        estaciones["satisfaccion_media"] = pd.NA

    estaciones[["emoji", "color"]] = estaciones["satisfaccion_media"].apply(
        lambda x: pd.Series(score_to_emoji_color(x))
    )
    return estaciones.drop(columns=["estacion_norm"])


def nube_palabras(opiniones: pd.DataFrame, estacion: str, top_n: int = 15):
    """Regresa top_n palabras por frecuencia para una estaci?n."""
    if opiniones.empty:
        return []
    estacion_norm = normaliza_estacion(estacion)
    opiniones_local = opiniones.copy()
    opiniones_local["estacion_norm"] = opiniones_local["estacion"].apply(normaliza_estacion)
    textos = opiniones_local.loc[opiniones_local["estacion_norm"] == estacion_norm, "texto"].dropna()
    if textos.empty:
        return []
    stop = {
        "the", "and", "a", "de", "la", "el", "los", "las", "y", "en", "un", "una", "por",
        "con", "del", "que", "para", "muy", "esto", "eso", "esta", "ese", "esta", "esta",
        "esta", "was", "were", "is", "are", "very", "good", "bad", "ok"
    }
    counter = Counter()
    for t in textos:
        words = re.findall(r"[A-Za-z??????????????']{3,}", t)
        words = [w.lower() for w in words if w.lower() not in stop]
        counter.update(words)
    return counter.most_common(top_n)


def render_word_cloud(words_with_freq):
    """Renderiza una nube de palabras simple usando HTML y tamaños según frecuencia."""
    if not words_with_freq:
        return
    max_freq = max(freq for _, freq in words_with_freq) or 1
    palette = ["#CC0000", "#000000", "#444444", "#990000", "#555555"]
    random.shuffle(words_with_freq)
    spans = []
    for word, freq in words_with_freq:
        size = 16 + int((freq / max_freq) * 32)  # 16–48px
        color = random.choice(palette)
        spans.append(f'<span style="font-size:{size}px; color:{color}; margin:6px; line-height:1.2">{word}</span>')
    html = "<div style='display:flex; flex-wrap:wrap; gap:6px'>" + "".join(spans) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


# --- Vistas ---
def vista_mapa():
    st.title(f"{EMOJI_HAPPY} Train Station Map in Austria")
    st.write(
        "Visualize the satisfaction per station. Each emoji on the map reflects average sentiment."
    )

    opiniones_df = cargar_opiniones()
    estaciones_df = estaciones_con_satisfaccion(opiniones_df)

    st.subheader("\U0001F5FA\U0000FE0F Interactive Map")
    st.pydeck_chart(
        pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=48.2082, longitude=16.3738, zoom=10),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=estaciones_df,
                    get_position="[lon, lat]",
                    get_radius=400,
                    get_fill_color="color",
                    pickable=True,
                ),
                pdk.Layer(
                    "TextLayer",
                    data=estaciones_df,
                    get_position="[lon, lat]",
                    get_text="emoji",
                    get_color="[0,0,0,255]",
                    get_size=24,
                    size_units="pixels",
                    size_scale=1,
                    billboard=True,
                ),
            ],
            tooltip={"text": "{estacion}\n{emoji} {satisfaccion_media}"},
        )
    )

    st.subheader("\U0001F4CB Stations")
    seleccion_estacion = st.selectbox("Select a station", estaciones_df["estacion"])
    fila = estaciones_df[estaciones_df["estacion"] == seleccion_estacion].iloc[0]

    if not pd.isna(fila["satisfaccion_media"]):
        st.write(f"{fila['emoji']} Average satisfaction: {fila['satisfaccion_media']:.2f}")
    else:
        st.info("No satisfaction data yet for this station.")

    st.dataframe(
        estaciones_df[["estacion", "ciudad", "emoji", "satisfaccion_media"]],
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("\U0001F4AD Word cloud (top 15 terms)")
    top_words = nube_palabras(opiniones_df, seleccion_estacion, top_n=15)
    if not top_words:
        st.info("No text opinions for this station yet.")
    else:
        render_word_cloud(top_words)


def vista_encuesta():
    st.title("\U0001F4DD Station Experience Survey")
    st.write("Share your experience. Your input updates the map averages.")

    estaciones_df = pd.DataFrame(STATIONS_DATA)
    estacion = st.selectbox("Which station?", estaciones_df["estacion"])

    satisfaccion = st.slider("Overall experience", min_value=1, max_value=5, value=3)

    texto = st.text_area(
        "Describe what happened (delays, cleanliness, safety, comfort, etc.)",
        height=150,
        placeholder="Example: The train arrived 15 minutes late...",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit opinion"):
            if not texto.strip():
                st.warning("Please write a comment before submitting.")
            else:
                fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                try:
                    guardar_opinion(fecha, estacion, texto, satisfaccion)
                    st.success("Thanks! Your opinion was saved.")
                    st.rerun()
                except Exception as exc:  # rare: write errors
                    st.error(f"Could not save the opinion: {exc}")

    with col2:
        if st.button("Back to map"):
            st.session_state["page"] = "mapa"
            st.rerun()

    st.markdown("---")
    st.subheader("\U0001F5C2\U0000FE0F Recent opinions")
    opiniones_df = cargar_opiniones()
    if opiniones_df.empty:
        st.info("No opinions yet.")
    else:
        with pd.option_context("mode.copy_on_write", True):
            try:
                opiniones_df["fecha"] = pd.to_datetime(opiniones_df["fecha"])
                opiniones_df = opiniones_df.sort_values("fecha", ascending=False)
            except Exception:
                opiniones_df = opiniones_df
        st.dataframe(opiniones_df, use_container_width=True)


# --- Feedback rapido con emojis ---
def feedback_rapido():
    st.markdown("---")
    st.subheader("\U0001F60A Quick feedback")
    colA, colB, colC = st.columns(3)
    if colA.button(EMOJI_BAD, key="btn_global_angry"):
        st.session_state["emoji_mode"] = "angry"
    if colB.button(EMOJI_GOOD, key="btn_global_neutral"):
        st.session_state["emoji_mode"] = "neutral"
    if colC.button(EMOJI_HAPPY, key="btn_global_happy"):
        st.session_state["emoji_mode"] = "happy"

    if st.session_state.get("emoji_mode"):
        emoji = st.session_state["emoji_mode"]
        palabras = {
            "angry": ["Dirty", "Service", "Comfort", "Security", "Payment", "Information", "Cancelled",],
            "neutral": ["Acceptable", "Confusing", "Crowded", "Unfriendly", "Payment"],
            "happy": ["happy", "Comfortable", "Punctual", "Clean", "Safe"],
        }
        st.write(f"Select the words that match your {emoji} emotion:")
        seleccion = st.multiselect(
            "Words for your mood",
            palabras[emoji],
            key="global_multiselect",
        )

        if seleccion:
            st.subheader("\U0001F4AC Free comment")
            comentario_libre = st.text_area(
                "Add an optional comment",
                height=100,
                key="global_text_area",
            )
            if st.button("Submit quick feedback", key="btn_final_feedback"):
                st.session_state.setdefault("quick_feedback", []).append(
                    {
                        "emoji": emoji,
                        "palabras": seleccion,
                        "comentario": comentario_libre,
                    }
                )
                st.success("Quick feedback submitted.")
                st.info(
                    f"Emotion: **{emoji}**\nSelected words: **{', '.join(seleccion)}**\nComment: **{comentario_libre or 'No comment'}**"
                )
                st.session_state.pop("emoji_mode", None)


# --- Pizarron ---
def pizarron():
    st.markdown("---")
    st.subheader("\U0000270F\U0000FE0F Interactive whiteboard")
    st.write("Use this space to sketch or take notes about your experience.")
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=300,
        drawing_mode="freedraw",
        key="canvas_board",
    )
    if canvas_result.image_data is not None:
        st.info("Your drawing was captured (not stored). Add persistence as needed.")


# --- Router ---
if "page" not in st.session_state:
    st.session_state["page"] = "mapa"

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if st.session_state["page"] == "mapa":
    vista_mapa()
else:
    vista_encuesta()

feedback_rapido()
pizarron()

