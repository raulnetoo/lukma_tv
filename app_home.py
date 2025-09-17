import time
import streamlit as st
from lib.services import (fetch_fx, fetch_weather_for_city, load_units_from_config,
                          list_news, list_videos, list_birthdays_current_month)
from lib.utils import wrap_index, now_in_tz

st.set_page_config(page_title="Lukma TV", layout="wide")

# ---------- Estilos (paleta: azuis, brancos, cinzas, pretos)
st.markdown("""
<style>
:root { --primary:#0A67B1; --dark:#0A0A0A; --light:#ffffff; --muted:#f3f4f6; --gray:#111827; }
.block-container{ padding-top: 1rem; padding-bottom: 0.5rem; }
.card{ background:var(--light); border-radius:16px; padding:16px; box-shadow:0 8px 20px rgba(0,0,0,0.06); }
.h1{ font-size:2rem; font-weight:700; color:var(--gray); margin:0 0 .5rem 0;}
.h2{ font-size:1.2rem; font-weight:600; color:#1f2937; margin:.2rem 0 .6rem;}
.news-img{ width:100%; height:38vh; object-fit:cover; border-radius:12px; }
.ticker-wrap{ overflow:hidden; white-space:nowrap; }
.ticker{ display:inline-block; padding-left:100%; animation: marquee 25s linear infinite; }
.ticker-item{ display:inline-block; margin-right:48px; background:#e5f2fb; padding:8px 12px; border-radius:999px; }
@keyframes marquee { 0%{transform: translate(0,0);} 100%{transform: translate(-100%,0);} }
.fx-badge{ display:inline-block; padding:6px 12px; border-radius:999px; background:#0a67b111; margin:4px; }
.clock{ font-size:1.6rem; font-weight:700; }
.small{ color:#6b7280; font-size:.9rem; }
</style>
""", unsafe_allow_html=True)

# ---------- Data
news = list_news()
videos = list_videos()
birthdays = list_birthdays_current_month()
units = load_units_from_config()
fx = fetch_fx()

# ---------- Session indices (auto carrossel)
st.session_state.setdefault("news_idx", 0)
st.session_state.setdefault("bday_idx", 0)
st.session_state.setdefault("video_idx", 0)

# Avanço automático
st_autorefresh_news = st.experimental_rerun  # alias mental
st_autorefresh_interval_ms = 1000  # menor intervalo; fazemos contagem abaixo

# Timer simples por sessão para controlar avanços
now = time.time()
st.session_state.setdefault("_t_news", now)
st.session_state.setdefault("_t_bday", now)
st.session_state.setdefault("_t_video", now)

def maybe_advance(key, every_s, size, idx_key):
    if size <= 1: return
    if time.time() - st.session_state[key] >= every_s:
        st.session_state[idx_key] = wrap_index(st.session_state[idx_key] + 1, size)
        st.session_state[key] = time.time()
        st.experimental_rerun()

# define períodos
NEWS_PERIOD = 10
BDAY_PERIOD = 6
# para vídeos usamos duration no admin; fallback 15s
VIDEO_PERIOD = 15
if videos:
    try:
        dur = int(videos[st.session_state["video_idx"]].get("duration_seconds") or 0)
        if dur > 0: VIDEO_PERIOD = min(max(dur,5), 600)
    except: pass

# Avanços
maybe_advance("_t_news", NEWS_PERIOD, len(news), "news_idx")
maybe_advance("_t_bday", BDAY_PERIOD, len(birthdays), "bday_idx")
maybe_advance("_t_video", VIDEO_PERIOD, len(videos), "video_idx")

# ---------- GRID
col1, col2 = st.columns([2,1], gap="large")

