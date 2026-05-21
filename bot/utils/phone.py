import re

_DIGITS_RE = re.compile(r"\D+")


def normalize_phone(raw: str) -> str | None:
    """
    Привести телефон к виду +7XXXXXXXXXX (если 10–11 цифр и похоже на российский номер)
    или +<digits> для международных. Возвращает None, если номер невалиден.
    """
    if not raw:
        return None
    digits = _DIGITS_RE.sub("", raw)
    if not digits:
        return None
    if len(digits) == 11 and digits[0] in ("7", "8"):
        return "+7" + digits[1:]
    if len(digits) == 10:
        return "+7" + digits
    if 10 <= len(digits) <= 15:
        return "+" + digits
    return None


def mask_phone(phone: str) -> str:
    """+79858885886 → +7 *** *** *5886"""
    if not phone or len(phone) < 5:
        return phone or ""
    return phone[:2] + " *** *** *" + phone[-4:]
