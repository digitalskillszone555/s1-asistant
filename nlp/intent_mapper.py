def map_intent_from_text(text: str):
    text = text.lower()

    if "open" in text:
        return "open"

    if "close" in text:
        return "close"

    if "time" in text:
        return "time"

    if "date" in text:
        return "date"

    return "unknown"