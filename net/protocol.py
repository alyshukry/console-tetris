import json

def encode(msg_type: str, data: dict | None = None) -> str:
    return json.dumps({"type": msg_type, **(data or {})})
