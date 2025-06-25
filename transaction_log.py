import threading
from typing import List, Dict, Optional

# Thread-safe transaction log
_lock = threading.Lock()
_transactions: List[Dict] = []
_spend_cap: float = 100.0  # Default spend cap in USD

COSTS = {
    'weather': 0.01,   # $0.01 per weather query
    'travel': 0.05,     # $0.05 per travel query
    'payment': 0.10,    # $0.10 per payment
}

def log_transaction(tool: str, amount: float, meta: Optional[Dict] = None):
    global _transactions
    with _lock:
        _transactions.append({
            'tool': tool,
            'amount': amount,
            'meta': meta or {},
        })

def get_total_spend() -> float:
    with _lock:
        return sum(tx['amount'] for tx in _transactions)

def get_remaining_cap() -> float:
    with _lock:
        return _spend_cap - get_total_spend()

def get_transaction_history() -> List[Dict]:
    with _lock:
        return list(_transactions)

def set_spend_cap(cap: float):
    global _spend_cap
    with _lock:
        _spend_cap = cap

def get_spend_cap() -> float:
    with _lock:
        return _spend_cap 