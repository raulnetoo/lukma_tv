import streamlit as st
from lib.auth import login, has_permission, is_admin
from lib.sheets import read_all, upsert_row, delete_row
from lib.services import load_units_from_config, save_config_units
import streamlit_authenticator as stauth

st.set_page_config(page_title="Admin - Lukma TV", layout="wide")

authenticator, name, username = login()
if not authenticator:
    st.stop()

st.sidebar.success(f"Logado como {name}")
if st.button("Sair"):
    authenticator.logout("Logout", "main")
    st.stop()

st.title("Administração")

# --- GUI helpers
def text_input_row(fields, sheet, key_field="id", defaults=None):
    defaults = defaults or {}
    with st.form(key=f"form_{sheet}"):
        values = {}
        cols = st.columns(len(fields))
        for (i, (label, k)) in enumerate(fields):
            with cols[i]:
                values[k] = st.text_input(label, value=str(defaults.get(k,"")))
        submitted = st.form_submit_button("Salvar")
        if submitted:
            if not values.get(key_field):
                st.error(f"{key_field} é obrigatório.")
            else:
                upsert_row(sheet, key_field, values)
                st.success("Salvo.")
                st.experimental_rerun()

def list_and_delete(sheet, key_field="id"):
    rows = read_all(sheet)
    st.dataframe(rows, use_container_width=True)
    did = st.text_input("ID para deletar", "")
    if st.button("Deletar"):
        if delete_row(sheet, key_field, did):
            st.success("Apagado.")
            st.experimental_rerun()
        else:
            st.error("ID não encontrado.")

tabs = st.tabs(["Notícias","Vídeos","Aniversariantes","Clima","Relógios","Moedas","Usuários"])

with tabs[0]:
    if not has_permission("news"):
        st.warning("Sem permissão para Notícias.")
    else:
        st.header("Notícias")
        text_input_row(
            [("ID","id"),("Título","title"),("Descrição","description"),
             ("URL Imagem","image_url"),("Ativo (1/0)","active"),("Ordem","order")],
            "news", "id"
        )
        list_and_delete("news","id")

with tabs[1]:
    if not has_permission("videos"):
        st.warning("Sem permissão para Vídeos.")
    else:
        st.header("Vídeos")
        text_input_row(
            [("ID","id"),("Título","title"),("URL vídeo (YouTube ou MP4)","url"),
             ("Duração (s)","duration_seconds"),("Ativo (1/0)","active"),("Ordem","order")],
            "videos", "id"
        )
        list_and_delete("videos","id")

with tabs[2]:
    if not has_permission("birthdays"):
        st.warning("Sem permissão para Aniversariantes.")
    else:
        st.header("Aniversariantes")
        text_input_row(
            [("ID","id"),("Nome","name"),("Setor","department"),
             ("Dia","day"),("Mês","month"),("Foto URL","photo_url"),("Ativo (1/0)","active")],
            "birthdays","id"
        )
        list_and_delete("birthdays","id")

with tabs[3]:
    if not has_permission("weather"):
        st.warning("Sem permissão para Clima.")
    else:
        st.header("Unidades de Clima")
        units = load_units_from_config()
        st.write("Formato: Nome da unidade + Cidade/UF/Localidade (como você quer mostrar).")
        for i, u in enumerate(units):
            cols = st.columns(2)
            u["name"] = cols[0].text_input(f"Nome unidade {i+1}", u["name"])
            u["city"] = cols[1].text_input(f"Cidade/UF {i+1}", u["city"])
        if st.button("Salvar unidades"):
            save_config_units(units)
            st.success("Unidades salvas.")

with tabs[4]:
    if not has_permission("clocks"):
        st.warning("Sem permissão para Relógios.")
    else:
        st.header("Relógios")
        st.info("Os relógios padrão são: Brasília, EUA (NY), Hong Kong. Ajuste no código se quiser mais.")

with tabs[5]:
    if not has_permission("fx"):
        st.warning("Sem permissão para Moedas.")
    else:
        st.header("Moedas")
        st.info("Cotações automáticas: USD/BRL, EUR/BRL (exchangerate.host) e BTC/BRL, ETH/BRL (CoinGecko).")

with tabs[6]:
    if not is_admin():
        st.warning("Somente admin pode gerenciar usuários.")
    else:
        st.header("Usuários")
        st.dataframe(read_all("users"), use_container_width=True)
        st.subheader("Criar/Atualizar")
        with st.form("user_form"):
            username_new = st.text_input("username")
            full_name = st.text_input("Nome")
            role = st.selectbox("Papel", ["admin","editor"])
            password = st.text_input("Senha (deixe vazio para não alterar)", type="password")
            c1,c2,c3 = st.columns(3)
            with c1:
                can_news = st.checkbox("Pode Notícias", True)
                can_videos = st.checkbox("Pode Vídeos", True)
            with c2:
                can_birthdays = st.checkbox("Pode Aniversários", True)
                can_weather = st.checkbox("Pode Clima", True)
            with c3:
                can_fx = st.checkbox("Pode Moedas", True)
                can_clocks = st.checkbox("Pode Relógios", True)
            submitted = st.form_submit_button("Salvar usuário")
            if submitted:
                if not username_new:
                    st.error("username é obrigatório.")
                else:
                    pwd_hash = None
                    if password:
                        pwd_hash = stauth.Hasher([password]).generate()[0]
                    row = {
                        "username": username_new,
                        "full_name": full_name,
                        "role": role,
                        "can_news": "1" if can_news else "0",
                        "can_videos": "1" if can_videos else "0",
                        "can_birthdays": "1" if can_birthdays else "0",
                        "can_weather": "1" if can_weather else "0",
                        "can_fx": "1" if can_fx else "0",
                        "can_clocks": "1" if can_clocks else "0",
                    }
                    if pwd_hash:
                        row["password_hash"] = pwd_hash
                    upsert_row("users","username",row)
                    st.success("Usuário salvo.")
                    st.experimental_rerun()
