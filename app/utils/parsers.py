from typing import Any
import re

def parse_price_string(v: Any) -> float:
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    if not isinstance(v, str):
        return 0.0
    
    s = v.strip().upper()
    if not s:
        return 0.0
    
    # Handle multipliers
    multipliers = {
        'CR': 10000000,
        'CRORE': 10000000,
        'L': 100000,
        'LACH': 100000,
        'LAKH': 100000,
        'LAC': 100000,
        'K': 1000,
        'THOUSAND': 1000
    }
    
    # Extract number and suffix (first part that looks like a number and second part that looks like a word)
    match = re.search(r"([\d.]+)\s*([A-Z]*)", s)
    if match:
        num_part = match.group(1)
        suffix_part = match.group(2)
        
        try:
            val = float(num_part)
            if suffix_part in multipliers:
                val *= multipliers[suffix_part]
            return val
        except ValueError:
            return 0.0
    
    return 0.0
