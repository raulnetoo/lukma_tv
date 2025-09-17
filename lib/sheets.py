# lib/sheets.py
import json
import os
from functools import lru_cache
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

def _from_streamlit_secrets():
    """
    Lê credenciais do Streamlit Secrets.
    Aceita tanto:
      - gcp_service_account como STRING JSON (entre aspas triplas no TOML)
      - gcp_service_account como OBJETO (TOML -> dict)
    """
    try:
        import streamlit as st
        svc = st.secrets.get("gcp_service_account", None)
        sid = st.secrets.get("GOOGLE_SHEET_ID", None)
        if not svc or not sid:
            return None, None

        # Caso 1: já é dict (TOML como objeto)
        if isinstance(svc, dict):
            creds_json = svc
        else:
            # Caso 2: é string JSON (entre aspas triplas)
            try:
                creds_json = json.loads(svc)
            except Exception as e:
                # Erro de parse: retorna None para cair no .env OU levantar erro claro adiante
                return None, None
        return creds_json, sid
    except Exception:
        return None, None

def _from_env():
    json_path = os.getenv("GOOGLE_SA_JSON_PATH")
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    creds_json = None
    if json_path and os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            creds_json = json.load(f)
    return creds_json, sheet_id

@lru_cache(maxsize=1)
def get_client_and_sheet():
    """
    Tenta Secrets primeiro; se falhar, tenta .env.
    Se ainda faltar algo, explica exatamente o que está faltando.
    """
    creds_json, sheet_id = _from_streamlit_secrets()
    if creds_json is None or sheet_id is None:
        creds_json_env, sheet_id_env = _from_env()
        creds_json = creds_json or creds_json_env
        sheet_id = sheet_id or sheet_id_env

    missing = []
    if creds_json is None:
        missing.append("gcp_service_account (nos Secrets) ou GOOGLE_SA_JSON_PATH (no .env)")
    if sheet_id is None:
        missing.append("GOOGLE_SHEET_ID (Secrets ou .env)")

    if missing:
        raise RuntimeError(
            "Config faltando: " + ", ".join(missing) +
            ". No Streamlit Cloud use Settings→Secrets com chaves gcp_service_account e GOOGLE_SHEET_ID."
        )

    credentials = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(sheet_id)
    return client, sheet
