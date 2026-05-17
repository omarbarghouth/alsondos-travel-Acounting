"""
database.py — JSON flat-file storage layer.
Production-ready interface: replace body of each function with
PostgreSQL calls in Phase 2 without changing any route code.
"""
import json, os, uuid
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

COLLECTIONS = [
    'transactions', 'suppliers', 'companies', 'customers',
    'hotels', 'tours', 'transfers', 'payments', 'vouchers', 'invoices'
]

# ── Internal helpers ─────────────────────────────────────────

def _path(name):
    return os.path.join(DATA_DIR, f'{name}.json')

def _init():
    """Ensure every collection file exists and is empty on first run."""
    os.makedirs(DATA_DIR, exist_ok=True)
    for col in COLLECTIONS:
        p = _path(col)
        if not os.path.exists(p):
            with open(p, 'w') as f:
                json.dump([], f)

def _read(col: str) -> list:
    try:
        with open(_path(col)) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def _write(col: str, data: list):
    with open(_path(col), 'w') as f:
        json.dump(data, f, indent=2, default=str)

# ── Public API ───────────────────────────────────────────────

def get_all(col: str) -> list:
    return _read(col)

def get_by_id(col: str, id_: str):
    return next((r for r in _read(col) if str(r.get('id')) == str(id_)), None)

def insert(col: str, record: dict) -> dict:
    data = _read(col)
    record['id']         = str(uuid.uuid4())
    record['created_at'] = datetime.now().isoformat()
    record['updated_at'] = datetime.now().isoformat()
    data.append(record)
    _write(col, data)
    return record

def update(col: str, id_: str, updates: dict) -> dict | None:
    data = _read(col)
    for i, r in enumerate(data):
        if str(r.get('id')) == str(id_):
            data[i].update(updates)
            data[i]['updated_at'] = datetime.now().isoformat()
            _write(col, data)
            return data[i]
    return None

def delete(col: str, id_: str) -> bool:
    data   = _read(col)
    fresh  = [r for r in data if str(r.get('id')) != str(id_)]
    changed = len(fresh) < len(data)
    if changed:
        _write(col, fresh)
    return changed

def next_number(col: str, prefix: str, pad: int = 4) -> str:
    """Return the next sequential ref e.g. TXN-0001."""
    nums = []
    for r in _read(col):
        ref = r.get('ref_number') or r.get('voucher_number') or r.get('invoice_number') or ''
        if ref.startswith(prefix + '-'):
            try:
                nums.append(int(ref.split('-', 1)[1]))
            except (IndexError, ValueError):
                pass
    n = (max(nums) + 1) if nums else 1
    return f"{prefix}-{str(n).zfill(pad)}"

def search(col: str, query: str, fields: list) -> list:
    q = query.lower().strip()
    if not q:
        return _read(col)
    results = []
    for r in _read(col):
        for f in fields:
            if q in str(r.get(f, '')).lower():
                results.append(r)
                break
    return results

# Initialise on import — creates empty JSON files if missing
_init()
