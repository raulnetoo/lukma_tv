import json, time, requests, streamlit as st
from .sheets import read_all, upsert_row
from .utils import month_now_br, int_or_none

@st.cache_data(ttl=600)
def fetch_fx():
    # Fiat
    fx = {}
    r = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=BRL", timeout=10).json()
    fx["USD_BRL"] = r.get("rates",{}).get("BRL")
    r = requests.get("https://api.exchangerate.host/latest?base=EUR&symbols=BRL", timeout=10).json()
    fx["EUR_BRL"] = r.get("rates",{}).get("BRL")
    # Cripto
    cg = requests.get("https://api.coingecko.com/api/v3/simple/price",
                      params={"ids":"bitcoin,ethereum","vs_currencies":"brl"}, timeout=10).json()
    fx["BTC_BRL"] = cg.get("bitcoin",{}).get("brl")
    fx["ETH_BRL"] = cg.get("ethereum",{}).get("brl")
    return fx

@st.cache_data(ttl=1800)
def geocode_city(city: str):
    # Open-Meteo geocoding
    r = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                     params={"name":city,"count":1,"language":"pt","format":"json"}, timeout=10).json()
    if r.get("results"):
        a = r["results"][0]
        return a["latitude"], a["longitude"]
    return None, None

@st.cache_data(ttl=900)
def fetch_weather_for_city(city: str):
    lat, lon = geocode_city(city)
    if lat is None:
        return None
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": "temperature_2m,precipitation_probability",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }
    r = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=10).json()
    return r

def load_units_from_config():
    cfg = read_all("config")
    item = next((c for c in cfg if c.get("key")=="weather_units"), None)
    if item and item.get("value"):
        try:
            return json.loads(item["value"])
        except: pass
    # padrão (pedido)
    return [
        {"name":"Lukma RP","city":"São José do Rio Preto - SP"},
        {"name":"Lukma SP","city":"Guarulhos - SP"},
        {"name":"Lukma MG","city":"Betim - MG"},
        {"name":"Lukma PE","city":"Jaboatão dos Guararapes - PE"},
    ]

def list_news():
    rows = read_all("news")
    rows = [r for r in rows if str(r.get("active","1")) in ("1","true","True")]
    rows.sort(key=lambda r: int_or_none(r.get("order") or 0) or 0)
    return rows

def list_videos():
    rows = read_all("videos")
    rows = [r for r in rows if str(r.get("active","1")) in ("1","true","True")]
    rows.sort(key=lambda r: int_or_none(r.get("order") or 0) or 0)
    return rows

def list_birthdays_current_month():
    rows = read_all("birthdays")
    m = month_now_br()
    rows = [r for r in rows if int_or_none(r.get("month")) == m and str(r.get("active","1")) in ("1","true","True")]
    rows.sort(key=lambda r: int_or_none(r.get("day") or 1) or 1)
    return rows

def save_config_units(units: list[dict]):
    upsert_row("config","key",{"key":"weather_units","value":json.dumps(units, ensure_ascii=False)})
