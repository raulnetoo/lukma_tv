import streamlit as st
from lib.sheets import get_client_and_sheet, get_ws, ensure_seed
import gspread
from google.auth.exceptions import GoogleAuthError

st.title("Healthcheck: Google Sheets")

ok = True
msgs = []

# 1) Ler secrets (já fizemos no 00_Debug, aqui só seguimos)
try:
    # 2) Tenta autenticar e abrir a planilha
    client, sheet = get_client_and_sheet()
    st.success(f"✅ Autenticado e abriu a planilha: {sheet.title}")
except Exception as e:
    ok = False
    st.error("❌ Falha ao autenticar/abrir planilha.")
    st.caption("Possíveis causas: Secrets com JSON inválido, GOOGLE_SHEET_ID errado, "
               "planilha não compartilhada com a Service Account, ou APIs não habilitadas.")
    st.code(repr(e))
    st.stop()

# 3) Tenta criar/abrir as abas obrigatórias (seed)
try:
    ensure_seed()  # cria as abas se faltarem
    ws_names = [ws.title for ws in sheet.worksheets()]
    st.write("Abas existentes:", ws_names)
    st.success("✅ Seed OK (abas garantidas).")
except gspread.exceptions.APIError as ge:
    ok = False
    st.error("❌ Falha de permissão ao criar/abrir abas.")
    st.caption("Verifique se a Service Account tem acesso como **Editor**.")
    st.code(repr(ge))
except Exception as e:
    ok = False
    st.error("❌ Erro inesperado ao criar/abrir abas.")
    st.code(repr(e))

if ok:
    st.info("Tudo certo! Agora a página Admin deve funcionar normalmente.")
