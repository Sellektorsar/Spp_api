"""
Скрипт сбора тестовых данных с реального сервера.
Запуск: python scripts/collect_test_data.py
"""
import warnings
warnings.filterwarnings("ignore")
import requests
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

BASE    = os.getenv("SPP_API_URL", "https://spp-dev.smartpack.world")
USER    = os.getenv("SPP_API_USERNAME", "sasha")
PASS    = os.getenv("SPP_API_PASSWORD", "qwerty")
VERIFY  = os.getenv("SPP_API_VERIFY_SSL", "false").lower() not in ("false", "0", "no")

def sep(title):
    print(f"\n{'='*65}")
    print(f"  {title}")
    print('='*65)

# ── Авторизация ──────────────────────────────────────────────────────
r = requests.post(f"{BASE}/api/web/v1/auth",
                  data={"username": USER, "password": PASS},
                  verify=VERIFY, timeout=15)
r.raise_for_status()
token = r.json()["data"]["access_token"]
h = {"Authorization": f"Bearer {token}"}
print(f"[AUTH] OK — {BASE}")


# ── 1. Линии ─────────────────────────────────────────────────────────
sep("LINES (limit=100)")
r = requests.post(f"{BASE}/api/web/v1/line/filter",
                  json={"limit": 100, "offset": 0}, headers=h, verify=VERIFY)
data = r.json()
lines_all = data.get("data", [])
total = data.get("meta", {}).get("total_count", "?")
print(f"total={total}")
lines_with_number = [l for l in lines_all if l.get("number")]
print(f"lines with number={len(lines_with_number)}")
for l in lines_with_number[:20]:
    print(f"  number={l.get('number'):>6}  id={l.get('id')}  "
          f"pg={l.get('product_group'):<12}  type={l.get('line_type')}  "
          f"active={l.get('active')}  name={repr(str(l.get('name',''))[:25])}")

# Группируем по product_group
pg_lines = {}
for l in lines_with_number:
    pg = l.get("product_group", "?")
    pg_lines.setdefault(pg, []).append(l.get("number"))
print("\n  По group:")
for pg, nums in sorted(pg_lines.items()):
    print(f"    {pg:<12}: lines {nums[:5]}")


# ── 2. Рабочие смены ─────────────────────────────────────────────────
sep("WORK SHIFTS (limit=30)")
r = requests.post(f"{BASE}/api/web/v1/work_shift/filter",
                  json={"limit": 30, "offset": 0}, headers=h, verify=VERIFY)
data = r.json()
shifts = data.get("data", [])
total = data.get("meta", {}).get("total_count", "?")
print(f"total={total}")
active_shifts = [s for s in shifts if s.get("is_active")]
finished_shifts = [s for s in shifts if not s.get("is_active")]
print(f"active={len(active_shifts)}  finished={len(finished_shifts)}")
for s in shifts[:15]:
    mark = "ACTIVE" if s.get("is_active") else "done"
    print(f"  [{mark:6}] id={s.get('id')}  line={s.get('line_number'):>7}  "
          f"pg={s.get('product_group'):<12}  date={str(s.get('start_date',''))[:10]}")


# ── 3. GTIN по группам товаров ───────────────────────────────────────
sep("GTINS by product_group (limit=5 each)")
all_gtins = {}
for pg in ["milk", "water", "shoes", "antiseptic", "bio", "lp", "perfumery"]:
    r2 = requests.post(f"{BASE}/api/web/v1/gtin/filter",
                       json={"limit": 5, "offset": 0, "product_group": pg},
                       headers=h, verify=VERIFY)
    rows = r2.json().get("data", [])
    total2 = r2.json().get("meta", {}).get("total_count", 0)
    all_gtins[pg] = rows
    if rows:
        g = rows[0]
        print(f"  [{pg:<12}] total={total2:>3}  "
              f"gtin={g.get('gtin')}  name={repr(str(g.get('good_name',''))[:40])}")


# ── 4. Устройства ────────────────────────────────────────────────────
sep("DEVICES (limit=50)")
r = requests.post(f"{BASE}/api/web/v1/devices/filter",
                  json={"limit": 50, "offset": 0}, headers=h, verify=VERIFY)
data = r.json()
devices = data.get("data", [])
total = data.get("meta", {}).get("total_count", "?")
print(f"total={total}")
for dv in devices[:15]:
    print(f"  device_id={dv.get('device_id')}  "
          f"type={dv.get('type')}  mob_id={dv.get('mob_device_id')}  "
          f"name={repr(str(dv.get('name',''))[:25])}")


# ── 5. Принтеры ──────────────────────────────────────────────────────
sep("PRINTERS / LAYOUTS (limit=20)")
r = requests.post(f"{BASE}/api/web/v1/printer/layout/filter",
                  json={"limit": 20, "offset": 0}, headers=h, verify=VERIFY)
data = r.json()
printers = data.get("data", [])
total = data.get("meta", {}).get("total_count", "?")
print(f"total={total}")
for p in printers[:10]:
    print(f"  layout_id={p.get('layout_id')}  "
          f"fav={p.get('is_favorite')}  type={p.get('print_type')}  "
          f"name={repr(str(p.get('name',''))[:45])}")


