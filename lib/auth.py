import streamlit as st
import streamlit_authenticator as stauth
from .sheets import read_all, upsert_row

def _to_credentials_dict(users_rows):
    usernames = [r["username"] for r in users_rows if r.get("username")]
    names = [r.get("full_name") or r["username"] for r in users_rows if r.get("username")]
    pw_hashes = [r.get("password_hash","") for r in users_rows if r.get("username")]
    return {"usernames": {
        u: {"name": n, "password": p}
        for u, n, p in zip(usernames, names, pw_hashes)
    }}

def login():
    users = read_all("users")
    if not users:
        st.warning("Nenhum usuário cadastrado. Criando admin padrão: admin/admin")
        # senha hash de "admin"
        default_hash = stauth.Hasher(["admin"]).generate()[0]
        upsert_row("users","username",{
            "username":"admin","full_name":"Administrador","role":"admin",
            "password_hash":default_hash,
            "can_news":"1","can_videos":"1","can_birthdays":"1","can_weather":"1","can_fx":"1","can_clocks":"1"
        })
        users = read_all("users")

    creds = _to_credentials_dict(users)
    authenticator = stauth.Authenticate(
        credentials=creds,
        cookie_name="lukma_tv_auth",
        key="lukma_tv_auth_key",
        cookie_expiry_days=7,
    )
    name, auth_status, username = authenticator.login("Login", "main")
    if auth_status:
        st.session_state["current_user"] = next((u for u in users if u["username"]==username), None)
        return authenticator, name, username
    elif auth_status is False:
        st.error("Usuário/senha inválidos.")
    else:
        st.info("Informe suas credenciais para entrar.")
    return None, None, None

def has_permission(section: str) -> bool:
    user = st.session_state.get("current_user")
    if not user:
        return False
    if user.get("role") == "admin":
        return True
    flag = f"can_{section}"
    return str(user.get(flag,"0")) in ("1","true","True")

def is_admin() -> bool:
    user = st.session_state.get("current_user")
    return user and user.get("role") == "admin"
