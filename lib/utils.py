from datetime import datetime
from zoneinfo import ZoneInfo

def now_in_tz(tzname: str) -> datetime:
    return datetime.now(ZoneInfo(tzname))

def month_now_br() -> int:
    return now_in_tz("America/Sao_Paulo").month

def wrap_index(i: int, n: int) -> int:
    if n == 0: return 0
    return i % n

def int_or_none(x):
    try: return int(x)
    except: return None

def boolish(x):
    return str(x).strip().lower() in ("1","true","yes","sim")