# ── 6. Отчёты по статусам ────────────────────────────────────────────
sep("REPORTS by status")
status_map = {0: "new", 100: "processing", 102: "sent", 103: "error", 104: "pending"}
report_ids = {}
for code, name in status_map.items():
    r2 = requests.post(f"{BASE}/api/web/v1/report/filter",
                       json={"limit": 3, "offset": 0, "status": code},
                       headers=h, verify=VERIFY)
    rows = r2.json().get("data", [])
    total2 = r2.json().get("meta", {}).get("total_count", 0)
    if rows:
        rp = rows[0]
        report_ids[name] = rp.get("id", "")
        print(f"  [status={code:>3}/{name:<10}] total={total2:>3}  "
              f"id={rp.get('id')}  type={rp.get('type')}")
    else:
        print(f"  [status={code:>3}/{name:<10}] total=0")


# ── 7. Агрегационные сессии — raw ключи ──────────────────────────────
sep("AGGREGATION SESSIONS — raw structure (limit=10)")
r = requests.post(f"{BASE}/api/web/v1/aggregation_session/pallets/filter",
                  json={"limit": 10, "offset": 0}, headers=h, verify=VERIFY)
data = r.json()
sessions = data.get("data", [])
total = data.get("meta", {}).get("total_count", "?")
print(f"total={total}")
if sessions:
    print(f"  Keys: {list(sessions[0].keys())}")
    for s in sessions[:8]:
        # Ищем поля похожие на id
        id_candidates = {k: v for k, v in s.items()
                         if ("id" in k.lower() or "session" in k.lower()) and v}
        print(f"  line={s.get('line_number')}  id_candidates={id_candidates}  status={s.get('status')}")
else:
    print("  (нет данных)")


# ── 8. Заказы ────────────────────────────────────────────────────────
sep("ORDERS (approvable + form-data)")
r = requests.post(f"{BASE}/api/network_proxy/api/network/v1/orders/approvable",
                  json={"limit": 10, "offset": 0}, headers=h, verify=VERIFY)
print(f"  approvable status={r.status_code}")
try:
    d2 = r.json()
    inner = d2.get("data", {})
    orders = inner.get("orders", inner) if isinstance(inner, dict) else inner
    if isinstance(orders, list):
        for o in orders[:5]:
            print(f"    id={o.get('id')}  status={o.get('status')}  "
                  f"gtin={o.get('gtin')}  qty={o.get('quantity')}")
    else:
        print(f"    data type: {type(inner)}, keys: {list(inner.keys()) if isinstance(inner,dict) else '?'}")
except Exception as e:
    print(f"    err: {e}")

# Form data
r = requests.get(f"{BASE}/api/network_proxy/api/network/v1/orders/form-data",
                 headers=h, verify=VERIFY)
print(f"\n  form-data status={r.status_code}")
try:
    fd = r.json().get("data", {})
    sp = fd.get("service_providers", fd.get("serviceProviders", []))
    if isinstance(sp, list) and sp:
        print(f"  serviceProviders[0]: id={sp[0].get('id')}  name={repr(str(sp[0].get('name',''))[:40])}")
except Exception as e:
    print(f"    err: {e}")


# ── 9. Contract areas ─────────────────────────────────────────────────
sep("CONTRACT AREAS")
r = requests.get(f"{BASE}/api/network_proxy/api/network/v1/codes-transfer/contract-areas",
                 headers=h, verify=VERIFY)
print(f"  status={r.status_code}")
try:
    areas_raw = r.json()
    areas = areas_raw.get("data", areas_raw)
    lst = areas if isinstance(areas, list) else []
    print(f"  total={len(lst)}")
    for a in lst[:5]:
        print(f"    id={a.get('id')}  name={repr(str(a.get('name',''))[:40])}")
except Exception as e:
    print(f"    err: {e}  raw={r.text[:200]}")


# ── ИТОГ: рекомендуемые значения .env ────────────────────────────────
sep("РЕКОМЕНДУЕМЫЕ ПАРАМЕТРЫ ДЛЯ .env")

# Выбираем линии по product_group
best_lines = {}
for l in lines_with_number:
    pg = l.get("product_group")
    if pg and pg not in best_lines:
        best_lines[pg] = l.get("number")
for pg, num in sorted(best_lines.items()):
    print(f"  SPP_TEST_LINE_{pg.upper()}={num}")

# GTIN
for pg, rows in all_gtins.items():
    if rows:
        print(f"  SPP_TEST_GTIN_{pg.upper()}={rows[0].get('gtin')}")

# Смены
if active_shifts:
    s = active_shifts[0]
    print(f"  SPP_TEST_SHIFT_ID={s.get('id')}  # line={s.get('line_number')} active")
if finished_shifts:
    s = finished_shifts[0]
    print(f"  SPP_TEST_SHIFT_ID_FINISHED={s.get('id')}  # line={s.get('line_number')} finished")

# Устройства
if devices:
    # первое НЕ тестовое (без "test-device" в mob_id)
    real_dev = next((d for d in devices if not str(d.get("mob_device_id","")).startswith("test-")), devices[0])
    print(f"  SPP_TEST_DEVICE_ID={real_dev.get('device_id')}")
    print(f"  SPP_TEST_MOB_DEVICE_ID={real_dev.get('mob_device_id')}")

# Принтеры
if printers:
    print(f"  SPP_TEST_PRINTER_ID={printers[0].get('layout_id')}")

# Отчёты
for name, rid in report_ids.items():
    if rid:
        print(f"  SPP_TEST_REPORT_ID_{name.upper()}={rid}")
