from datetime import datetime

from fastapi.responses import HTMLResponse
from fastapi import Request

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, list):
        return [serialize_datetime(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: serialize_datetime(v) for k, v in obj.items()}
    return obj
