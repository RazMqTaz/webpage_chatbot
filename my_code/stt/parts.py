from typing import Optional, Dict, Any

# This function will send these parts to frontend
def make_part(
        text: str,
        is_final: bool
) -> Dict[str, Any]:
    return {
        "text": text,
        "is_final": is_final,
    }