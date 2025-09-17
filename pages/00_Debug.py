import streamlit as st
st.title("Debug de Secrets")

# O objetivo é apenas ver se o app enxerga as chaves, sem imprimir segredos sensíveis
have_sa = "gcp_service_account" in st.secrets and bool(st.secrets["gcp_service_account"])
have_id = "GOOGLE_SHEET_ID" in st.secrets and bool(st.secrets["GOOGLE_SHEET_ID"])

st.write("gcp_service_account presente? ", "✅" if have_sa else "❌")
st.write("GOOGLE_SHEET_ID presente? ", "✅" if have_id else "❌")

if have_id:
    st.write("GOOGLE_SHEET_ID (parcial): ", str(st.secrets["GOOGLE_SHEET_ID"])[:6] + "…")
st.info("Se algum item estiver ❌, volte em Settings → Secrets e corrija o nome/valor.")
