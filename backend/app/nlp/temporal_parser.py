import re
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any

MONTH_MAP = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}

def parse_temporal_expression(query: str, ref_date_str: str = "2026-09-10T23:59:59") -> Optional[Dict[str, Any]]:
    """
    Parses natural temporal expressions in user queries into start/end datetime ranges.
    Anchored against corpus reference date (e.g. 2026-09-10).
    """
    q_lower = query.lower()
    ref_dt = datetime.strptime(ref_date_str, "%Y-%m-%dT%H:%M:%S")

    # Yesterday
    if "yesterday" in q_lower:
        target_day = ref_dt - timedelta(days=1)
        start_dt = target_day.replace(hour=0, minute=0, second=0)
        end_dt = target_day.replace(hour=23, minute=59, second=59)
        return {
            "label": f"Yesterday ({target_day.strftime('%b %d, %Y')})",
            "start": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "exact_day": True
        }

    # Today
    if "today" in q_lower:
        start_dt = ref_dt.replace(hour=0, minute=0, second=0)
        end_dt = ref_dt.replace(hour=23, minute=59, second=59)
        return {
            "label": f"Today ({ref_dt.strftime('%b %d, %Y')})",
            "start": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "exact_day": True
        }

    # Last month (relative to reference date)
    if "last month" in q_lower:
        # If ref is September 2026, last month is August 2026
        target_month = ref_dt.month - 1
        target_year = ref_dt.year
        if target_month == 0:
            target_month = 12
            target_year -= 1
        start_dt = datetime(target_year, target_month, 1, 0, 0, 0)
        # End of August is 31
        end_dt = datetime(target_year, target_month, 31, 23, 59, 59) if target_month in [1,3,5,7,8,10,12] else datetime(target_year, target_month, 30, 23, 59, 59)
        return {
            "label": f"Last month (August {target_year})",
            "start": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "exact_day": False
        }

    # This month
    if "this month" in q_lower:
        start_dt = datetime(ref_dt.year, ref_dt.month, 1, 0, 0, 0)
        end_dt = ref_dt
        return {
            "label": f"This month (September {ref_dt.year})",
            "start": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "exact_day": False
        }

    # Exact date pattern like "july 14" or "14 july" or "september 18"
    day_match = re.search(r"\b(july|august|september|sept|june|may|april|march|february)\s+(\d{1,2})\b", q_lower)
    if day_match:
        m_str, d_str = day_match.group(1), day_match.group(2)
        month_num = MONTH_MAP[m_str]
        day_num = int(d_str)
        start_dt = datetime(2026, month_num, day_num, 0, 0, 0)
        end_dt = datetime(2026, month_num, day_num, 23, 59, 59)
        return {
            "label": f"{m_str.capitalize()} {day_num}, 2026",
            "start": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "exact_day": True
        }

    # "first week of [month]"
    first_week_match = re.search(r"\bfirst week of\s+([a-z]+)\b", q_lower)
    if first_week_match and first_week_match.group(1) in MONTH_MAP:
        m_num = MONTH_MAP[first_week_match.group(1)]
        start_dt = datetime(2026, m_num, 1, 0, 0, 0)
        end_dt = datetime(2026, m_num, 7, 23, 59, 59)
        return {
            "label": f"First week of {first_week_match.group(1).capitalize()} 2026",
            "start": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "exact_day": False
        }

    # "mid-[month]" or "mid [month]"
    mid_match = re.search(r"\bmid-?([a-z]+)\b", q_lower)
    if mid_match and mid_match.group(1) in MONTH_MAP:
        m_num = MONTH_MAP[mid_match.group(1)]
        start_dt = datetime(2026, m_num, 10, 0, 0, 0)
        end_dt = datetime(2026, m_num, 20, 23, 59, 59)
        return {
            "label": f"Mid-{mid_match.group(1).capitalize()} 2026",
            "start": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "exact_day": False
        }

    # "late [month]"
    late_match = re.search(r"\blate\s+([a-z]+)\b", q_lower)
    if late_match and late_match.group(1) in MONTH_MAP:
        m_num = MONTH_MAP[late_match.group(1)]
        start_dt = datetime(2026, m_num, 21, 0, 0, 0)
        end_day = 31 if m_num in [1,3,5,7,8,10,12] else 30
        end_dt = datetime(2026, m_num, end_day, 23, 59, 59)
        return {
            "label": f"Late {late_match.group(1).capitalize()} 2026",
            "start": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "exact_day": False
        }

    # Single Month mention: "in march", "during april", "in july"
    for m_name, m_num in MONTH_MAP.items():
        if re.search(rf"\b(in|during|around|of)\s+{m_name}\b", q_lower) or re.search(rf"\b{m_name}\b", q_lower):
            start_dt = datetime(2026, m_num, 1, 0, 0, 0)
            end_day = 31 if m_num in [1,3,5,7,8,10,12] else 30
            end_dt = datetime(2026, m_num, end_day, 23, 59, 59)
            return {
                "label": f"{m_name.capitalize()} 2026",
                "start": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                "end": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                "exact_day": False
            }

    return None

def compute_temporal_score(msg_timestamp: str, start_iso: str, end_iso: str) -> float:
    """Calculates proximity score (0.0 to 1.0) for a message timestamp given a date range."""
    try:
        msg_dt = datetime.strptime(msg_timestamp, "%Y-%m-%dT%H:%M:%S")
        start_dt = datetime.strptime(start_iso, "%Y-%m-%dT%H:%M:%S")
        end_dt = datetime.strptime(end_iso, "%Y-%m-%dT%H:%M:%S")

        # Inside target range
        if start_dt <= msg_dt <= end_dt:
            return 1.0

        # Proximity decay if outside range
        if msg_dt < start_dt:
            diff_days = (start_dt - msg_dt).total_seconds() / 86400.0
        else:
            diff_days = (msg_dt - end_dt).total_seconds() / 86400.0

        if diff_days <= 1.0:
            return 0.8
        elif diff_days <= 3.0:
            return 0.5
        elif diff_days <= 7.0:
            return 0.2
        return 0.0
    except Exception:
        return 0.0
