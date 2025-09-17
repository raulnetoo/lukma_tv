import json
import os
from functools import lru_cache
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

def _from_streamlit_secrets():
    try:
        import streamlit as st
        svc = st.secrets.get("gcp_service_account", None)
        sid = st.secrets.get("GOOGLE_SHEET_ID", None)
        if svc and sid:
            return json.loads(svc), sid
    except Exception:
        pass
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
    creds_json, sheet_id = _from_streamlit_secrets()
    if creds_json is None or sheet_id is None:
        creds_json, sheet_id = _from_env()
    if creds_json is None or sheet_id is None:
        raise RuntimeError("Credenciais/GOOGLE_SHEET_ID não configurados.")

    credentials = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(sheet_id)
    return client, sheet

def get_ws(name: str, headers: list[str] | None = None):
    _, sheet = get_client_and_sheet()
    try:
        ws = sheet.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = sheet.add_worksheet(title=name, rows=1000, cols=20)
        if headers:
            ws.append_row(headers)
    return ws

def read_all(name: str) -> list[dict]:
    ws = get_ws(name)
    rows = ws.get_all_records()
    return rows

def upsert_row(name: str, key_field: str, data: dict):
    ws = get_ws(name)
    records = ws.get_all_records()
    headers = ws.row_values(1)
    if key_field not in headers:
        raise ValueError(f"Campo-chave {key_field} não existe em {name}.")

    # acha linha (2-based index por causa do header na linha 1)
    for idx, rec in enumerate(records, start=2):
        if str(rec.get(key_field)) == str(data.get(key_field)):
            # update
            row_values = [data.get(h, "") for h in headers]
            ws.update(f"A{idx}:{chr(64+len(headers))}{idx}", [row_values])
            return

    # insert
    # garante headers
    if not headers:
        headers = list(data.keys())
        ws.append_row(headers)
    row_values = [data.get(h, "") for h in headers]
    ws.append_row(row_values)

def delete_row(name: str, key_field: str, key_value: str | int):
    ws = get_ws(name)
    records = ws.get_all_records()
    headers = ws.row_values(1)
    key_idx = headers.index(key_field) + 1
    for idx, rec in enumerate(records, start=2):
        if str(rec.get(key_field)) == str(key_value):
            ws.delete_rows(idx)
            return True
    return False

def ensure_seed():
    # cria abas e cabeçalhos se faltarem
    get_ws("news", ["id","title","description","image_url","active","order"])
    get_ws("videos", ["id","title","url","duration_seconds","active","order"])
    get_ws("birthdays", ["id","name","department","day","month","photo_url","active"])
    get_ws("users", ["username","full_name","role","password_hash",
                     "can_news","can_videos","can_birthdays","can_weather","can_fx","can_clocks"])
    get_ws("config", ["key","value"])