with col1:
    # Notícias (card grande)
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="h1" aria-label="Notícias da empresa">Notícias</div>', unsafe_allow_html=True)
        if news:
            ix = st.session_state["news_idx"]
            n = news[ix]
            st.image(n.get("image_url",""), use_column_width=True, caption=n.get("title",""), output_format="auto")
            st.write(n.get("description",""))
            st.caption(f"{ix+1}/{len(news)} — troca automática a cada {NEWS_PERIOD}s")
        else:
            st.info("Sem notícias cadastradas.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Vídeos (abaixo)
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="h1" aria-label="Vídeos institucionais">Vídeos institucionais</div>', unsafe_allow_html=True)
        if videos:
            vx = st.session_state["video_idx"]
            v = videos[vx]
            st.video(v.get("url",""))
            st.caption(f"{vx+1}/{len(videos)} — avança automático (duração configurada).")
        else:
            st.info("Sem vídeos cadastrados.")
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Relógios + Moedas
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="h1">Relógios & Moedas</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="h2">Horários</div>', unsafe_allow_html=True)
            br = now_in_tz("America/Sao_Paulo")
            ny = now_in_tz("America/New_York")
            hk = now_in_tz("Asia/Hong_Kong")
            st.write(f"🇧🇷 Brasília")
            st.markdown(f'<div class="clock">{br:%H:%M:%S}</div><div class="small">{br:%d/%m/%Y}</div>', unsafe_allow_html=True)
            st.write(f"🇺🇸 EUA (NY)")
            st.markdown(f'<div class="clock">{ny:%H:%M:%S}</div><div class="small">{ny:%d/%m/%Y}</div>', unsafe_allow_html=True)
            st.write(f"🇭🇰 Hong Kong")
            st.markdown(f'<div class="clock">{hk:%H:%M:%S}</div><div class="small">{hk:%d/%m/%Y}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="h2">Cotações</div>', unsafe_allow_html=True)
            if fx:
                st.markdown(f'<span class="fx-badge">USD → R$ {fx.get("USD_BRL"):.2f}</span>', unsafe_allow_html=True)
                st.markdown(f'<span class="fx-badge">EUR → R$ {fx.get("EUR_BRL"):.2f}</span>', unsafe_allow_html=True)
                st.markdown(f'<span class="fx-badge">BTC → R$ {fx.get("BTC_BRL"):,.0f}</span>', unsafe_allow_html=True)
                st.markdown(f'<span class="fx-badge">ETH → R$ {fx.get("ETH_BRL"):,.0f}</span>', unsafe_allow_html=True)
            else:
                st.info("Sem dados de câmbio.")

        st.markdown('</div>', unsafe_allow_html=True)

    # Aniversariantes
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="h1">Aniversariantes do mês 🎉</div>', unsafe_allow_html=True)
        if birthdays:
            bx = st.session_state["bday_idx"]
            b = birthdays[bx]
            cols = st.columns([1,2])
            with cols[0]:
                if b.get("photo_url"): st.image(b["photo_url"], caption=b["name"], use_column_width=True)
                else: st.image("https://media.giphy.com/media/3o6ZsXSgX9eS5aB8Uo/giphy.gif", caption=b["name"], use_column_width=True)
            with cols[1]:
                st.subheader(b.get("name",""))
                st.write(f"Setor: **{b.get('department','')}**")
                st.write(f"Dia: **{b.get('day')}/{b.get('month')}**")
                st.balloons()
                st.caption(f"{bx+1}/{len(birthdays)} — troca automática a cada 6s")
        else:
            st.info("Sem aniversariantes cadastrados para este mês.")
        st.markdown('</div>', unsafe_allow_html=True)

# Ticker clima (barra inteira)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="h2">Previsão do tempo</div>', unsafe_allow_html=True)
if units:
    items = []
    for u in units:
        data = fetch_weather_for_city(u["city"])
        if not data: continue
        d = data.get("daily", {})
        tmax = d.get("temperature_2m_max",[None])[0]
        tmin = d.get("temperature_2m_min",[None])[0]
        rain = d.get("precipitation_sum",[None])[0]
        items.append(f'<span class="ticker-item"><b>{u["name"]}</b> ({u["city"]}): '
                     f'Max {tmax}°C | Min {tmin}°C | Chuva {rain}mm</span>')
    if items:
        st.markdown('<div class="ticker-wrap"><div class="ticker">' + "".join(items) + '</div></div>', unsafe_allow_html=True)
    else:
        st.info("Sem dados de clima.")
else:
    st.info("Sem unidades configuradas.")
st.markdown('</div>', unsafe_allow_html=True)

# Atualização constante para relógios/auto-carrossel
st.experimental_singleton.clear()  # reduz chance de cache travar timers
time.sleep(0.2)
st.experimental_rerun()
